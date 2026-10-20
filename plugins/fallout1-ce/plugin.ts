import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "fallout1-ce"
export const title = "Fallout Community Edition"
export const description =
  "Runs Fallout with your own installed game data. Requires a writable installation folder."

export const runners = {
  "fallout-ce": {
    id: "@simonwjackson:fallout1-ce/fallout-ce",
    program: "fallout-ce",
    releases: [
      // MASTER.DAT from the owner's Fallout (1997).zip, 333674504 bytes.
      "sha256:8cdb879ac4431dce48a25c3e02e9db4aee3449b73e7b185a63d69fef3982a509",
    ],
  },
}

export const games = {
  fallout1: {
    title: "Fallout",
    releases: {
      prepared: {
        hashes: runners["fallout-ce"].releases,
        file: "fallout-ce/MASTER.DAT",
      },
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  // Provider-ref routes carry no file. This runner always loads one.
  const contentPath = input.contentPath
  if (contentPath === undefined) {
    throw new Error("Fallout Community Edition requires a content file")
  }
  if (input.runnerId !== runners["fallout-ce"].id) {
    throw new Error("Unknown Fallout runner")
  }
  if (input.corePath !== undefined) {
    throw new Error("Fallout CE is a native engine, not an emulator core")
  }
  if (input.overrides?.config !== undefined) {
    throw new Error("Configure Fallout with its native fallout.cfg and f1_res.ini")
  }
  if (Object.keys(input.overrides?.settings ?? {}).length > 0) {
    throw new Error("Fallout CE does not implement typed settings")
  }
  const separator = contentPath.lastIndexOf("/")
  if (
    !contentPath.startsWith("/") ||
    contentPath.slice(separator + 1).toLowerCase() !== "master.dat"
  ) {
    throw new Error("Select MASTER.DAT in an installed Fallout folder")
  }
  // Upstream reads native configuration, companion data and saves from cwd.
  // Do not copy assets, overwrite configuration, or introduce a save layout.
  return {
    command: input.program,
    args: [],
    cwd: contentPath.slice(0, separator) || "/",
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
