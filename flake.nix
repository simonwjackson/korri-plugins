{
  description = "Personal Korri plugins, built separately from Korri OS";

  inputs = {
    korri.url = "github:korri-os/korri/d86968adbb6ff1ebf4993fdc620ca76d2b072724";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    skate3.url = "github:simonwjackson/skate-3-flake/e309e451f644eab95490c8e7c4bab9de398cda40";
    plugin-publisher.url = "github:korri-os/plugins/4f2ca37bfacdb475bf112292d62f60dcbde0eabc";
  };

  outputs =
    {
      korri,
      nixpkgs,
      flake-utils,
      skate3,
      plugin-publisher,
      ...
    }:
    import ./nix {
      inherit
        korri
        nixpkgs
        flake-utils
        skate3
        plugin-publisher
        ;
    };
}
