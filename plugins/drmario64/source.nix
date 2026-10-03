{ pkgs }:
pkgs.fetchgit {
  name = "drmario64_recomp_plus-af91e3b";
  url = "https://github.com/theboy181/drmario64_recomp_plus";
  rev = "af91e3bf56b1ffc329ff4327fdc2380515463de7";
  hash = "sha256-ux+IAZWvLtyiTf8s6vdwm/wPuJxbwGhFvlSy2A0cIQk=";
  fetchSubmodules = true;
  # Upstream's public gitlinks use SSH. Fetch reproducibly without user keys.
  gitConfigFile = ./fetch.gitconfig;
}
