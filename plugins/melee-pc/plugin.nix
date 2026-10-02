{ meleePackage }:
{
  packages.melee-pc = meleePackage;
  files.melee-pc = "${meleePackage}/bin/melee-pc";
}
