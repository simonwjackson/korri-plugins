import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "dr-mario"
export const title = "Dr. Mario NES Recomp"
export const description =
  "Runs the native Dr. Mario preview with your own supported Europe NES ROM."

// Retain the NES identity used by the publisher's libretro cores.
export const systems = {
  nes: { id: "nes", title: "Nintendo Entertainment System" },
}

export const runners = {
  "dr-mario": {
    id: "@simonwjackson:dr-mario/dr-mario",
    program: "dr-mario",
    releases: [
      // Measured whole-file hash of the owner's 65552-byte Europe iNES ROM.
      "sha256:83914c08f82fc70779121760a48392af3a5988f015794eb53cbe1aa0a165c821",
    ],
  },
}

export const discovery = {
  fileReleases: {
    "nes-files": {
      id: "@simonwjackson:dr-mario/nes-files",
      title: "Nintendo Entertainment System files",
      extensions: ["nes"],
      system: "nes",
      runners: [runners["dr-mario"].id],
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("Dr. Mario is standalone and loads no emulator core")
  }
  if (
    input.overrides?.config !== undefined ||
    Object.keys(input.overrides?.settings ?? {}).length > 0
  ) {
    throw new Error("Dr. Mario uses its native config.ini and keybinds.ini")
  }
  // User-approved account namespace, named after upstream's executable.
  const directory = `${input.accountRoot}/DrMarioRecomp`
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
