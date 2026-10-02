import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "2ship"
export const title = "2 Ship 2 Harkinian"
export const description =
  "Runs Majora's Mask natively from your own supported Nintendo 64 ROM."

export const systems = {
  n64: { id: "n64", title: "Nintendo 64" },
}

export const runners = {
  "2ship": {
    id: "@simonwjackson:2ship/2ship",
    program: "2ship",
    releases: [
      // Owner's NTSC-U 1.0 dump, 32 MiB. Original bytes and big-endian form.
      "sha256:8dc31559174f958a938ab7eccb25dd310a4167f98cb68a521181f4653b684431",
      "sha256:efb1365b3ae362604514c0f9a1a2d11f5dc8688ba5be660a37debf5e3be43f2b",
    ],
  },
}

export const discovery = {
  fileReleases: {
    "n64-roms": {
      id: "@simonwjackson:2ship/n64-roms",
      title: "Nintendo 64 ROMs",
      extensions: ["n64", "z64", "v64"],
      system: "n64",
      runners: ["@simonwjackson:2ship/2ship"],
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  // Core supplies accountRoot; upstream's appShortName / SDL directory is 2ship.
  const directory = `${input.accountRoot}/2ship`
  return {
    command: input.program,
    args: [input.contentPath],
    cwd: directory,
    directories: [directory],
    env: { SHIP_HOME: directory },
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
