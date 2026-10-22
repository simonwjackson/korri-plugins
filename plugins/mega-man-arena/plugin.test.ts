import { describe, expect, test } from "bun:test"
import { artifacts, games, handlers, runners } from "./plugin"

const dataWin =
  "sha256:1c9b5c7787f7286fd515af0bb16c1fa79349d9e00c32c61b75cedd0f7cd9ca4f"
const gameDirectory = "/var/lib/korri/cache/mega-man-arena/game/4.2.3"
const protonDirectory = "/var/lib/korri/cache/proton/cachyos/11.0-20260601-slr-arm64"

const launchInput = () => ({
  runnerId: "@simonwjackson:mega-man-arena/proton",
  program: "/nix/store/mma/bin/mega-man-arena-proton",
  contentPath: `${gameDirectory}/data.win`,
  accountRoot: "/var/lib/korri/accounts/a",
  cacheRoot: "/var/lib/korri/cache",
  files: {
    "proton-launch": "/nix/store/mma/bin/mega-man-arena-proton",
    "game-unpack": "/nix/store/mma/bin/mega-man-arena-unpack",
  },
  artifacts: { "@korri:proton/cachyos": protonDirectory } as Record<string, string>,
})

describe("Mega Man Arena declaration", () => {
  test("the release is data.win inside the game artifact, by its hash", () => {
    const release = games["mega-man-arena"].releases["4.2.3"]
    expect(release).toEqual({
      hashes: [dataWin],
      artifacts: [artifacts.game.id],
      file: { artifact: artifacts.game.id, path: "data.win" },
    })
  })

  test("the runner accepts that release and needs @korri:proton's build", () => {
    expect(runners.proton).toEqual({
      id: "@simonwjackson:mega-man-arena/proton",
      program: "proton-launch",
      releases: [dataWin],
      artifacts: ["@korri:proton/cachyos"],
    })
  })
})

describe("Mega Man Arena launch", () => {
  test("runs the launcher on data.win from the game directory with Proton and its home", () => {
    const input = launchInput()
    expect(handlers["launch.prepare"](input)).toEqual({
      command: input.program,
      args: [`${gameDirectory}/data.win`],
      env: {
        HOME: "/var/lib/korri/accounts/a/mega-man-arena",
        KORRI_PROTON_CACHYOS: protonDirectory,
      },
      cwd: gameDirectory,
      directories: ["/var/lib/korri/accounts/a/mega-man-arena"],
      envUnset: [],
    })
  })

  test("refuses a launch korrid cannot supply", () => {
    const refused: [string, Record<string, unknown>][] = [
      ["requires a content path", { contentPath: undefined }],
      ["requires an absolute content path", { contentPath: "data.win" }],
      ["loads no core", { corePath: "/nix/store/core.so" }],
      ["no raw config override", { overrides: { config: { append: [] } } }],
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
