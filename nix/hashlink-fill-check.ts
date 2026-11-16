import assert from "node:assert/strict"
import { accessSync, constants, readFileSync, readdirSync } from "node:fs"
import { spawnSync } from "node:child_process"
import type { PluginComposeInput } from "../contracts/generated/korrid"
import { handlers, modifiers, name } from "../plugins/hashlink-fill/plugin"

const [packagePath, hostCli] = process.argv.slice(2)
assert(packagePath && hostCli)
const manifest = JSON.parse(readFileSync(`${packagePath}/manifest.json`, "utf8"))
assert.deepEqual(manifest.publisher, { namespace: "@simonwjackson" })
assert.deepEqual(manifest.sources, ["plugin.ts"])
assert.deepEqual(Object.keys(manifest.packages), ["patcher"])
assert.deepEqual(Object.keys(manifest.files).sort(), ["deadcells.json", "patcher"])
assert.deepEqual(manifest.services, {})
assert.deepEqual(manifest.ports, {})
accessSync(manifest.files.patcher, constants.X_OK)
const fix = JSON.parse(readFileSync(manifest.files["deadcells.json"], "utf8"))
assert.equal(fix.app, "588650")
assert.equal(fix.expected_matches, 2)
assert.equal(fix.type, "Main")
assert.equal(fix.method, "onResize")
assert(readFileSync(`${manifest.packages.patcher}/share/licenses/hl-fill/LICENSE`, "utf8").includes("TLin-Y"))
assert(readdirSync(`${manifest.packages.patcher}/share/licenses/hl-fill/dependencies`).length > 0)
assert.equal(name, "hashlink-fill")
assert.deepEqual(modifiers, { fill: { id: "@simonwjackson:hashlink-fill/fill" } })
assert.deepEqual(Object.keys(handlers), ["launch.compose"])
const input: PluginComposeInput = {
  modifierId: modifiers.fill.id,
  runnerId: "@korri:steam/steam",
  plan: {
    command: "/store/steam-session", args: ["588650"],
    env: { STEAM_HOME: "/account/steam '; $() #", KEEP_ME: "value" },
    envUnset: ["REMOVE_ME"], directories: ["/account/steam"], cwd: "/game",
  },
  settings: {}, config: {}, files: manifest.files,
}
const compose = handlers["launch.compose"]
const planBefore = JSON.stringify(input.plan)
const wrapped = {
  ...input.plan,
  command: "/nix/store/gamescope/bin/gamescope",
  args: [
    "--backend", "wayland", "--fullscreen", "--expose-wayland",
    "--output-width", "2448", "--output-height", "1848",
    "--force-composition", "--",
    "/nix/store/native-steam-session/bin/steam-session", "588650",
  ],
}
assert.deepEqual(compose({ ...input, plan: wrapped }), {
  ...wrapped,
  command: manifest.files.patcher,
  args: [
    "prepare", "--fix", manifest.files["deadcells.json"],
    "--steam-home", input.plan.env?.STEAM_HOME, "--app", "588650",
    "--cache", `${input.plan.env?.STEAM_HOME}/.korri/hashlink-fill/`,
    "--", wrapped.command, ...wrapped.args,
  ],
})
assert.deepEqual(compose(input), {
  ...input.plan,
  command: manifest.files.patcher,
  args: [
    "prepare", "--fix", manifest.files["deadcells.json"],
    "--steam-home", input.plan.env?.STEAM_HOME, "--app", "588650",
    "--cache", `${input.plan.env?.STEAM_HOME}/.korri/hashlink-fill/`,
    "--", input.plan.command, ...input.plan.args,
  ],
})
assert.equal(JSON.stringify(input.plan), planBefore)
assert.strictEqual(compose({ ...input, runnerId: "@simonwjackson:2ship/2ship" }), input.plan)
for (const plan of [
  { ...input.plan, args: [] },
  { ...input.plan, args: ["--backend"] },
  { ...input.plan, args: ["0"] },
  { ...input.plan, args: ["588650junk"] },
  { ...wrapped, args: ["--backend", "wayland", "--", "/bin/other", "588650"] },
  { ...wrapped, args: ["--", "/bin/steam-session"] },
  { ...input.plan, env: {} },
  { ...input.plan, env: undefined },
]) assert.strictEqual(compose({ ...input, plan }), plan)
assert.strictEqual(compose({ ...input, files: {} }), input.plan)
assert.equal(compose({ ...input, plan: { ...input.plan, args: ["123", "literal arg"] } }).args.at(-1), "literal arg")

// Host seed evaluates the packaged source in Core's actual script sandbox and
// validates its modifier ID. This pinned Core requires no settings handlers for
// a modifier with no settings.
const admission = spawnSync(hostCli, ["seed", packagePath, "https://cache.example.invalid"], { encoding: "utf8" })
assert.equal(admission.status, 0, admission.stderr)
assert.equal(JSON.parse(admission.stdout).id, "@simonwjackson:hashlink-fill")
console.log("HashLink Fill manifest, Core admission and compose checks passed")
