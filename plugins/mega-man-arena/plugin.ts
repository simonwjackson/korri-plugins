import type {
  PluginLaunchInput,
  PluginLaunchOutput,
} from "../../contracts/generated/korrid"

// KishSquared's Mega Man Arena, the public Windows x86_64 GameMaker build.
// korrid downloads the ZIP as the artifact `game`, and the game's release
// names `data.win` in its ready directory (ADR 0013). The runner starts
// MegaManArena.exe beside it with the Proton-CachyOS arm64 build of
// @korri:proton, whose own FEX runs the x86 Windows code. The game's
// extension DLLs (gme.dll, libxprocess_x64.dll, rousrDissonance.dll) are
// Windows code, so no native engine can replace Proton here.
export const name = "mega-man-arena"
export const title = "Mega Man Arena"
export const description =
  "Public Windows release of KishSquared's Mega Man Arena, played with Proton."

// The release identity: the SHA-256 of `data.win`, the GameMaker game data,
// not of the ZIP (ADR 0013).
const dataWin =
  "sha256:1c9b5c7787f7286fd515af0bb16c1fa79349d9e00c32c61b75cedd0f7cd9ca4f"

// The download page's link (megamanarena.com/download-page, read on
// 2026-10-21). It redirects to Dropbox's MegaManArena_v4.2.3.zip. `bytes` is
// the size of the file downloaded on 2026-10-21. korrid verifies it, then
// runs `game-unpack`, which extracts it and requires MegaManArena.exe and
// data.win.
export const artifacts = {
  game: {
    id: "@simonwjackson:mega-man-arena/game",
    version: "4.2.3",
    files: [
      {
        url: "https://bit.ly/mmav423a",
        sha256: "sha256:ea88237b61467a4731dc47d126e3f7565be274e52b98addcd248b0432810245e",
        bytes: 61477538,
      },
    ],
    unpack: "game-unpack",
  },
}

export const games = {
  "mega-man-arena": {
    title: "Mega Man Arena",
    releases: {
      "4.2.3": {
        hashes: [dataWin],
        artifacts: ["@simonwjackson:mega-man-arena/game"],
        file: { artifact: "@simonwjackson:mega-man-arena/game", path: "data.win" },
      },
    },
  },
}

const proton = "@korri:proton/cachyos"

// No system: the runner accepts the release by its hash.
export const runners = {
  proton: {
    id: "@simonwjackson:mega-man-arena/proton",
    program: "proton-launch",
    releases: [dataWin],
    artifacts: [proton],
  },
}

function prepareLaunch(input: PluginLaunchInput): PluginLaunchOutput {
  if (!input.contentPath) {
    throw new Error("Mega Man Arena requires a content path")
  }
  if (input.corePath !== undefined) {
    throw new Error("Mega Man Arena is a whole game and loads no core")
  }
  const overrides = input.overrides
  if (overrides?.config !== undefined) {
    throw new Error("Mega Man Arena takes no raw config override")
  }
  if (
    overrides?.settings !== undefined &&
    Object.keys(overrides.settings).length > 0
  ) {
    throw new Error("Mega Man Arena runner does not implement typed settings")
  }
  if (!input.contentPath.startsWith("/")) {
    throw new Error("Mega Man Arena requires an absolute content path")
  }
  const protonDirectory = input.artifacts[proton]
  if (!protonDirectory) {
    throw new Error(`Mega Man Arena requires the ready ${proton} artifact`)
  }
  // The content path is `data.win`; the launcher runs from its directory.
  const gameDirectory =
    input.contentPath.slice(0, input.contentPath.lastIndexOf("/")) || "/"
  // The launcher keeps Proton's Wine prefix under HOME. GameMaker writes the
  // game's settings and saves in that prefix, under AppData/Local/MegaManArena.
  const home = `${input.accountRoot}/mega-man-arena`
  return {
    command: input.program,
    args: [input.contentPath],
    env: { HOME: home, KORRI_PROTON_CACHYOS: protonDirectory },
    cwd: gameDirectory,
    directories: [home],
    envUnset: [],
  }
}

export const handlers = {
  "launch.prepare": prepareLaunch,
}
