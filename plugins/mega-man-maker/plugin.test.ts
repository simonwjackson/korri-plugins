import { describe, expect, test } from "bun:test"
import { artifacts, games, handlers, runners } from "./plugin"

const dataWin =
  "sha256:888d7eee4442e3105ba28fe05d126d26901ef98e82380a2c0096ac4d6953dca4"
const gameDirectory = "/var/lib/korri/cache/mega-man-maker/game/1.10.4.2"
const proton = "/var/lib/korri/cache/proton/cachyos/11.0-20260601-slr-arm64"

const launchInput = () => ({
  runnerId: "@simonwjackson:mega-man-maker/proton",
  program: "/nix/store/mmm/bin/mega-man-maker-proton",
  contentPath: `${gameDirectory}/data.win`,
  accountRoot: "/var/lib/korri/accounts/a",
  cacheRoot: "/var/lib/korri/cache",
  files: {
    "proton-launch": "/nix/store/mmm/bin/mega-man-maker-proton",
    "game-unpack": "/nix/store/mmm/bin/mega-man-maker-unpack",
  },
  artifacts: { "@korri:proton/cachyos": proton },
})

describe("Mega Man Maker declaration", () => {
  test("the game artifact is the pinned public ZIP", () => {
    expect(artifacts.game).toEqual({
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
    })
  })

  test("the release is data.win inside the game artifact, by its hash", () => {
    expect(games["mega-man-maker"].releases["1.10.4.2"]).toEqual({
      hashes: [dataWin],
      artifacts: [artifacts.game.id],
      file: { artifact: artifacts.game.id, path: "data.win" },
    })
  })

  test("the runner accepts that release and needs only Proton", () => {
    expect(runners.proton).toEqual({
      id: "@simonwjackson:mega-man-maker/proton",
      program: "proton-launch",
      releases: [dataWin],
      artifacts: ["@korri:proton/cachyos"],
    })
  })
})

describe("Mega Man Maker launch", () => {
  test("runs the launcher on data.win from the game directory with Proton and its home", () => {
    const input = launchInput()
    expect(handlers["launch.prepare"](input)).toEqual({
      command: input.program,
      args: [`${gameDirectory}/data.win`],
      env: {
        HOME: "/var/lib/korri/accounts/a/mega-man-maker",
        KORRI_PROTON: proton,
      },
      cwd: gameDirectory,
      directories: ["/var/lib/korri/accounts/a/mega-man-maker"],
      envUnset: [],
    })
  })

  test("refuses a launch korrid cannot supply", () => {
    const refused: [string, Record<string, unknown>][] = [
      ["requires a content path", { contentPath: undefined }],
      ["requires an absolute content path", { contentPath: "data.win" }],
      ["loads no core", { corePath: "/nix/store/core.so" }],
      ["no raw config override", { overrides: { config: { append: "x" } } }],
      ["does not implement typed settings", { overrides: { settings: { scale: 2 } } }],
      ["requires the ready @korri:proton/cachyos artifact", { artifacts: {} }],
    ]
    for (const [message, change] of refused) {
      expect(() => handlers["launch.prepare"]({ ...launchInput(), ...change } as never)).toThrow(
        message,
      )
    }
  })

  test("accepts empty overrides", () => {
    const plan = handlers["launch.prepare"]({ ...launchInput(), overrides: { settings: {} } })
    expect(plan.cwd).toBe(gameDirectory)
  })
})
