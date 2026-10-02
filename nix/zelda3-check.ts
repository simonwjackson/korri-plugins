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
} from "../plugins/zelda3/plugin"

const [packagePath, hostCli, korridCli, recordArguments] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && recordArguments)

const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["zelda3"])
assert.deepEqual(manifest.files, {
  zelda3: join(manifest.packages.zelda3, "bin/zelda3"),
})
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
accessSync(manifest.files.zelda3, constants.X_OK)
assert.equal(name, "zelda3")
assert.deepEqual(systems, { snes: { id: "snes", title: "Super Nintendo" } })
assert.deepEqual(Object.keys(runners), ["zelda3"])
assert.equal(runners.zelda3.id, "@simonwjackson:zelda3/zelda3")
assert.equal(runners.zelda3.program, "zelda3")
assert(!("systems" in runners.zelda3))
assert.deepEqual(runners.zelda3.releases, [
  "sha256:66871d66be19ad2c34c927d6b14cd8eb6fc3181965b6e517cb361f7316009cfb",
])
assert.deepEqual(discovery.fileReleases["snes-files"], {
  id: "@simonwjackson:zelda3/snes-files",
  title: "Super Nintendo files",
  extensions: ["sfc", "smc"],
  system: "snes",
  runners: [runners.zelda3.id],
})
assert.deepEqual(Object.keys(handlers), ["launch.prepare"])

const admission = spawnSync(hostCli, [
  "seed", packagePath, "https://cache.example.invalid",
], { encoding: "utf8" })
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, "@simonwjackson:zelda3")
assert.equal(receipt.package, packagePath)
assert.deepEqual(receipt.desired, { state: "Enabled" })
assert.equal(receipt.previous, null)

for (const contentPath of [
  "/library/Legend of Zelda, The - A Link to the Past (USA).sfc",
  "/library/Zelda %s '; $(exit 19) #.smc",
]) {
  const input: PluginLaunchInput = {
    runnerId: runners.zelda3.id,
    program: recordArguments,
    contentPath,
    accountRoot: "/accounts/Player One '; $(exit 21)",
    files: manifest.files,
  }
  const args = ["--", contentPath, `${input.accountRoot}/zelda3`]
  assert.deepEqual(handlers["launch.prepare"](input), {
    command: recordArguments, args, env: {},
  })
  // Exercise the production sandbox and launch executor with a real argv
  // recording program. No game effects or trust changes run in this check.
  const launch = spawnSync(korridCli, [
    "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(input),
  ], { encoding: "utf8" })
  assert.equal(launch.status, 0, launch.stderr)
  assert.equal(launch.stdout, `${args.join("\0")}\0`)

  for (const unsupported of [
    { corePath: "/core.so" },
    { overrides: { config: { replace: "ignore me" } } },
    { overrides: { settings: { unimplemented: true } } },
  ]) {
    const invalid = { ...input, ...unsupported }
    assert.throws(() => handlers["launch.prepare"](invalid))
    const rejected = spawnSync(korridCli, [
      "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(invalid),
    ], { encoding: "utf8" })
    assert.notEqual(rejected.status, 0)
    assert.equal(rejected.stdout, "")
  }
}
console.log("Zelda3 package, contract, admission and sandboxed launch checks passed")
