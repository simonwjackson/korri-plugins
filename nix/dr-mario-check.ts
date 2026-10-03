import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { accessSync, constants, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import process from "node:process"
import type { PluginLaunchInput } from "../contracts/generated/korrid"
import { discovery, handlers, name, runners, systems } from "../plugins/dr-mario/plugin"

const [packagePath, hostCli, korridCli, probe] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && probe)
const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["dr-mario"])
assert.deepEqual(manifest.files, { "dr-mario": join(manifest.packages["dr-mario"], "bin/dr-mario") })
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
accessSync(manifest.files["dr-mario"], constants.X_OK)
assert.equal(name, "dr-mario")
assert.deepEqual(systems, { nes: { id: "nes", title: "Nintendo Entertainment System" } })
assert.deepEqual(runners, {
  "dr-mario": {
    id: "@simonwjackson:dr-mario/dr-mario",
    program: "dr-mario",
    releases: ["sha256:83914c08f82fc70779121760a48392af3a5988f015794eb53cbe1aa0a165c821"],
  },
})
assert.deepEqual(discovery.fileReleases["nes-files"], {
  id: "@simonwjackson:dr-mario/nes-files",
  title: "Nintendo Entertainment System files",
  extensions: ["nes"],
  system: "nes",
  runners: [runners["dr-mario"].id],
})
assert.deepEqual(Object.keys(handlers), ["launch.prepare"])

const admission = spawnSync(hostCli, ["seed", packagePath, "https://cache.example.invalid"], { encoding: "utf8" })
assert.equal(admission.status, 0, admission.stderr)
assert.equal(JSON.parse(admission.stdout).id, "@simonwjackson:dr-mario")

const temporary = mkdtempSync(join(tmpdir(), "dr-mario-check-"))
try {
  for (const account of ["Player One", "Player Two %s '; $(exit 91) `exit 92` #"]) {
    const input: PluginLaunchInput = {
      runnerId: runners["dr-mario"].id,
      program: probe,
      contentPath: "/library/Dr. Mario %s '; $(exit 93) `exit 94` #.nes",
      accountRoot: join(temporary, account),
      files: manifest.files,
    }
    const directory = `${input.accountRoot}/DrMarioRecomp`
    const expected = {
      command: probe, args: [input.contentPath], cwd: directory,
      directories: [directory], env: {}, envUnset: [],
    }
    for (const valid of [input, { ...input, overrides: {} }, { ...input, overrides: { settings: {} } }]) {
      assert.deepEqual(handlers["launch.prepare"](valid), expected)
      const result = spawnSync(korridCli, ["plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(valid)], { encoding: "utf8" })
      assert.equal(result.status, 0, result.stderr)
      assert.equal(result.stdout, `${directory}\n${input.contentPath}\n`)
      assert.deepEqual(readdirSync(directory), [])
    }
    for (const invalid of [
      { ...input, corePath: "" },
      { ...input, corePath: "/core.so" },
      { ...input, overrides: { config: {} } },
      { ...input, overrides: { config: { append: "ignored" } } },
      { ...input, overrides: { settings: { fullscreen: true } } },
    ]) {
      assert.throws(() => handlers["launch.prepare"](invalid))
      const result = spawnSync(korridCli, ["plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(invalid)], { encoding: "utf8" })
      assert.notEqual(result.status, 0)
      assert.equal(result.stdout, "")
    }
    // Exercise the packaged launcher through the production callback/executor,
    // without redistributing a ROM or treating a mock as the game runtime.
    const badRom = join(temporary, "unsupported %.nes")
    for (const bytes of [Buffer.alloc(0), Buffer.from("NES\u001a"), Buffer.alloc(65552), Buffer.alloc(65553)]) {
      writeFileSync(badRom, bytes)
      const result = spawnSync(korridCli, ["plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify({
        ...input, contentPath: badRom, program: manifest.files["dr-mario"],
      })], { encoding: "utf8" })
      assert.notEqual(result.status, 0)
      assert.match(result.stderr, /requires the supported Europe iNES ROM/)
      assert.deepEqual(readFileSync(badRom), bytes)
      assert.deepEqual(readdirSync(directory), [])
    }
  }
} finally {
  rmSync(temporary, { recursive: true, force: true })
}
console.log("Dr. Mario package, contract, host admission, account cwd and unsupported-ROM checks passed")
