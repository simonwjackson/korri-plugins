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
} from "../plugins/2ship/plugin"

const [packagePath, hostCli, korridCli, probe] = process.argv.slice(2)
assert(packagePath && hostCli && korridCli && probe)
const manifest = JSON.parse(
  readFileSync(join(packagePath, "manifest.json"), "utf8"),
)
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(Object.keys(manifest.packages), ["2ship"])
assert.deepEqual(Object.keys(manifest.files), ["2ship"])
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
assert.equal(
  manifest.files["2ship"],
  join(manifest.packages["2ship"], "bin/2ship"),
)
accessSync(manifest.files["2ship"], constants.X_OK)
assert.equal(name, "2ship")
assert.deepEqual(Object.keys(runners), ["2ship"])
assert.equal(runners["2ship"].id, "@simonwjackson:2ship/2ship")
assert.equal(runners["2ship"].program, "2ship")
assert(!("systems" in runners["2ship"]))
assert.deepEqual(runners["2ship"].releases, [
  "sha256:8dc31559174f958a938ab7eccb25dd310a4167f98cb68a521181f4653b684431",
  "sha256:efb1365b3ae362604514c0f9a1a2d11f5dc8688ba5be660a37debf5e3be43f2b",
])
assert.deepEqual(systems, { n64: { id: "n64", title: "Nintendo 64" } })
assert.deepEqual(discovery.fileReleases["n64-roms"], {
  id: "@simonwjackson:2ship/n64-roms",
  title: "Nintendo 64 ROMs",
  extensions: ["n64", "z64", "v64"],
  system: "n64",
  runners: [runners["2ship"].id],
})
assert.deepEqual(Object.keys(handlers), ["launch.prepare"])
const admission = spawnSync(
  hostCli,
  ["seed", packagePath, "https://cache.example.invalid"],
  {
    encoding: "utf8",
  },
)
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, "@simonwjackson:2ship")
assert.equal(receipt.package, packagePath)
assert.deepEqual(receipt.desired, { state: "Enabled" })
assert.equal(receipt.previous, null)

const root = mkdtempSync(join(tmpdir(), "korri-2ship-contract-"))
try {
  for (const filename of [
    "Majora's Mask (USA).n64",
    "ROM '; $(exit 19) #.z64",
  ]) {
    const account = join(root, `Account ${filename}`)
    const directory = join(account, "2ship")
    const input: PluginLaunchInput = {
      runnerId: runners["2ship"].id,
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
      env: { SHIP_HOME: directory },
    })
    const launch = spawnSync(
      korridCli,
      ["plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(input)],
      { encoding: "utf8" },
    )
    assert.equal(launch.status, 0, launch.stderr)
    assert.equal(
      launch.stdout,
      `${directory}\n${directory}\n${input.contentPath}\n`,
    )

    // Exercise the actual packaged launcher and host executor with invalid data.
    // Failure must preserve existing archives, config and saves without extraction.
    mkdirSync(join(directory, "saves"))
    const preserved = ["mm.o2r", "2ship2harkinian.json", "saves/file1.json"]
    for (const file of preserved)
      writeFileSync(join(directory, file), `unchanged:${file}`)
    input.program = manifest.files["2ship"]
    for (const bytes of [
      Buffer.from("not a ROM"),
      Buffer.alloc(32 * 1024 * 1024),
    ]) {
      writeFileSync(input.contentPath, bytes)
      const failure = spawnSync(
        korridCli,
        [
          "plugin-launch",
          join(packagePath, "plugin.ts"),
          JSON.stringify(input),
        ],
        { encoding: "utf8", timeout: 10000 },
      )
      assert.equal(failure.status, 1, failure.stderr)
      assert.match(failure.stderr, /2 Ship launch failed:/)
      for (const file of preserved) {
        assert.equal(
          readFileSync(join(directory, file), "utf8"),
          `unchanged:${file}`,
        )
      }
      assert.deepEqual(readFileSync(input.contentPath), bytes)
      assert(
        !readdirSync(directory).some((entry) =>
          entry.startsWith(".2ship-extract-"),
        ),
      )
    }
  }
  const usage = spawnSync(manifest.files["2ship"], [], { encoding: "utf8" })
  assert.equal(usage.status, 2, usage.stderr)
  assert.match(usage.stderr, /Usage: 2ship/)
} finally {
  rmSync(root, { recursive: true, force: true })
}
console.log(
  "2 Ship package, contract, admission, literal paths and safe invalid-ROM rejection passed",
)
