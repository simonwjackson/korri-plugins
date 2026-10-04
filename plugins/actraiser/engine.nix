{ pkgs }:
let
  src = import ./source.nix { inherit pkgs; };
  tools = import ./tools.nix { inherit pkgs; };
  sdl = import ./sdl.nix { inherit pkgs; };
  # Same requireFile boundary as skate-3-flake/package-source.nix. This exact
  # headerless input is specified by upstream and measured from the owned ROM.
  rom = pkgs.requireFile {
    name = "ar.sfc";
    sha256 = "b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0";
    message = ''
      ActRaiser needs your owned, headerless USA ROM as ar.sfc (1,048,576 bytes).
      On a private build machine, use: nix-store --add-fixed sha256 /path/to/ar.sfc
      The ROM and build outputs must not enter public caches or release assets.
      The local Nix store is readable by other local accounts.
    '';
  };
in
pkgs.stdenv.mkDerivation {
  pname = "actraiser";
  version = "0-unstable-546ba47";
  inherit src;
  nativeBuildInputs = [
    pkgs.cmake
    pkgs.ninja
    pkgs.pkg-config
    pkgs.python3
  ];
  buildInputs = [
    sdl.sdl3
    sdl.ttf
  ];
  preConfigure = ''
    ${tools.builder}/bin/actraiser-builder native-source --root . --rom ${rom}
    ${tools.snesbuild}/bin/snesbuild regen --root . --rom ${rom} --allow-stubs
  '';
  cmakeFlags = [
    "-DCMAKE_BUILD_TYPE=Release"
    "-DBUILD_TESTING=ON"
    "-DACTRAISER_ENABLE_RUN_DIR_BY_DEFAULT=OFF"
    "-DSNESRECOMP_ENABLE_TRACE_RECORDER=OFF"
    "-DSNESRECOMP_ENABLE_TRACE=OFF"
    "-DSNESRECOMP_WATCHDOG=OFF"
    # Build the helper separately with pinned Go modules. CMake otherwise
    # invokes Go with a network-dependent module cache inside the C build.
    "-DACTRAISER_GO_EXECUTABLE=ACTRAISER_GO_EXECUTABLE-NOTFOUND"
  ];
  # Build and run only the upstream Auto canvas, presentation and capture
  # regression targets, not the whole upstream suite. Their binaries stay in
  # the private build directory.
  ninjaFlags = [
    "ActRaiserRecomp"
    "actraiser_ui_catalog_test"
    "actraiser_hud_layout_test"
    "actraiser_action_bg_test"
    "actraiser_action_effect_render_test"
    "actraiser_present_hud_test"
    "actraiser_present_action_effects_test"
    "actraiser_diorama_camera_test"
    "actraiser_diorama_projection_test"
    "actraiser_settings_test"
    "actraiser_settings_overlay_test"
    "actraiser_auto_canvas_test"
    "actraiser_action_sprites_test"
    "actraiser_dev_tools_capture_trace_test"
    "actraiser_scene_inspector_test"
    "actraiser_present_world_nav_test"
    "actraiser_present_sim3d_project_test"
    "actraiser_present_frame_order_test"
    "actraiser_ppu_render_pipeline_test"
  ];
  doCheck = true;
  checkPhase = ''
    runHook preCheck
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ctest --output-on-failure \
      -R '^actraiser_(ui_catalog|hud_layout|action_bg|action_effect_render|present_hud|present_action_effects|diorama_camera|diorama_projection|settings|settings_overlay|auto_canvas|action_sprites_(activation|priority|empty)|dev_tools_capture_trace|scene_inspector|present_world_nav|present_sim3d_project|present_frame_order|ppu_render_pipeline|runner_private_boundary|render_backend_boundary|render_backend_boundary_negative)$'
    runHook postCheck
  '';
  installPhase = ''
    runHook preInstall
    install -Dm755 ActRaiserRecomp "$out/libexec/ActRaiserRecomp"
    ln -s ${tools.builder}/bin/actraiser-builder "$out/libexec/actraiser-builder"
    resources="$out/share/ActRaiserRecomp"
    mkdir -p "$resources/defaults/game-assets" "$resources/game-assets"
    cp ../installer/packaging/templates/config.ini ../diorama-layers.ini "$resources/defaults/"
    cp ../installer/internal/builder/assets/manifest.ini "$resources/defaults/game-assets/"
    cp -r ../game-assets/fonts "$resources/game-assets/"
    cp -r ../game-assets/languages "$resources/game-assets/"
    install -Dm644 ../LICENSE "$resources/licenses/ActRaiser.txt"
    install -Dm644 ../snesrecomp-go/THIRD_PARTY_NOTICES.md "$resources/licenses/runner-notices.md"
    install -Dm644 ../snesrecomp-go/runtime/LICENSE "$resources/licenses/runner-MIT.txt"
    install -Dm644 ../snesrecomp-go/runtime/licenses/Snaggletooth-LICENSE.txt "$resources/licenses/Snaggletooth.txt"
    install -Dm644 ../third_party/sheenbidi/LICENSE "$resources/licenses/SheenBidi.txt"
    runHook postInstall
  '';
  allowSubstitutes = false;
  preferLocalBuild = true;
  meta = {
    description = "Private native ActRaiser build from an owned USA ROM";
    license = pkgs.lib.licenses.unfree;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
  };
}
