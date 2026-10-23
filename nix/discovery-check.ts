// Run with Node 24: node nix/discovery-check.ts
// No native packages, owned data, display, or korrid admission are needed.
import assert from "node:assert/strict"
import {
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { pathToFileURL } from "node:url"
import { test } from "node:test"

const plugins = new URL("../plugins/", import.meta.url)
const expectedContent = {
  "2ship": { n64: ["n64", "z64", "v64"] },
  "super-mario-world": { snes: ["smc", "sfc"] },
  "zquest-classic": { "zelda-classic": ["qst"] },
}

for (const directory of readdirSync(plugins)) {
  const source = new URL(`${directory}/plugin.ts`, plugins)
  const template = new URL(`${directory}/plugin.ts.in`, plugins)
  test(`${directory}: current exports only`, async () => {
    // Signs of Rain is generated from a packaged PCK hash. Check its source
    // template here; the package check still verifies the actual PCK bytes.
    const text = readFileSync(
      directory === "signs-of-rain" ? template : source,
      "utf8",
    )
    assert.doesNotMatch(text, /export const (discovery|sessionControls)\b/)
    if (directory !== "signs-of-rain") {
      const plugin = await import(source.href)
      assert.equal("discovery" in plugin, false)
      assert.equal("sessionControls" in plugin, false)
    }
  })
}

for (const [directory, systems] of Object.entries(expectedContent)) {
  test(`${directory}: system content keeps its file extensions`, async () => {
    const plugin = await import(new URL(`${directory}/plugin.ts`, plugins).href)
    assert.deepEqual(Object.keys(plugin.systems), Object.keys(systems))
    for (const [system, extensions] of Object.entries(systems)) {
      assert.equal(plugin.systems[system].id, system)
      assert.deepEqual(plugin.systems[system].content, { extensions })
    }
  })
}

const originals = {
  "2ship": [
    "majoras-mask",
    "The Legend of Zelda: Majora's Mask",
    "2ship",
    "n64",
  ],
  "super-mario-world": [
    "super-mario-world",
    "Super Mario World",
    "smw",
    "snes",
  ],
} as const

for (const [directory, [key, title, runner, system]] of Object.entries(
  originals,
)) {
  test(`${directory}: measured original hashes join one declared game`, async () => {
    const plugin = await import(new URL(`${directory}/plugin.ts`, plugins).href)
    assert.deepEqual(plugin.games, {
      [key]: {
        title,
        releases: {
          original: {
            ...(system === undefined ? {} : { system }),
            hashes: plugin.runners[runner].releases,
          },
        },
      },
    })
  })
}

for (const [directory, key, title, runner, installation] of [
  ["fallout1-ce", "fallout1", "Fallout", "fallout-ce", "fallout-ce"],
  ["fallout2-ce", "fallout2", "Fallout 2", "fallout2-ce", "fallout2-ce"],
]) {
  test(`${directory}: installed MASTER.DAT is declared without a system`, async () => {
    const plugin = await import(new URL(`${directory}/plugin.ts`, plugins).href)
    assert.equal(plugin.systems, undefined, "No invented prepared-game system")
    assert.deepEqual(plugin.games, {
      [key]: {
        title,
        releases: {
          prepared: {
            hashes: plugin.runners[runner].releases,
            file: `${installation}/MASTER.DAT`,
          },
        },
      },
    })
    assert.deepEqual(
      plugin.handlers["launch.prepare"]({
        runnerId: plugin.runners[runner].id,
        program: "/engine",
        contentPath: `/accounts/default/${plugin.games[key].releases.prepared.file}`,
        accountRoot: "/accounts/default",
        cacheRoot: "/cache",
        files: {},
        artifacts: {},
      }),
      { command: "/engine", args: [], cwd: `/accounts/default/${installation}` },
    )
  })
}

// Measured GAME.CGO hashes, also checked against the native package by
// opengoal-check.ts. Keep target exclusion testable without building a runtime.
const opengoalHashes = {
  "x86_64-linux": {
    jak1: [
      "sha256:3cda4bc7f551a51d2fa9c4d5949549237ea846ce4851437403dbe91548a52807",
    ],
    jak2: [
      "sha256:6a673c9cf1e7aee115e82be459b1348fd1981fef49086569aae67a2a64c4cc14",
      "sha256:a8c829303340a1c572252e408f0730e2495d84505cdfcd94b3e34167fd9a6ad8",
    ],
    jak3: [
      "sha256:442becdbf74aa11fe046e76c243b7ce0122d924593f6e20682ff06ae5dacd4f5",
    ],
  },
  "aarch64-linux": {
    jak1: [
      "sha256:6c838d001de990273431c2e2bdc900052a6637e91d3c64bb625e5965a0f0084b",
    ],
    jak2: [
      "sha256:d877c28cfa48074a7a6e02b81c67c38b70f27f8b0be9922642cf12c13bf055f6",
      "sha256:65fe7daca4265a29e6308d1c5f089c488a1ce67ce1360dcc41a0142215de1b03",
    ],
    jak3: [
      "sha256:7280fce6003568d10b36cc26cb7cac13a545959e44353b7bbe1bd1a73eadb58a",
    ],
  },
}

for (const [system, expectedHashes] of Object.entries(opengoalHashes)) {
  test(`OpenGOAL ${system}: three games, Renegade shares Jak II`, async () => {
    const root = mkdtempSync(join(tmpdir(), "opengoal-discovery-check-"))
    try {
      const source = readFileSync(
        new URL("opengoal/plugin.ts", plugins),
        "utf8",
      ).replace('const system = "x86_64-linux"', `const system = "${system}"`)
      const path = join(root, "plugin.ts")
      writeFileSync(path, source)
      const plugin = await import(pathToFileURL(path).href)
      assert.equal(
        plugin.systems,
        undefined,
        "No invented prepared-game system",
      )
      assert.deepEqual(Object.keys(plugin.games), ["jak1", "jak2", "jak3"])
      for (const [game, title] of [
        ["jak1", "Jak and Daxter: The Precursor Legacy"],
        ["jak2", "Jak II"],
        ["jak3", "Jak 3"],
      ] as const) {
        const runner = plugin.runners[game]
        assert.deepEqual(runner.releases, expectedHashes[game])
        const prepared = {
          hashes: [runner.releases[0]],
          file: `opengoal/${game}/out/${game}/iso/GAME.CGO`,
        }
        const renegade = {
          hashes: [runner.releases[1]],
          file: "opengoal/jak2-renegade/out/jak2/iso/GAME.CGO",
        }
        assert.deepEqual(plugin.games[game], {
          title,
          releases: { prepared, ...(game === "jak2" ? { renegade } : {}) },
        })
        for (const release of Object.values(
          plugin.games[game].releases,
        ) as Array<typeof prepared>) {
          const contentPath = `/accounts/default/${release.file}`
          const data = contentPath.slice(0, -`/out/${game}/iso/GAME.CGO`.length)
          assert.deepEqual(
            plugin.handlers["launch.prepare"]({
              runnerId: runner.id,
              program: "/gk",
              contentPath,
              accountRoot: "/accounts/default",
              cacheRoot: "/cache",
              files: {},
              artifacts: {},
            }),
            { command: "/gk", args: ["--game", game, "--proj-path", data] },
          )
        }
      }
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
}
