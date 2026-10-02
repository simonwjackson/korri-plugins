import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { accessSync, constants, readFileSync } from "node:fs"
import { join } from "node:path"
import process from "node:process"
import type { PluginLaunchInput } from "../contracts/generated/korrid"
import * as plugin from "../plugins/melee-pc/plugin"

const [packagePath, hostCli, korridCli, recordArguments] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && recordArguments)
const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["melee-pc"])
assert.deepEqual(manifest.files, { "melee-pc": join(manifest.packages["melee-pc"], "bin/melee-pc") })
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
accessSync(manifest.files["melee-pc"], constants.X_OK)
assert.equal(plugin.name, "melee-pc")
assert.equal("systems" in plugin, false)
assert.equal("discovery" in plugin, false)
assert.deepEqual(plugin.runners, {
  "melee-pc": {
    id: "@simonwjackson:melee-pc/melee-pc",
    program: "melee-pc",
    releases: ["sha256:0de05981a34156b9cedcef73c73d4244ac05cf6149ab3c9cfed917698819e464"],
  },
})

const admission = spawnSync(hostCli, ["seed", packagePath, "https://cache.example.invalid"], { encoding: "utf8" })
assert.equal(admission.status, 0, admission.stderr)
assert.equal(JSON.parse(admission.stdout).id, "@simonwjackson:melee-pc")

for (const contentPath of [
  "/library/Super Smash Bros. Melee (USA) (v1.02).iso",
  "/library/Melee '; $(exit 19) %s #.iso",
]) {
  const input: PluginLaunchInput = {
    runnerId: plugin.runners["melee-pc"].id,
    program: recordArguments,
    contentPath,
    accountRoot: "/accounts/Player One '; $(exit 21)",
    files: manifest.files,
  }
  const args = ["--", contentPath, input.accountRoot]
  assert.deepEqual(plugin.handlers["launch.prepare"](input), { command: recordArguments, args, env: {} })
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
    assert.throws(() => plugin.handlers["launch.prepare"](invalid))
    const rejected = spawnSync(korridCli, [
      "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(invalid),
    ], { encoding: "utf8" })
    assert.notEqual(rejected.status, 0)
    assert.equal(rejected.stdout, "")
  }
}
console.log("Melee PC package, contract, admission and sandboxed launch checks passed")
