import type {
  PluginComposeInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "hashlink-fill"
export const title = "HashLink Fill"
export const description =
  "Removes Dead Cells' stage aspect-ratio clamp before its Steam session."

export const modifiers = {
  fill: { id: "@simonwjackson:hashlink-fill/fill" },
}

function composeLaunch(input: PluginComposeInput): PluginLaunchOutput {
  const plan = input.plan
  if (input.runnerId !== "@korri:steam/steam") return plan
  // Earlier modifiers (Gamescope at Device on aka) can wrap steam-session.
  // Read only argv elements; never parse a shell command or rewrite a wrapper.
  const basename = (program: string) => program.split("/").pop()
  const steamIndex = basename(plan.command) === "steam-session"
    ? -1
    : plan.args.findIndex(arg => basename(arg) === "steam-session")
  if (steamIndex === -1 && basename(plan.command) !== "steam-session") return plan
  const app = plan.args[steamIndex + 1]
  const steamHome = plan.env?.STEAM_HOME
  const patcher = input.files.patcher
  const fix = input.files["deadcells.json"]
  // A malformed or unrelated plan must never prevent the original launch.
  if (!app || !/^[1-9][0-9]*$/.test(app) || !steamHome || !patcher || !fix) return plan
  return {
    ...plan,
    command: patcher,
    args: [
      "prepare", "--fix", fix, "--steam-home", steamHome, "--app", app,
      // PluginComposeInput carries no cacheRoot. Keep private backups in Steam's
      // existing writable account root, not in the immutable plugin closure.
      "--cache", `${steamHome}/.korri/hashlink-fill/`,
      "--", plan.command, ...plan.args,
    ],
  }
}

export const handlers = {
  "launch.compose": composeLaunch,
}
