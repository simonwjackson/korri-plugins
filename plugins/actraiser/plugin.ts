import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "actraiser"
export const title = "ActRaiser Recomp"
export const description =
  "Runs a private native build from your own supported ActRaiser USA cartridge."

// Existing SNES identity, shared with SMW, Zelda3 and Snes9x.
export const systems = {
  snes: {
    id: "snes",
    title: "Super Nintendo",
    content: { extensions: ["sfc", "smc"] },
  },
}

export const runners = {
  actraiser: {
    id: "@simonwjackson:actraiser/actraiser",
    program: "actraiser",
    // Upstream's ROM contract, verified against the owner's actual cartridge dump.
    releases: [
      "sha256:b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0",
    ],
  },
}

export const games = {
  actraiser: {
    title: "ActRaiser",
    releases: {
      original: {
        system: "snes",
        hashes: runners.actraiser.releases,
      },
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("ActRaiser is standalone and loads no emulator core")
  }
  if (
    input.overrides?.config !== undefined ||
    Object.keys(input.overrides?.settings ?? {}).length > 0
  ) {
    throw new Error("ActRaiser does not implement Korri launch overrides")
  }
  return {
    command: input.program,
    args: ["--", input.contentPath],
    // Retain upstream's ActRaiserRecomp/game namespace within Core's existing
    // accountRoot. The native runtime owns config, settings and save formats.
    env: { AR_USER_DATA_DIR: `${input.accountRoot}/ActRaiserRecomp/game` },
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
