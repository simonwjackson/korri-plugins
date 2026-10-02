import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import {
  accessSync,
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
import type { PluginLaunchInput } from "../contracts/generated/korrid"

const [packagePath, name, program, machine, hostCli, korridCli, pwd] =
  process.argv.slice(2)
assert(packagePath && name && program && machine && hostCli && korridCli && pwd)
const plugin = await import(join(packagePath, "plugin.ts"))
const expectedHash = name === "fallout1-ce"
  ? "sha256:8cdb879ac4431dce48a25c3e02e9db4aee3449b73e7b185a63d69fef3982a509"
  : "sha256:bf349305c3749ce6501c1e3618689d3ccbecd732569d486183786a227fc79703"
assert(["fallout1-ce", "fallout2-ce"].includes(name))
const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.deepEqual(Object.keys(manifest.packages), [program])
assert.deepEqual(manifest.files, {
  [program]: join(manifest.packages[program], "libexec", program),
})
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
accessSync(manifest.files[program], constants.X_OK)
const executable = readFileSync(manifest.files[program])
assert.equal(executable.subarray(0, 4).toString("hex"), "7f454c46")
assert.equal(executable[4], 2, "64-bit ELF")
assert.equal(executable[5], 1, "little-endian ELF")
assert.equal(executable.readUInt16LE(18), Number(machine), "actual native architecture")
const doc = join(manifest.packages[program], "share/doc", program)
assert.match(readFileSync(join(doc, "LICENSE.md"), "utf8"), /Sustainable Use License/)
assert.match(readFileSync(join(doc, "NOTICE"), "utf8"), /modified by the pinned nixpkgs/)
assert.equal(plugin.name, name)
assert.deepEqual(plugin.runners, {
  [program]: {
    id: `@simonwjackson:${name}/${program}`,
    program,
    releases: [expectedHash],
  },
})
// No extension guess, platform invention, or claim that any DAT file is Fallout.
assert.equal(plugin.discovery, undefined)
assert.equal(plugin.systems, undefined)
assert.deepEqual(Object.keys(plugin.handlers), ["launch.prepare"])

const admission = spawnSync(hostCli, ["seed", packagePath, "https://cache.example.invalid"], {
  encoding: "utf8",
})
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, `@simonwjackson:${name}`)
assert.equal(receipt.package, packagePath)
assert.deepEqual(receipt.desired, { state: "Enabled" })

const root = mkdtempSync(join(tmpdir(), "fallout-plugin-check-"))
try {
  for (const directory of ["Fallout installed", "Fallout '; $(exit 19) #"]) {
    const cwd = join(root, directory)
    mkdirSync(cwd)
    writeFileSync(join(cwd, "user-config"), "retain user settings")
    for (const filename of ["MASTER.DAT", "master.dat"]) {
      const input: PluginLaunchInput = {
        runnerId: plugin.runners[program].id,
        program: pwd,
        contentPath: join(cwd, filename),
        accountRoot: join(root, "must-not-be-created"),
        files: manifest.files,
      }
      assert.deepEqual(plugin.handlers["launch.prepare"](input), {
        command: pwd,
        args: [],
        cwd,
      })
      const launch = spawnSync(korridCli, [
        "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(input),
      ], { encoding: "utf8" })
      assert.equal(launch.status, 0, launch.stderr)
      assert.equal(launch.stdout.trimEnd(), cwd)
      assert.deepEqual(readdirSync(cwd), ["user-config"])
      assert.equal(readFileSync(join(cwd, "user-config"), "utf8"), "retain user settings")
      for (const change of [
        { runnerId: "@other:game/runner" },
        { corePath: "/core.so" },
        { overrides: { config: { prepend: "native config" } } },
        { overrides: { settings: { invented: true } } },
        { contentPath: "relative/MASTER.DAT" },
        { contentPath: join(cwd, "CRITTER.DAT") },
        { contentPath: join(cwd, "game.zip") },
        { contentPath: join(cwd, "") },
      ]) {
        assert.throws(() => plugin.handlers["launch.prepare"]({ ...input, ...change }))
        const rejected = spawnSync(korridCli, [
          "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify({ ...input, ...change }),
        ], { encoding: "utf8" })
        assert.notEqual(rejected.status, 0, "sandbox must reject unsupported input")
      }
    }
  }
  assert.deepEqual(readdirSync(root).sort(), ["Fallout '; $(exit 19) #", "Fallout installed"])
} finally {
  rmSync(root, { recursive: true, force: true })
}
console.log(`${name}: package, license, ELF, contract, admission and sandboxed cwd checks passed`)
