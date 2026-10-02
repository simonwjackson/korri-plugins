import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { accessSync, constants, readFileSync } from "node:fs"
import { join } from "node:path"
import process from "node:process"
import type { PluginLaunchInput } from "../contracts/generated/korrid"
import { discovery, handlers, name, runners, systems } from "../plugins/nocturne/plugin"

const [packagePath, hostCli, korridCli, recordArguments] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && recordArguments)
const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["nocturne"])
assert.deepEqual(manifest.files, { nocturne: join(manifest.packages.nocturne, "bin/nocturne") })
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
accessSync(manifest.files.nocturne, constants.X_OK)
assert.equal(name, "nocturne")
assert.deepEqual(systems, { "xbox-360": { id: "xbox-360", title: "Xbox 360" } })
assert.equal(runners.nocturne.id, "@simonwjackson:nocturne/nocturne")
assert.equal(runners.nocturne.program, "nocturne")
assert.deepEqual(runners.nocturne.releases, [
  "sha256:26a58b074c5dd6185b77a8111a0012866d11cba674b4b0810d79dbf07ad68aa6",
])
assert.deepEqual(discovery.fileReleases["xbox-360-executables"], {
  id: "@simonwjackson:nocturne/xbox-360-executables",
  title: "Xbox 360 executables",
  extensions: ["xex"],
  system: "xbox-360",
  runners: [runners.nocturne.id],
})

const admission = spawnSync(hostCli, ["seed", packagePath, "https://cache.example.invalid"], { encoding: "utf8" })
assert.equal(admission.status, 0, admission.stderr)
assert.equal(JSON.parse(admission.stdout).id, "@simonwjackson:nocturne")

for (const contentPath of [
  "/library/Castlevania (World)/assets/default.xex",
  "/library/Castlevania '; $(exit 19) %s #/default.xex",
]) {
  const input: PluginLaunchInput = {
    runnerId: runners.nocturne.id,
    program: recordArguments,
    contentPath,
    accountRoot: "/accounts/Player One '; $(exit 21)",
    files: manifest.files,
  }
  const args = ["--", contentPath, `${input.accountRoot}/nocturnerecomp`]
  assert.deepEqual(handlers["launch.prepare"](input), { command: recordArguments, args, env: {} })
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
console.log("Nocturne package, contract, admission and sandboxed launch checks passed")
