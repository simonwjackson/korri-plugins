{
  pkgs,
  package,
  engine,
  contract,
  hostPackage,
  korridPackage,
}:
let
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
  tsconfig = pkgs.writeText "dr-mario-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/dr-mario/plugin.ts" ];
    }
  );
  probe = pkgs.writeShellScript "dr-mario-launch-probe" ''
    ${pkgs.coreutils}/bin/printf '%s\n' "$PWD" "$@"
  '';
in
pkgs.runCommand "korri-dr-mario-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.binutils
    ];
  }
  ''
      readelf -h ${engine}/bin/DrMarioRecomp > elf.txt
      grep -q '${
        if pkgs.stdenv.hostPlatform.isAarch64 then "AArch64" else "Advanced Micro Devices X86-64"
      }' elf.txt
      test -s ${engine}/share/licenses/DrMarioRecomp/DrMario-LICENSE.txt
      test -s ${engine}/share/licenses/DrMarioRecomp/NESRecomp-LICENSE.txt
      test -s ${engine}/share/licenses/DrMarioRecomp/ImGui-LICENSE.txt
    test -s ${engine}/share/licenses/DrMarioRecomp/font-NOTICE.md
      mkdir -p work/plugins/dr-mario work/contracts/generated work/nix
      cp ${package}/plugin.ts work/plugins/dr-mario/plugin.ts
      cp ${contractSource} work/contracts/generated/korrid.ts
      cp ${./dr-mario-check.ts} work/nix/dr-mario-check.ts
      cp ${tsconfig} work/tsconfig.json
      cd work
      tsc --project tsconfig.json
      bun nix/dr-mario-check.ts ${package} ${hostPackage}/bin/korri-plugin \
        ${korridPackage}/bin/korrid ${probe}
      touch "$out"
  ''
