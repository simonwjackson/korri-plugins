import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import {
  accessSync,
  constants,
  mkdtempSync,
  readFileSync,
  rmSync,
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
} from "../plugins/fable-ii-recomp/plugin"

const [packagePath, hostCli, korridCli, probe] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && probe)
const manifest = JSON.parse(
  readFileSync(join(packagePath, "manifest.json"), "utf8"),
)
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["game-files.json", "plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["fable_ii"])
assert.deepEqual(Object.keys(manifest.files), ["fable_ii"])
assert.equal(
  manifest.files.fable_ii,
  join(manifest.packages.fable_ii, "bin/fable_ii"),
)
accessSync(manifest.files.fable_ii, constants.X_OK)
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
assert.equal(name, "fable-ii-recomp")
assert.deepEqual(runners.fable_ii, {
  id: "@simonwjackson:fable-ii-recomp/fable_ii",
  program: "fable_ii",
  releases: [
    "sha256:2cdaafead95680e2c6fe8886a89f1ae3d5e41549857c7fc125a12aab1cb99ad9",
  ],
})
assert.deepEqual(systems, { "xbox-360": { id: "xbox-360", title: "Xbox 360" } })
assert.deepEqual(discovery.fileReleases["xbox-360-discs"], {
  id: "@simonwjackson:fable-ii-recomp/xbox-360-discs",
  title: "Xbox 360 disc images",
  extensions: ["iso"],
  system: "xbox-360",
  runners: [runners.fable_ii.id],
})
assert.deepEqual(Object.keys(handlers), ["launch.prepare"])
const admission = spawnSync(
  hostCli,
  ["seed", packagePath, "https://cache.example.invalid"],
  { encoding: "utf8" },
)
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, "@simonwjackson:fable-ii-recomp")
assert.equal(receipt.package, packagePath)
assert.deepEqual(receipt.desired, { state: "Enabled" })

const root = mkdtempSync(join(tmpdir(), "korri-fable2-check-"))
try {
  for (const account of ["first account", "second '; $(exit 19) # account"]) {
    const input: PluginLaunchInput = {
      runnerId: runners.fable_ii.id,
      program: probe,
      contentPath: "/library/Fable II '; $(exit 19) #.iso",
      accountRoot: join(root, account),
      files: manifest.files,
    }
    const directory = join(input.accountRoot, "fable_ii")
    assert.deepEqual(handlers["launch.prepare"](input), {
      command: probe,
      args: [input.contentPath],
      cwd: directory,
      directories: [directory],
      env: {},
      envUnset: [],
    })
    const launch = spawnSync(
      korridCli,
      ["plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(input)],
      { encoding: "utf8" },
    )
    assert.equal(launch.status, 0, launch.stderr)
    assert.equal(launch.stdout, `${directory}\n${input.contentPath}\n`)
    for (const refused of [
      { ...input, corePath: "/unwanted/core.so" },
      { ...input, overrides: { settings: {}, config: { append: "ignored" } } },
      { ...input, overrides: { settings: { unsupported: true } } },
    ] satisfies PluginLaunchInput[]) {
      assert.throws(() => handlers["launch.prepare"](refused))
      const result = spawnSync(
        korridCli,
        [
          "plugin-launch",
          join(packagePath, "plugin.ts"),
          JSON.stringify(refused),
        ],
        { encoding: "utf8" },
      )
      assert.notEqual(result.status, 0)
    }
  }
} finally {
  rmSync(root, { recursive: true, force: true })
}
console.log(
  "Fable II package, admission, account isolation and sandboxed callback checks passed",
)
