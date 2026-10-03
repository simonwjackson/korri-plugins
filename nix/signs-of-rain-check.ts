import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { createHash } from "node:crypto"
import { accessSync, constants, existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import process from "node:process"
import type { PluginLaunchInput } from "../contracts/generated/korrid"
import * as plugin from "../plugins/signs-of-rain/plugin"

const [packagePath, gamePackage, hostCli, korridCli, recordArguments] = process.argv.slice(2)
assert(packagePath && gamePackage && hostCli && korridCli && recordArguments)
const manifest = JSON.parse(readFileSync(join(packagePath, "manifest.json"), "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.equal(manifest.entry, "plugin.ts")
assert.deepEqual(manifest.packages, { "signs-of-rain": gamePackage })
assert.deepEqual(manifest.files, { "signs-of-rain": join(gamePackage, "bin/signs-of-rain") })
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
assert.equal(manifest.requires, undefined)
accessSync(manifest.files["signs-of-rain"], constants.X_OK)
const pack = join(gamePackage, "share/signs-of-rain/signs-of-rain.pck")
const hash = createHash("sha256").update(readFileSync(pack)).digest("hex")
assert.equal(plugin.name, "signs-of-rain")
assert.deepEqual(Object.keys(plugin).sort(), ["description", "handlers", "name", "runners", "title"])
assert.deepEqual(plugin.runners, {
  "signs-of-rain": {
    id: "@simonwjackson:signs-of-rain/signs-of-rain",
    program: "signs-of-rain",
    releases: [`sha256:${hash}`],
  },
})
assert.deepEqual(Object.keys(plugin.handlers), ["launch.prepare"])
assert.equal(readFileSync(join(packagePath, "plugin.ts"), "utf8").includes("@PACK_SHA256@"), false)

// Existing build-side host admission; this does not install, approve or enable a plugin.
const admission = spawnSync(hostCli, [
  "seed", packagePath, "https://cache.example.invalid",
], { encoding: "utf8", timeout: 30_000 })
assert.equal(admission.status, 0, admission.stderr)
const receipt = JSON.parse(admission.stdout)
assert.equal(receipt.id, "@simonwjackson:signs-of-rain")
assert.equal(receipt.package, packagePath)
assert.deepEqual(receipt.desired, { state: "Enabled" })
assert.equal(receipt.previous, null)

const work = mkdtempSync(join(tmpdir(), "signs-of-rain-contract-"))
const inherited = {
  SDL_GAMECONTROLLERCONFIG: "seat controller mapping,buttons and axes",
  SDL_JOYSTICK_HIDAPI: "0",
  XDG_RUNTIME_DIR: "/run/user/1001",
  WAYLAND_DISPLAY: "wayland-test",
  DISPLAY: ":42",
  DBUS_SESSION_BUS_ADDRESS: "unix:path=/run/user/1001/bus",
  PULSE_SERVER: "unix:/run/user/1001/pulse/native",
}
try {
  for (const accountRoot of [join(work, "Player One '; $(exit 21)"), join(work, "Player Two")]) {
    assert.equal(existsSync(accountRoot), false)
    for (const contentPath of [pack, "/library/Rain %s '; $(exit 19) #.pck"]) {
      const input: PluginLaunchInput = {
        runnerId: plugin.runners["signs-of-rain"].id,
        program: recordArguments,
        contentPath,
        accountRoot,
        files: manifest.files,
      }
      const expected = {
        command: recordArguments,
        args: ["--main-pack", contentPath,
          "--rendering-method", "gl_compatibility", "--rendering-driver", "opengl3_es",
          "--", "--handheld", "--graphics=fast"],
        env: { HOME: accountRoot },
        envUnset: ["XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"],
        cwd: accountRoot,
        directories: [accountRoot],
      }
      assert.deepEqual(plugin.handlers["launch.prepare"](input), expected)
      assert.deepEqual(plugin.handlers["launch.prepare"]({
        ...input, overrides: { settings: {} },
      }), expected)
      // Real korrid sandbox evaluation and exec into a literal argv/env observer.
      const launch = spawnSync(korridCli, [
        "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(input),
      ], {
        encoding: "utf8", timeout: 30_000,
        env: {
          ...process.env, ...inherited,
          XDG_DATA_HOME: "/host/data", XDG_CONFIG_HOME: "/host/config", XDG_CACHE_HOME: "/host/cache",
        },
      })
      assert.equal(launch.status, 0, launch.stderr)
      assert.deepEqual(JSON.parse(launch.stdout), {
        args: expected.args, cwd: accountRoot,
        env: { ...inherited, HOME: accountRoot, XDG_DATA_HOME: null, XDG_CONFIG_HOME: null, XDG_CACHE_HOME: null },
      })
      assert.equal(existsSync(accountRoot), true)

      for (const unsupported of [
        { runnerId: "@other:runner/runner" },
        { corePath: "/core.so" },
        { overrides: { config: { replace: "ignored settings" } } },
        { overrides: { config: {} } },
        { overrides: { settings: { fullscreen: true } } },
        { program: "relative-program" },
        { program: "/program\0" },
        { contentPath: "--help" },
        { contentPath: "relative.pck" },
        { contentPath: "/library/pack\0.pck" },
        { accountRoot: "relative-account" },
        { accountRoot: "/account\0" },
      ]) {
        const invalid = { ...input, ...unsupported }
        assert.throws(() => plugin.handlers["launch.prepare"](invalid))
        const rejected = spawnSync(korridCli, [
          "plugin-launch", join(packagePath, "plugin.ts"), JSON.stringify(invalid),
        ], { encoding: "utf8", timeout: 30_000 })
        assert.notEqual(rejected.status, 0)
        assert.equal(rejected.stdout, "")
      }
    }
  }
} finally {
  rmSync(work, { recursive: true, force: true })
}
console.log("Signs of Rain exact-pack manifest, types, host admission and Core sandbox launch contract passed")
