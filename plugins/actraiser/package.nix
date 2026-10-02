{ pkgs }:
let
  engine = import ./engine.nix { inherit pkgs; };
in
pkgs.runCommand "actraiser-launcher"
  {
    allowSubstitutes = false;
    preferLocalBuild = true;
    meta = engine.meta // {
      mainProgram = "actraiser";
    };
  }
  ''
    mkdir -p "$out/bin"
    substitute ${./launcher.py} "$out/bin/actraiser" \
      --replace-fail '@python@' '${pkgs.python3}/bin/python3' \
      --replace-fail '@engine@' '${engine}/libexec/ActRaiserRecomp' \
      --replace-fail '@resources@' '${engine}/share/ActRaiserRecomp' \
      --replace-fail '@vulkan@' '${pkgs.vulkan-loader}/lib/libvulkan.so.1'
    chmod +x "$out/bin/actraiser"
  ''
