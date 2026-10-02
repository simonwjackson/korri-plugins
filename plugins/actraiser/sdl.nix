{ pkgs }:
let
  # The repository lock has SDL 3.2.26; ActRaiser requires 3.4.0 or newer.
  # Follow its snesrecomp-go/internal/toolchain/sdl_pins.go pin locally,
  # without changing other plugins' SDL packages or the shared nixpkgs lock.
  sdl3 = pkgs.sdl3.overrideAttrs (old: {
    # SDL 3.4 moved the shared Zenity invocation out of the Wayland file.
    postPatch =
      builtins.replaceStrings
        [ "src/video/wayland/SDL_waylandmessagebox.c" ]
        [ "src/dialog/unix/SDL_zenitymessagebox.c" ]
        old.postPatch;
    buildInputs = old.buildInputs ++ [ pkgs.xorg.libXtst ];
    # testrwlock exceeded upstream's 20-second limit on the shared ARM builder.
    # Keep the test enabled; allow scheduling time without changing its workload.
    cmakeFlags =
      old.cmakeFlags
      ++ pkgs.lib.optional pkgs.stdenv.hostPlatform.isAarch64 "-DSDLTEST_TIMEOUT_MULTIPLIER=3";
    version = "3.4.12";
    src = pkgs.fetchFromGitHub {
      owner = "libsdl-org";
      repo = "SDL";
      tag = "release-3.4.12";
      hash = "sha256-b6l3HgdhqIe9LazJmLivbCJgbKPAS8S54fuB9xvgalI=";
    };
  });
in
{
  inherit sdl3;
  ttf = pkgs.sdl3-ttf.override { inherit sdl3; };
}
