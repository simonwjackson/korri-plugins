{ pkgs }:
let
  python = pkgs.python3.withPackages (ps: [
    ps.numpy
    ps.pillow
  ]);
  # Only our tools enter the store. Quest inputs and outputs are runtime paths.
  scripts = pkgs.runCommand "zquest-midi-proof-scripts" { } ''
    mkdir -p "$out"
    cp ${./zquest-midi-proof.py} "$out/zquest-midi-proof.py"
    cp ${./zquest-midi-proof-test.py} "$out/zquest-midi-proof-test.py"
    cp ${./zquest-midi-proof-runtime.py} "$out/zquest-midi-proof-runtime.py"
  '';
in
{
  proof = pkgs.writeShellApplication {
    name = "zquest-midi-proof";
    runtimeInputs = [ pkgs.git ];
    text = ''
      exec ${python}/bin/python3 ${scripts}/zquest-midi-proof.py "$@"
    '';
  };
  test = pkgs.writeShellApplication {
    name = "zquest-midi-proof-test";
    runtimeInputs = [ pkgs.git ];
    text = ''
      exec ${python}/bin/python3 ${scripts}/zquest-midi-proof-test.py "$@"
    '';
  };
  runtime = pkgs.writeShellApplication {
    name = "zquest-midi-proof-runtime";
    runtimeInputs = [
      pkgs.xvfb-run
      pkgs.util-linux
      pkgs.pulseaudio
    ];
    text = ''
      exec ${python}/bin/python3 ${scripts}/zquest-midi-proof-runtime.py "$@"
    '';
  };
}
