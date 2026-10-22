import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { accessSync, constants, mkdtempSync, readFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import process from "node:process"
import type { PluginLaunchInput } from "../contracts/generated/korrid"
import { handlers, runners } from "../plugins/mega-man-maker/plugin"

const [packagePath, hostCli, korridCli, probe] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && probe)
const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
// Proton is a foreign artifact, not a required package: no `requires`.
assert(!("requires" in manifest), JSON.stringify(manifest.requires))
assert(!("hosts" in manifest), JSON.stringify(manifest.hosts))
assert.deepEqual(Object.keys(manifest.packages).sort(), [
  "mega-man-maker-proton",
  "mega-man-maker-unpack",
])
assert.deepEqual(manifest.files, {
  "game-unpack": join(manifest.packages["mega-man-maker-unpack"], "bin/mega-man-maker-unpack"),
  "proton-launch": join(manifest.packages["mega-man-maker-proton"], "bin/mega-man-maker-proton"),
})
for (const file of Object.values(manifest.files) as string[]) accessSync(file, constants.X_OK)

// The unpack program refuses bad usage with status 1 and writes no stdout.
for (const args of [[], ["/nonexistent-work"], ["/nonexistent-work", "/nonexistent.zip"]]) {
  const result = spawnSync(manifest.files["game-unpack"], args, { encoding: "utf8" })
  assert.equal(result.status, 1, result.stderr)
  assert.equal(result.stdout, "")
}

const admission = spawnSync(hostCli, ["seed", packagePath, "https://cache.example.invalid"], {
  encoding: "utf8",
})
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, "@simonwjackson:mega-man-maker")
assert.equal(receipt.package, packagePath)

const root = mkdtempSync(join(tmpdir(), "korri-mega-man-maker-check-"))
try {
  const game = join(root, "cache/mega-man-maker/game/1.10.4.2 '; $(exit 19) #")
  const proton = join(root, "cache/proton/cachyos/11.0-20260601-slr-arm64")
  const input: PluginLaunchInput = {
    runnerId: runners.proton.id,
    program: probe,
    contentPath: join(game, "data.win"),
    accountRoot: join(root, "account '; $(exit 19) #"),
    cacheRoot: join(root, "cache"),
    files: manifest.files,
    artifacts: { "@korri:proton/cachyos": proton },
  }
  const home = join(input.accountRoot, "mega-man-maker")
  // Exercise the packaged callback through Core's real sandbox and executor.
  // The game directory need not exist for the probe; cwd does.
  const launch = spawnSync(
    korridCli,
    [
      "plugin-launch",
      join(packagePath, "plugin.ts"),
      JSON.stringify({ ...input, contentPath: join(root, "data.win") }),
      JSON.stringify({ modifiers: [] }),
    ],
    { encoding: "utf8" },
  )
  assert.equal(launch.status, 0, launch.stderr)
  assert.equal(launch.stdout, `${root}\n${home}\n${proton}\n${join(root, "data.win")}\n`)

  const prepare = handlers["launch.prepare"]
  const refusals: PluginLaunchInput[] = [
    { ...input, contentPath: undefined, ref: "123" },
    { ...input, corePath: "/unwanted/core.so" },
    { ...input, overrides: { settings: {}, config: { append: "ignored" } } },
    { ...input, overrides: { settings: { unsupported: true } } },
    { ...input, artifacts: {} },
  ]
  for (const refused of refusals) {
    assert.throws(() => prepare(refused))
    const result = spawnSync(
      korridCli,
      [
        "plugin-launch",
        join(packagePath, "plugin.ts"),
        JSON.stringify(refused),
        JSON.stringify({ modifiers: [] }),
      ],
      { encoding: "utf8" },
    )
    assert.notEqual(result.status, 0)
  }
} finally {
  rmSync(root, { recursive: true, force: true })
}
console.log("Mega Man Maker package, admission and sandboxed launch checks passed")
