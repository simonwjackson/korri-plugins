import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "super-mario-world"
export const title = "Super Mario World"
export const description =
  "Runs the native Super Mario World reimplementation with your own USA ROM."

export const systems = {
  snes: { id: "snes", title: "Super Nintendo" },
}

export const runners = {
  smw: {
    id: "@simonwjackson:super-mario-world/smw",
    program: "smw",
    releases: [
      // Measured from the owner's Super Mario World (U) [!].smc, 524800 bytes.
      "sha256:d70c9c7716ad12c674fc7dd744736aa48d4d7b4237f58066be620fda26024872",
      // The same USA ROM without its 512-byte copier header, 524288 bytes.
      "sha256:0838e531fe22c077528febe14cb3ff7c492f1f5fa8de354192bdff7137c27f5b",
    ],
  },
}

export const discovery = {
  fileReleases: {
    "snes-files": {
      id: "@simonwjackson:super-mario-world/snes-files",
      title: "Super Nintendo files",
      extensions: ["smc", "sfc"],
      system: "snes",
      runners: [runners.smw.id],
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("SMW is a native program and loads no emulator core")
  }
  if (input.overrides?.config !== undefined) {
    throw new Error("SMW takes configuration through its native smw.ini")
  }
  if (Object.keys(input.overrides?.settings ?? {}).length > 0) {
    throw new Error("SMW runner does not implement typed settings yet")
  }
  // User chose separate account storage; filenames inside it belong to smw.
  const directory = `${input.accountRoot}/smw`
  return {
    command: input.program,
    args: [input.contentPath],
    cwd: directory,
    directories: [directory],
    env: {},
    envUnset: [],
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
