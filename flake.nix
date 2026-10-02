{
  description = "Personal Korri plugins, built separately from Korri OS";

  inputs = {
    korri.url = "github:korri-os/korri/d86968adbb6ff1ebf4993fdc620ca76d2b072724";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    skate3.url = "github:simonwjackson/skate-3-flake/4e58e784407326d4da9dab5ab2b44fd32eb03c22";
  };

  outputs =
    {
      korri,
      nixpkgs,
      flake-utils,
      skate3,
      ...
    }:
    import ./nix {
      inherit
        korri
        nixpkgs
        flake-utils
        skate3
        ;
    };
}
