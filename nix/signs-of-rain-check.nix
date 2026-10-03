{
  pkgs,
  package,
  signsOfRainPackage,
  contract,
  hostPackage,
  korridPackage,
}:
let
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
  recordArguments = pkgs.writeScript "record-signs-of-rain-launch" ''
    #!${pkgs.python3}/bin/python3
    import json, os, sys
    names = ["HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME",
             "SDL_GAMECONTROLLERCONFIG", "SDL_JOYSTICK_HIDAPI", "XDG_RUNTIME_DIR",
             "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "PULSE_SERVER"]
    print(json.dumps({"args": sys.argv[1:], "cwd": os.getcwd(),
                      "env": {name: os.environ.get(name) for name in names}}))
  '';
in
pkgs.runCommand "korri-signs-of-rain-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
    ];
  }
  ''
    mkdir -p work/plugins/signs-of-rain work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/signs-of-rain/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./signs-of-rain-check.ts} work/nix/signs-of-rain-check.ts
    cd work
    tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext \
      --moduleResolution Bundler plugins/signs-of-rain/plugin.ts
    bun nix/signs-of-rain-check.ts ${package} ${signsOfRainPackage} \
      ${hostPackage}/bin/korri-plugin ${korridPackage}/bin/korrid ${recordArguments}
    touch "$out"
  ''
