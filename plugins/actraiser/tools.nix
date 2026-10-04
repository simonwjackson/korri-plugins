{ pkgs }:
let
  src = import ./source.nix { inherit pkgs; };
in
{
  snesbuild = pkgs.buildGoModule {
    pname = "actraiser-snesbuild";
    version = "0-unstable-546ba47";
    inherit src;
    modRoot = "snesrecomp-go";
    subPackages = [ "cmd/snesbuild" ];
    vendorHash = null;
    doCheck = false;
  };
  builder = pkgs.buildGoModule {
    pname = "actraiser-builder";
    version = "0-unstable-546ba47";
    inherit src;
    modRoot = "installer";
    subPackages = [ "cmd/actraiser-builder" ];
    vendorHash = "sha256-7tZy8BAwCIPe6krmRf9n2gq3fCLeDKXeQ+oKGjnIyMI=";
    doCheck = false;
    # Upstream embeds retail/manual media outside its MIT license scope.
    allowSubstitutes = false;
    preferLocalBuild = true;
    meta.license = pkgs.lib.licenses.unfree;
  };
}
