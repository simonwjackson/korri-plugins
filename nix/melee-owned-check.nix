{
  pkgs,
  package,
  korridPackage,
}:
let
  python = pkgs.python3.withPackages (p: [ p.xlib ]);
in
pkgs.writeShellApplication {
  name = "verify-melee";
  runtimeInputs = [
    pkgs.xorg.xorgserver
    pkgs.xorg.xauth
    pkgs.xdotool
    pkgs.imagemagick
    pkgs.dbus
  ];
  text = ''
    exec dbus-run-session -- ${python}/bin/python3 ${./melee-owned-check.py} \
      ${package} ${korridPackage}/bin/korrid "$@"
  '';
}
