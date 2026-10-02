import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { existsSync, readFileSync } from "node:fs"
import { join } from "node:path"
import type { PluginLaunchInput } from "../contracts/generated/korrid"

const [packagePath, hostCli, korridCli, argvProgram] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && argvProgram)
const plugin = await import(join(packagePath, "plugin.ts"))
const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.deepEqual(Object.keys(manifest.packages), ["opengoal"])
assert.deepEqual(manifest.files, { opengoal: join(manifest.packages.opengoal, "bin/gk") })
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
assert.equal(plugin.name, "opengoal")
assert.equal(plugin.discovery, undefined, "Do not claim unrelated ISO or CGO files")
assert.equal(plugin.systems, undefined, "No invented prepared-game system")
assert.deepEqual(Object.keys(plugin.runners), ["jak1", "jak2", "jak3"])
const hashes = [
  ["sha256:3cda4bc7f551a51d2fa9c4d5949549237ea846ce4851437403dbe91548a52807"],
  ["sha256:6a673c9cf1e7aee115e82be459b1348fd1981fef49086569aae67a2a64c4cc14", "sha256:a8c829303340a1c572252e408f0730e2495d84505cdfcd94b3e34167fd9a6ad8"],
  ["sha256:442becdbf74aa11fe046e76c243b7ce0122d924593f6e20682ff06ae5dacd4f5"],
]
const elf = readFileSync(manifest.files.opengoal)
assert.equal(elf.subarray(0, 4).toString("hex"), "7f454c46")
assert.equal(elf.readUInt16LE(18), 62, "x86_64 runtime")
for (const path of ["bin/extractor", "bin/goalc", "share/opengoal/data/goal_src"]) {
  assert.equal(existsSync(join(manifest.packages.opengoal, path)), false)
}
assert.match(readFileSync(join(manifest.packages.opengoal, "share/licenses/opengoal/LICENSE"), "utf8"), /ISC License/)
const version = spawnSync(manifest.files.opengoal, ["--version"], { encoding: "utf8" })
assert.equal(version.status, 0, version.stderr)
assert.match(version.stdout, /v0\.3\.8/)
const admission = spawnSync(hostCli, ["seed", packagePath, "https://cache.example.invalid"], { encoding: "utf8" })
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, "@simonwjackson:opengoal")
assert.deepEqual(receipt.desired, { state: "Enabled" })

for (const [index, game] of ["jak1", "jak2", "jak3"].entries()) {
  assert.deepEqual(plugin.runners[game], {
    id: `@simonwjackson:opengoal/${game}`, program: "opengoal", releases: hashes[index],
  })
  for (const data of ["/prepared data", "/game ' ; $(exit 19) 日本語", "/another location"]) {
    const input: PluginLaunchInput = {
      runnerId: plugin.runners[game].id,
      program: argvProgram,
      contentPath: `${data}/out/${game}/iso/GAME.CGO`,
      accountRoot: "/unused-account-root",
      files: manifest.files,
    }
    const args = ["--game", game, "--proj-path", data]
    assert.deepEqual(plugin.handlers["launch.prepare"](input), { command: argvProgram, args })
    const launched = spawnSync(korridCli, ["plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(input)], { encoding: "utf8" })
    assert.equal(launched.status, 0, launched.stderr)
    assert.deepEqual(launched.stdout.split("\0").slice(0, -1), args)
    for (const change of [
      { runnerId: "@other:plugin/jak1" },
      { corePath: "/core.so" },
      { overrides: { config: { prepend: "unsafe" } } },
      { overrides: { settings: { invented: true } } },
      { contentPath: "relative/out/jak1/iso/GAME.CGO" },
      { contentPath: `${data}/game.iso` },
      { contentPath: `${data}/out/${game}/iso/KERNEL.CGO` },
      { contentPath: `${data}/../out/${game}/iso/GAME.CGO` },
      { contentPath: `${data}/out/${game === "jak1" ? "jak2" : "jak1"}/iso/GAME.CGO` },
    ]) {
      const rejected = spawnSync(korridCli, ["plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify({ ...input, ...change })], { encoding: "utf8" })
      assert.notEqual(rejected.status, 0, "The actual sandbox must reject unsupported inputs")
    }
  }
}
console.log("OpenGOAL: packaged native runtime, measured releases, admission and sandboxed argv verified")
