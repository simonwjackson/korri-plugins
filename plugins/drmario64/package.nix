{ pkgs, engine }:
pkgs.runCommand "drmario64-launcher"
  {
    allowSubstitutes = false;
    preferLocalBuild = true;
  }
  ''
    mkdir -p "$out/bin"
    substitute ${./launch.py} "$out/bin/drmario64" \
      --replace-fail '@python@' '${pkgs.python3}/bin/python3' \
      --replace-fail '@engine@' '${engine}/libexec/drmario64_recomp' \
      --replace-fail '@bundle@' '${engine}/share/drmario64' \
      --replace-fail '@vulkan@' '${pkgs.vulkan-loader}/lib/libvulkan.so.1'
    chmod +x "$out/bin/drmario64"
  ''
