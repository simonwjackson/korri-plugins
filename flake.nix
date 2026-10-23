{
  description = "Personal Korri plugins, built separately from Korri OS";

  inputs = {
    korri.url = "github:korri-os/korri/2c7a515b5bd28abcf366cc024753209bbb53acd6";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    signs-of-rain.url = "github:simonwjackson/signs-of-rain/a5a320681fa0688a618b0894d04de1a00b1ad537";
  };

  outputs =
    {
      korri,
      nixpkgs,
      flake-utils,
      signs-of-rain,
      ...
    }:
    import ./nix {
      inherit
        korri
        nixpkgs
        flake-utils
        signs-of-rain
        ;
    };
}
