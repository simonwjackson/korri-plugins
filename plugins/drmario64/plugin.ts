import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "drmario64"
export const title = "Dr. Mario 64 Recompiled"
export const description =
  "Runs Dr. Mario 64 natively from your own supported US Nintendo 64 ROM."

export const systems = {
  n64: { id: "n64", title: "Nintendo 64" },
}

export const runners = {
  drmario64: {
    id: "@simonwjackson:drmario64/drmario64",
    program: "drmario64",
    releases: [
      // Measured owner-supplied US ROM: original swap16 and canonical big-endian.
      "sha256:613778b244784492a881c0d72d6017f82c39026706a406bd7ef95c6f33e53b89",
      "sha256:bb2c0dec0a8287ad256929563d0509801c2f239df883c1cf52cab05b23bd77b6",
    ],
  },
}

export const discovery = {
  fileReleases: {
    "n64-roms": {
      id: "@simonwjackson:drmario64/n64-roms",
      title: "Nintendo 64 ROMs",
      extensions: ["n64", "z64", "v64"],
      system: "n64",
      runners: [runners.drmario64.id],
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("Dr. Mario 64 is a native runner, not an emulator core")
  }
  if (
    input.overrides?.config !== undefined ||
    Object.keys(input.overrides?.settings ?? {}).length > 0
  ) {
    throw new Error("Dr. Mario 64 uses its native settings, not Korri overrides")
  }
  // Core supplies accountRoot; drmario64.us is upstream's registered game_id.
  const directory = `${input.accountRoot}/drmario64.us`
  return {
    command: input.program,
    args: [input.contentPath],
    cwd: directory,
    directories: [directory],
    env: { APP_FOLDER_PATH: directory },
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
