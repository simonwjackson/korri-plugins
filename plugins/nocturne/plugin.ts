import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "nocturne"
export const title = "NocturneRecomp"
export const description =
  "Runs Castlevania: Symphony of the Night from your extracted Xbox Live Arcade game."

export const systems = {
  "xbox-360": { id: "xbox-360", title: "Xbox 360" },
}

export const runners = {
  nocturne: {
    id: "@simonwjackson:nocturne/nocturne",
    program: "nocturne",
    // Upstream GameDataSelectorSettings.default_xex_sha256, also measured
    // from the owner's XBLA package. This identifies default.xex, not STFS.
    releases: [
      "sha256:26a58b074c5dd6185b77a8111a0012866d11cba674b4b0810d79dbf07ad68aa6",
    ],
  },
}

export const discovery = {
  fileReleases: {
    "xbox-360-executables": {
      id: "@simonwjackson:nocturne/xbox-360-executables",
      title: "Xbox 360 executables",
      extensions: ["xex"],
      system: "xbox-360",
      runners: [runners.nocturne.id],
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("Nocturne is a standalone game and loads no core")
  }
  if (
    input.overrides?.config !== undefined ||
    Object.keys(input.overrides?.settings ?? {}).length > 0
  ) {
    throw new Error("Nocturne does not implement Korri launch overrides")
  }
  return {
    command: input.program,
    // accountRoot follows the existing Zelda3/PPSSPP launch contract.
    // nocturnerecomp is the SDK's native application data-directory name.
    args: ["--", input.contentPath, `${input.accountRoot}/nocturnerecomp`],
    env: {},
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
