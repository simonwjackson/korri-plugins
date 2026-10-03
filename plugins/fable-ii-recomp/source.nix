# Public handwritten sources only. The SDK fetch includes every exact recursive
# gitlink (including SIMDe's munit), but strips Git metadata before the build.
{ pkgs }:
{
  game = pkgs.fetchFromGitHub {
    owner = "Oery";
    repo = "fable-ii-recomp";
    rev = "f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092";
    hash = "sha256-dYbmQJJ4cxdghyk3lBf5GYcn/BfzGclkb+wSdAqmOA0=";
  };

  sdk = pkgs.fetchgit {
    name = "rexglue-sdk-c94f5eb";
    url = "https://github.com/rexglue/rexglue-sdk";
    rev = "c94f5ebdcb3c9d1a460ca48e04f9758448f8d518";
    fetchSubmodules = true;
    hash = "sha256-XudNtyigfVgMs8P6enLSpztGRKH84yVT0XYYs2PrfjE=";
  };
}
