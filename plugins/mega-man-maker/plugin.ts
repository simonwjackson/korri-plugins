import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

// Mega Man Maker, the public Windows 1.10.4.2 release: a 64-bit GameMaker
// game. korrid downloads the ZIP as the artifact `game` and the game's
// release names `data.win` in its ready directory (ADR 0013). The runner
// starts `MegaMaker.exe` beside it with Proton-CachyOS for arm64, whose
// built-in FEX DLLs run the x86_64 Windows code. It needs no FEX rootfs.
export const name = "mega-man-maker"
export const title = "Mega Man Maker"
export const description =
  "Public Windows 1.10.4.2 release of Mega Man Maker, run with Proton."

// The release identity: the SHA-256 of `data.win`, the game's content, not of
// the ZIP or of the GameMaker runner `MegaMaker.exe` (ADR 0013).
const dataWin =
  "sha256:888d7eee4442e3105ba28fe05d126d26901ef98e82380a2c0096ac4d6953dca4"

// The URL and ZIP hash are those of legacy `packages/mega-man-maker/default.nix`.
// `bytes` is the size downloaded on 2026-10-21.
export const artifacts = {
  game: {
    id: "@simonwjackson:mega-man-maker/game",
    version: "1.10.4.2",
    files: [
      {
        url: "https://megamanmaker.com/downloads/MegaMaker_v1_10_4_2.zip",
        sha256: "sha256:3d2145136bb828b86f88f0efbd6d719d1cdea1c3c23d6c753f5432d33c6fe6af",
        bytes: 83060701,
      },
    ],
    unpack: "game-unpack",
  },
}

export const games = {
  "mega-man-maker": {
    title: "Mega Man Maker",
    releases: {
      "1.10.4.2": {
        hashes: [dataWin],
        artifacts: ["@simonwjackson:mega-man-maker/game"],
        file: { artifact: "@simonwjackson:mega-man-maker/game", path: "data.win" },
      },
    },
  },
}

// No system: the runner accepts the release by its hash. Proton is the
// `@korri:proton` plugin's artifact; korrid downloads it before the launch.
export const runners = {
  proton: {
    id: "@simonwjackson:mega-man-maker/proton",
    program: "proton-launch",
    releases: [dataWin],
    artifacts: ["@korri:proton/cachyos"],
  },
}

const protonArtifact = "@korri:proton/cachyos"

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (!input.contentPath) {
    throw new Error("Mega Man Maker requires a content path")
  }
  if (input.corePath !== undefined) {
    throw new Error("Mega Man Maker is a whole game and loads no core")
  }
  const overrides = input.overrides
  if (overrides?.config !== undefined) {
    throw new Error("Mega Man Maker takes no raw config override")
  }
  if (
    overrides?.settings !== undefined &&
    Object.keys(overrides.settings).length > 0
  ) {
    throw new Error("Mega Man Maker runner does not implement typed settings")
  }
  if (!input.contentPath.startsWith("/")) {
    throw new Error("Mega Man Maker requires an absolute content path")
  }
  const proton = input.artifacts[protonArtifact]
  if (!proton) {
    throw new Error(`Mega Man Maker requires the ready ${protonArtifact} artifact`)
  }
  // The content path is `data.win`; MegaMaker.exe is in the same directory.
  const gameDirectory =
    input.contentPath.slice(0, input.contentPath.lastIndexOf("/")) || "/"
  // The Wine prefix, and in it the game's %LOCALAPPDATA%\Megamaker with
  // levels, settings and GIFs, live under this account directory.
  const home = `${input.accountRoot}/mega-man-maker`
  return {
    command: input.program,
    args: [input.contentPath],
    env: { HOME: home, KORRI_PROTON: proton },
    cwd: gameDirectory,
    directories: [home],
    envUnset: [],
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
