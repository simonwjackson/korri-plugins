import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

// Identity follows the selected upstream repository, Oery/fable-ii-recomp.
export const name = "fable-ii-recomp"
export const title = "Fable II"
export const description =
  "Runs the experimental native Fable II recompilation with your USA/Europe GOTY ISO."

export const systems = {
  "xbox-360": { id: "xbox-360", title: "Xbox 360" },
}

export const runners = {
  fable_ii: {
    id: "@simonwjackson:fable-ii-recomp/fable_ii",
    program: "fable_ii",
    releases: [
      // Whole owned Fable 2 PLT.iso, 7,838,695,424 bytes. Its XEX is USA/EU GOTY.
      "sha256:2cdaafead95680e2c6fe8886a89f1ae3d5e41549857c7fc125a12aab1cb99ad9",
    ],
  },
}

export const discovery = {
  fileReleases: {
    "xbox-360-discs": {
      id: "@simonwjackson:fable-ii-recomp/xbox-360-discs",
      title: "Xbox 360 disc images",
      extensions: ["iso"],
      system: "xbox-360",
      runners: [runners.fable_ii.id],
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("Fable II is native and loads no emulator core")
  }
  if (input.overrides?.config !== undefined) {
    throw new Error("Fable II uses its native fable_ii.toml")
  }
  if (Object.keys(input.overrides?.settings ?? {}).length > 0) {
    throw new Error("The Fable II runner does not implement typed settings")
  }
  // Core owns accountRoot. fable_ii is the upstream ReXApp name and user folder.
  const directory = `${input.accountRoot}/fable_ii`
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
