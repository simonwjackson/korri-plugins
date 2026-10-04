{
  description = "Personal Korri plugins, built separately from Korri OS";

  inputs = {
    korri.url = "github:korri-os/korri/d86968adbb6ff1ebf4993fdc620ca76d2b072724";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    skate3.url = "github:simonwjackson/skate-3-flake/4e58e784407326d4da9dab5ab2b44fd32eb03c22";
    signs-of-rain.url = "github:simonwjackson/signs-of-rain/a5a320681fa0688a618b0894d04de1a00b1ad537";
    # Mod source for the Nocturne plugin (fork of birabittoh/NocturneRecomp-Mods).
    nocturne-encore = {
      url = "github:simonwjackson/nocturne-encore/eb7045d04f3f2435ffd902a3cbb65b21e66a6b16";
      flake = false;
    };
  };

  outputs =
    {
      korri,
      nixpkgs,
      flake-utils,
      skate3,
      signs-of-rain,
      nocturne-encore,
      ...
    }:
    import ./nix {
      inherit
        korri
        nixpkgs
        flake-utils
        skate3
        signs-of-rain
        nocturne-encore
        ;
    };
}
