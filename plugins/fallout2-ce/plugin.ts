import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "fallout2-ce"
export const title = "Fallout 2 Community Edition"
export const description =
  "Runs Fallout 2 with your own installed game data. Requires a writable installation folder."

export const runners = {
  "fallout2-ce": {
    id: "@simonwjackson:fallout2-ce/fallout2-ce",
    program: "fallout2-ce",
    releases: [
      // MASTER.DAT from the owner's Interplay-Fallout2-Win95.iso, 333176843 bytes.
      "sha256:bf349305c3749ce6501c1e3618689d3ccbecd732569d486183786a227fc79703",
    ],
  },
}

export const games = {
  fallout2: {
    title: "Fallout 2",
    releases: {
      prepared: {
        hashes: runners["fallout2-ce"].releases,
        file: "fallout2-ce/MASTER.DAT",
      },
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  // Provider-ref routes carry no file. This runner always loads one.
  const contentPath = input.contentPath
  if (contentPath === undefined) {
    throw new Error("Fallout 2 Community Edition requires a content file")
  }
  if (input.runnerId !== runners["fallout2-ce"].id) {
    throw new Error("Unknown Fallout 2 runner")
  }
  if (input.corePath !== undefined) {
    throw new Error("Fallout 2 CE is a native engine, not an emulator core")
  }
  if (input.overrides?.config !== undefined) {
    throw new Error("Configure Fallout 2 with its native fallout2.cfg and f2_res.ini")
  }
  if (Object.keys(input.overrides?.settings ?? {}).length > 0) {
    throw new Error("Fallout 2 CE does not implement typed settings")
  }
  const separator = contentPath.lastIndexOf("/")
  if (
    !contentPath.startsWith("/") ||
    contentPath.slice(separator + 1).toLowerCase() !== "master.dat"
  ) {
    throw new Error("Select MASTER.DAT in an installed Fallout 2 folder")
  }
  return {
    command: input.program,
    args: [],
    cwd: contentPath.slice(0, separator) || "/",
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
