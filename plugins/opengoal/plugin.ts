import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "opengoal"
export const title = "Jak and Daxter trilogy"
export const description =
  "Runs OpenGOAL with game data prepared off-device from your own PS2 discs. Linux x86_64 only."

// These identify upstream out/<game>/iso/GAME.CGO produced by OpenGOAL 0.3.8,
// not an ISO, archive, or the complete prepared directory. See README.md.
export const runners = {
  jak1: {
    id: "@simonwjackson:opengoal/jak1",
    program: "opengoal",
    releases: [
      "sha256:3cda4bc7f551a51d2fa9c4d5949549237ea846ce4851437403dbe91548a52807",
    ],
  },
  jak2: {
    id: "@simonwjackson:opengoal/jak2",
    program: "opengoal",
    releases: [
      // USA v1.00, then Jak II: Renegade Europe/Australia.
      "sha256:6a673c9cf1e7aee115e82be459b1348fd1981fef49086569aae67a2a64c4cc14",
      "sha256:a8c829303340a1c572252e408f0730e2495d84505cdfcd94b3e34167fd9a6ad8",
    ],
  },
  jak3: {
    id: "@simonwjackson:opengoal/jak3",
    program: "opengoal",
    releases: [
      "sha256:442becdbf74aa11fe046e76c243b7ce0122d924593f6e20682ff06ae5dacd4f5",
    ],
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("OpenGOAL is a native engine and loads no emulator core")
  }
  if (
    input.overrides?.config !== undefined ||
    Object.keys(input.overrides?.settings ?? {}).length > 0
  ) {
    throw new Error("Configure OpenGOAL through its native game settings")
  }
  const game = (Object.keys(runners) as Array<keyof typeof runners>).find(
    (candidate) => runners[candidate].id === input.runnerId,
  )
  if (game === undefined) {
    throw new Error("Unknown OpenGOAL runner")
  }
  const suffix = `/out/${game}/iso/GAME.CGO`
  const segments = input.contentPath.split("/")
  if (
    !input.contentPath.startsWith("/") ||
    !input.contentPath.endsWith(suffix) ||
    segments.includes(".") ||
    segments.includes("..")
  ) {
    throw new Error(`Select ${suffix} inside a complete OpenGOAL 0.3.8 prepared data directory`)
  }
  const data = input.contentPath.slice(0, -suffix.length) || "/"
  return {
    command: input.program,
    args: ["--game", game, "--proj-path", data],
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
