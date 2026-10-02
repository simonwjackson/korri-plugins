import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "the-simpsons-game"
export const title = "The Simpsons Game"
export const description =
  "Runs the native Xbox 360 recompilation with your own USA disc image."

export const systems = {
  "xbox-360": { id: "xbox-360", title: "Xbox 360" },
}

export const runners = {
  simpsons: {
    id: "@simonwjackson:the-simpsons-game/simpsons",
    program: "simpsons",
    releases: [
      // Whole simpsons-ntscu-cs.iso, 7,835,492,352 bytes, from the owner's RAR.
      "sha256:fd794e7a3025c3fd1340d25301658bac8c829a65d5e5e47d2663b431f869531b",
    ],
  },
}

export const discovery = {
  fileReleases: {
    "xbox-360-discs": {
      id: "@simonwjackson:the-simpsons-game/xbox-360-discs",
      title: "Xbox 360 disc images",
      extensions: ["iso"],
      system: "xbox-360",
      runners: [runners.simpsons.id],
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("The Simpsons Game is native and loads no emulator core")
  }
  if (input.overrides?.config !== undefined) {
    throw new Error("The Simpsons Game uses its native simpsons.toml")
  }
  if (Object.keys(input.overrides?.settings ?? {}).length > 0) {
    throw new Error(
      "The Simpsons Game runner does not implement typed settings",
    )
  }
  // Account isolation is user-approved; native filenames stay with upstream.
  const directory = `${input.accountRoot}/simpsons`
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
