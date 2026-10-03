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
import process from "node:process"
import type { PluginLaunchInput } from "../contracts/generated/korrid"
import {
  discovery,
  handlers,
  name,
  runners,
  systems,
} from "../plugins/drmario64/plugin"

const [packagePath, hostCli, korridCli, probe, engine] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && probe && engine)
const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["drmario64"])
assert.deepEqual(Object.keys(manifest.files), ["drmario64"])
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
assert.equal(manifest.files.drmario64, join(manifest.packages.drmario64, "bin/drmario64"))
accessSync(manifest.files.drmario64, constants.X_OK)
assert.equal(name, "drmario64")
assert.deepEqual(Object.keys(runners), ["drmario64"])
assert.equal(runners.drmario64.id, "@simonwjackson:drmario64/drmario64")
assert.equal(runners.drmario64.program, "drmario64")
assert(!("systems" in runners.drmario64))
assert.deepEqual(runners.drmario64.releases, [
  "sha256:613778b244784492a881c0d72d6017f82c39026706a406bd7ef95c6f33e53b89",
  "sha256:bb2c0dec0a8287ad256929563d0509801c2f239df883c1cf52cab05b23bd77b6",
])
assert.deepEqual(systems, { n64: { id: "n64", title: "Nintendo 64" } })
assert.deepEqual(discovery.fileReleases["n64-roms"], {
  id: "@simonwjackson:drmario64/n64-roms",
  title: "Nintendo 64 ROMs",
  extensions: ["n64", "z64", "v64"],
  system: "n64",
  runners: [runners.drmario64.id],
})
assert.deepEqual(Object.keys(handlers), ["launch.prepare"])
const admitted = spawnSync(hostCli, ["seed", packagePath, "https://cache.example.invalid"], {
  encoding: "utf8",
})
assert.equal(admitted.status, 0, admitted.stderr)
const receipt = JSON.parse(admitted.stdout)
assert.equal(receipt.id, "@simonwjackson:drmario64")
assert.equal(receipt.package, packagePath)
assert.deepEqual(receipt.desired, { state: "Enabled" })
assert.equal(receipt.previous, null)

const root = mkdtempSync(join(tmpdir(), "korri-drmario64-contract-"))
try {
  for (const filename of ["Dr. Mario 64 (USA).n64", "ROM '; $(exit 19) #.z64"]) {
    const account = join(root, `Account ${filename}`)
    const directory = join(account, "drmario64.us")
    const input: PluginLaunchInput = {
      runnerId: runners.drmario64.id,
      program: probe,
      contentPath: join(root, filename),
      accountRoot: account,
      files: manifest.files,
    }
    assert.deepEqual(handlers["launch.prepare"](input), {
      command: probe,
      args: [input.contentPath],
      cwd: directory,
      directories: [directory],
      env: { APP_FOLDER_PATH: directory },
    })
    const command = () => ["plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(input)]
    const launch = spawnSync(korridCli, command(), { encoding: "utf8" })
    assert.equal(launch.status, 0, launch.stderr)
    assert.equal(launch.stdout, `${directory}\n${directory}\n${input.contentPath}\n`)

    mkdirSync(join(directory, "saves"))
    const preserved = ["general.json", "graphics.json", "saves/drmario64.us.bin", "drmario64.us.z64"]
    for (const file of preserved) writeFileSync(join(directory, file), `unchanged:${file}`)
    input.program = manifest.files.drmario64
    for (const bytes of [Buffer.from("not a ROM"), Buffer.alloc(4 * 1024 * 1024)]) {
      writeFileSync(input.contentPath, bytes)
      const failure = spawnSync(korridCli, command(), { encoding: "utf8", timeout: 10000 })
      assert.equal(failure.status, 1, failure.stderr)
      assert.match(failure.stderr, /Dr\. Mario 64 launch failed:/)
      for (const file of preserved) {
        assert.equal(readFileSync(join(directory, file), "utf8"), `unchanged:${file}`)
      }
      assert.deepEqual(readFileSync(input.contentPath), bytes)
      assert(!readdirSync(directory).some((entry) => entry.startsWith(".drmario64-")))
    }
    for (const unsupported of [
      { corePath: "/unneeded/core.so" },
      { overrides: { config: { replace: "unimplemented" } } },
      { overrides: { settings: { fullscreen: "true" } } },
    ]) {
      assert.throws(() => handlers["launch.prepare"]({ ...input, ...unsupported }))
      const failure = spawnSync(korridCli, [
        "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify({ ...input, ...unsupported }),
      ], { encoding: "utf8" })
      assert.notEqual(failure.status, 0)
    }
  }
  const usage = spawnSync(manifest.files.drmario64, [], { encoding: "utf8" })
  assert.equal(usage.status, 2, usage.stderr)
  assert.match(usage.stderr, /Usage: drmario64/)
  const nativeHelp = spawnSync(engine, ["--help"], { encoding: "utf8", timeout: 10000 })
  assert.equal(nativeHelp.status, 0, nativeHelp.stderr)
  assert.match(nativeHelp.stdout, /Usage: drmario64_recomp \[--start\]/)
  const nativeInvalid = spawnSync(engine, ["--not-an-option"], { encoding: "utf8", timeout: 10000 })
  assert.equal(nativeInvalid.status, 2, nativeInvalid.stderr)
} finally {
  rmSync(root, { recursive: true, force: true })
}
console.log("Dr. Mario 64 package, admission, launch contract and invalid-ROM preservation passed")
