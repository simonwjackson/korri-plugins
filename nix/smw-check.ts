import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import {
  accessSync,
  chmodSync,
  constants,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import process from "node:process"
import type { PluginLaunchInput } from "../contracts/generated/korrid"
import {
  discovery,
  handlers,
  name,
  runners,
  systems,
} from "../plugins/super-mario-world/plugin"

const [packagePath, hostCli, korridCli, probe] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && probe)
const manifest = JSON.parse(
  readFileSync(join(packagePath, "manifest.json"), "utf8"),
)
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["smw"])
assert.deepEqual(Object.keys(manifest.files), ["smw"])
assert.equal(manifest.files.smw, join(manifest.packages.smw, "bin/smw"))
accessSync(manifest.files.smw, constants.X_OK)
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
assert.equal(name, "super-mario-world")
assert.equal(runners.smw.id, "@simonwjackson:super-mario-world/smw")
assert.equal(runners.smw.program, "smw")
assert(!("systems" in runners.smw))
assert.deepEqual(runners.smw.releases, [
  "sha256:d70c9c7716ad12c674fc7dd744736aa48d4d7b4237f58066be620fda26024872",
  "sha256:0838e531fe22c077528febe14cb3ff7c492f1f5fa8de354192bdff7137c27f5b",
])
assert.deepEqual(systems.snes, { id: "snes", title: "Super Nintendo" })
assert.deepEqual(discovery.fileReleases["snes-files"], {
  id: "@simonwjackson:super-mario-world/snes-files",
  title: "Super Nintendo files",
  extensions: ["smc", "sfc"],
  system: "snes",
  runners: [runners.smw.id],
})
assert.deepEqual(Object.keys(handlers), ["launch.prepare"])

const admission = spawnSync(
  hostCli,
  ["seed", packagePath, "https://cache.example.invalid"],
  { encoding: "utf8" },
)
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, "@simonwjackson:super-mario-world")
assert.equal(receipt.package, packagePath)
assert.deepEqual(receipt.desired, { state: "Enabled" })

const root = mkdtempSync(join(tmpdir(), "korri-smw-check-"))
try {
  const input: PluginLaunchInput = {
    runnerId: runners.smw.id,
    program: probe,
    contentPath: "/library/Super Mario World (U) [!].smc",
    accountRoot: join(root, "account '; $(exit 19) #"),
    files: manifest.files,
  }
  const directory = join(input.accountRoot, "smw")
  const prepare = handlers["launch.prepare"]
  assert.deepEqual(prepare(input), {
    command: probe,
    args: [input.contentPath],
    cwd: directory,
    directories: [directory],
    env: {},
    envUnset: [],
  })
  for (const contentPath of [
    input.contentPath,
    "/library/SMW '; $(exit 19) #.sfc",
  ]) {
    // Exercise the packaged callback through Core's real sandbox and executor.
    const launch = spawnSync(
      korridCli,
      [
        "plugin-launch",
        join(packagePath, "plugin.ts"),
        JSON.stringify({ ...input, contentPath }),
      ],
      { encoding: "utf8" },
    )
    assert.equal(launch.status, 0, launch.stderr)
    assert.equal(launch.stdout, `${directory}\n${contentPath}\n`)
  }
  const refusals: PluginLaunchInput[] = [
    { ...input, corePath: "/unwanted/core.so" },
    { ...input, overrides: { settings: {}, config: { append: "ignored" } } },
    { ...input, overrides: { settings: { unsupported: true } } },
  ]
  for (const refused of refusals) {
    assert.throws(() => prepare(refused))
    const launch = spawnSync(
      korridCli,
      [
        "plugin-launch",
        join(packagePath, "plugin.ts"),
        JSON.stringify(refused),
      ],
      { encoding: "utf8" },
    )
    assert.notEqual(launch.status, 0)
  }

  // Real launcher failures must not overwrite prior config, assets or saves.
  writeFileSync(join(directory, "smw.ini"), "user configuration\n")
  writeFileSync(join(directory, "smw_assets.dat"), "previous assets")
  mkdirSync(join(directory, "saves"))
  writeFileSync(join(directory, "saves", "save0.sav"), "previous save")
  const invalid = join(root, "wrong ROM '; $(exit 19) #.smc")
  for (const size of [0, 524288, 524800, 524801]) {
    writeFileSync(invalid, Buffer.alloc(size))
    chmodSync(invalid, 0o444)
    const rejected = spawnSync(manifest.files.smw, [invalid], {
      cwd: directory,
      encoding: "utf8",
    })
    assert.equal(rejected.status, 1, rejected.stderr)
    assert(rejected.stderr.includes("SMW launch failed:"))
    assert.equal(readFileSync(invalid).length, size)
    assert.equal(
      readFileSync(join(directory, "smw.ini"), "utf8"),
      "user configuration\n",
    )
    assert.equal(
      readFileSync(join(directory, "smw_assets.dat"), "utf8"),
      "previous assets",
    )
    assert.equal(
      readFileSync(join(directory, "saves", "save0.sav"), "utf8"),
      "previous save",
    )
    assert.deepEqual(readdirSync(directory).sort(), [
      "saves",
      "smw.ini",
      "smw_assets.dat",
    ])
    chmodSync(invalid, 0o644)
  }
  const missing = spawnSync(manifest.files.smw, [join(root, "missing.sfc")], {
    cwd: directory,
    encoding: "utf8",
  })
  assert.equal(missing.status, 1)
  assert(missing.stderr.includes("SMW launch failed:"))
} finally {
  rmSync(root, { recursive: true, force: true })
}
console.log(
  "SMW package, admission, sandboxed launch and invalid-ROM preservation checks passed",
)
