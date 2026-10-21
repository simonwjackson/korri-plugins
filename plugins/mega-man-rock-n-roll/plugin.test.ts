import { describe, expect, test } from "bun:test"
import { artifacts, games, handlers, runners } from "./plugin"

const dataPck =
  "sha256:eb6fc0155b1996c5fcc5b42d6ec3f9c3aea4ba1e9aca5389cd7da8070310bd41"
const gameDirectory = "/var/lib/korri/cache/mega-man-rock-n-roll/game/1.3"

const launchInput = () => ({
  runnerId: "@simonwjackson:mega-man-rock-n-roll/godot",
  program: "/nix/store/mmrnr/bin/mega-man-rock-n-roll-godot",
  contentPath: `${gameDirectory}/data.pck`,
  accountRoot: "/var/lib/korri/accounts/a",
  cacheRoot: "/var/lib/korri/cache",
  files: {
    "godot-launch": "/nix/store/mmrnr/bin/mega-man-rock-n-roll-godot",
    "game-unpack": "/nix/store/mmrnr/bin/mega-man-rock-n-roll-unpack",
  },
  artifacts: {},
})

describe("Mega Man Rock N Roll declaration", () => {
  test("the release is data.pck inside the game artifact, by its hash", () => {
    const release = games["mega-man-rock-n-roll"].releases["1.3"]
    expect(release).toEqual({
      hashes: [dataPck],
      artifacts: [artifacts.game.id],
      file: { artifact: artifacts.game.id, path: "data.pck" },
    })
  })

  test("the runner accepts that release and needs no other artifact", () => {
    expect(runners.godot).toEqual({
      id: "@simonwjackson:mega-man-rock-n-roll/godot",
      program: "godot-launch",
      releases: [dataPck],
    })
  })
})

describe("Mega Man Rock N Roll launch", () => {
  test("runs the launcher on data.pck from the game directory with its home", () => {
    const input = launchInput()
    expect(handlers["launch.prepare"](input)).toEqual({
      command: input.program,
      args: [`${gameDirectory}/data.pck`],
      env: { HOME: "/var/lib/korri/accounts/a/mega-man-rock-n-roll" },
      cwd: gameDirectory,
      directories: ["/var/lib/korri/accounts/a/mega-man-rock-n-roll"],
      envUnset: [],
    })
  })

  test("refuses a launch korrid cannot supply", () => {
    const refused: [string, Record<string, unknown>][] = [
      ["requires a content path", { contentPath: undefined }],
      ["requires an absolute content path", { contentPath: "data.pck" }],
      ["loads no core", { corePath: "/nix/store/core.so" }],
      ["no raw config override", { overrides: { config: { append: [] } } }],
      ["does not implement typed settings", { overrides: { settings: { scale: 2 } } }],
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
