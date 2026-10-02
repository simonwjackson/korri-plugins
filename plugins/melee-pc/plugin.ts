import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "melee-pc"
export const title = "Melee PC"
export const description =
  "Runs Super Smash Bros. Melee natively from your supported USA 1.02 disc. Beta software."

export const runners = {
  "melee-pc": {
    id: "@simonwjackson:melee-pc/melee-pc",
    program: "melee-pc",
    // Measured whole-file identity of the owner's 1,459,978,240-byte GALE01 rev 2 ISO.
    releases: [
      "sha256:0de05981a34156b9cedcef73c73d4244ac05cf6149ab3c9cfed917698819e464",
    ],
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("Melee PC is a standalone game and loads no core")
  }
  if (
    input.overrides?.config !== undefined ||
    Object.keys(input.overrides?.settings ?? {}).length > 0
  ) {
    throw new Error("Melee PC does not implement Korri launch overrides")
  }
  return {
    command: input.program,
    args: ["--", input.contentPath, input.accountRoot],
    env: {},
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
