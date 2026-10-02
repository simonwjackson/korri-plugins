import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

export const name = "zelda3"
export const title = "Zelda3"
export const description =
  "Runs A Link to the Past natively from your own supported US ROM."

// Same system identity as the published Snes9x plugin.
export const systems = {
  snes: { id: "snes", title: "Super Nintendo" },
}

export const runners = {
  zelda3: {
    id: "@simonwjackson:zelda3/zelda3",
    program: "zelda3",
    // Upstream README's whole, unheadered US ROM SHA-256.
    releases: [
      "sha256:66871d66be19ad2c34c927d6b14cd8eb6fc3181965b6e517cb361f7316009cfb",
    ],
  },
}

export const discovery = {
  fileReleases: {
    "snes-files": {
      id: "@simonwjackson:zelda3/snes-files",
      title: "Super Nintendo files",
      extensions: ["sfc", "smc"],
      system: "snes",
      runners: [runners.zelda3.id],
    },
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (input.corePath !== undefined) {
    throw new Error("Zelda3 is a standalone game and loads no core")
  }
  if (
    input.overrides?.config !== undefined ||
    Object.keys(input.overrides?.settings ?? {}).length > 0
  ) {
    throw new Error("Zelda3 does not implement Korri launch overrides")
  }
  // The user chose account-owned storage, following PPSSPP's runner pattern.
  // The launcher retains upstream's zelda3.ini, zelda3_assets.dat and saves/.
  return {
    command: input.program,
    args: ["--", input.contentPath, `${input.accountRoot}/zelda3`],
    env: {},
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
