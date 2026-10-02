import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { accessSync, constants, readFileSync } from "node:fs"
import { join } from "node:path"
import process from "node:process"
import type { PluginLaunchInput } from "../contracts/generated/korrid"
import {
  discovery,
  handlers,
  name,
  runners,
  systems,
} from "../plugins/actraiser/plugin"

const [packagePath, hostCli, korridCli, recordArguments] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && recordArguments)

const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["actraiser"])
assert.deepEqual(manifest.files, {
  actraiser: join(manifest.packages.actraiser, "bin/actraiser"),
})
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
accessSync(manifest.files.actraiser, constants.X_OK)
assert.equal(name, "actraiser")
assert.deepEqual(systems, { snes: { id: "snes", title: "Super Nintendo" } })
assert.deepEqual(Object.keys(runners), ["actraiser"])
assert.equal(runners.actraiser.id, "@simonwjackson:actraiser/actraiser")
assert.equal(runners.actraiser.program, "actraiser")
assert(!("systems" in runners.actraiser))
assert.deepEqual(runners.actraiser.releases, [
  "sha256:b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0",
])
assert.deepEqual(discovery.fileReleases["snes-files"], {
  id: "@simonwjackson:actraiser/snes-files",
  title: "Super Nintendo files",
  extensions: ["sfc", "smc"],
  system: "snes",
  runners: [runners.actraiser.id],
})
assert.deepEqual(Object.keys(handlers), ["launch.prepare"])

// Seed checks admission only. It does not install the plugin or grant trust.
const admission = spawnSync(hostCli, [
  "seed", packagePath, "https://cache.example.invalid",
], { encoding: "utf8" })
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, "@simonwjackson:actraiser")
assert.equal(receipt.package, packagePath)
assert.deepEqual(receipt.desired, { state: "Enabled" })
assert.equal(receipt.previous, null)

for (const contentPath of [
  "/library/ActRaiser (USA).sfc",
  "/library/ActRaiser %s '; $(exit 19) `exit 20` #.smc",
]) {
  const input: PluginLaunchInput = {
    runnerId: runners.actraiser.id,
    program: recordArguments,
    contentPath,
    accountRoot: "/accounts/Player One %s '; $(exit 21) `exit 22` #",
    files: manifest.files,
  }
  const args = ["--", contentPath]
  const userDataDirectory = `${input.accountRoot}/ActRaiserRecomp/game`
  const expected = {
    command: recordArguments,
    args,
    env: { AR_USER_DATA_DIR: userDataDirectory },
  }
  const accepted: PluginLaunchInput[] = [
    input,
    { ...input, overrides: {} },
    { ...input, overrides: { settings: {} } },
  ]
  for (const valid of accepted) {
    assert.deepEqual(handlers["launch.prepare"](valid), expected)
    // Run Core's production sandbox and executor with a real recording program.
    // This tests argv/env transport, not the private native game or its launcher.
    // No ROM is opened and no game data or account directory is created.
    const launch = spawnSync(korridCli, [
      "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(valid),
    ], {
      encoding: "utf8",
      env: { ...process.env, AR_USER_DATA_DIR: "/must-be-replaced" },
    })
    assert.equal(launch.status, 0, launch.stderr)
    assert.equal(
      launch.stdout,
      `${args.join("\0")}\0AR_USER_DATA_DIR=${userDataDirectory}\0`,
    )
  }

  const rejectedInputs: PluginLaunchInput[] = [
    { ...input, corePath: "/core.so" },
    { ...input, corePath: "" },
    { ...input, overrides: { config: {} } },
    { ...input, overrides: { config: { replace: "ignore me" } } },
    { ...input, overrides: { config: { prepend: "ignore me" } } },
    { ...input, overrides: { config: { append: "ignore me" } } },
    { ...input, overrides: { settings: { unimplemented: true } } },
  ]
  for (const invalid of rejectedInputs) {
    assert.throws(() => handlers["launch.prepare"](invalid))
    const rejected = spawnSync(korridCli, [
      "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(invalid),
    ], { encoding: "utf8" })
    assert.notEqual(rejected.status, 0)
    assert.equal(rejected.stdout, "")
  }
}
console.log("ActRaiser package, contract, admission and sandboxed argv/env checks passed (no native runtime verification)")
