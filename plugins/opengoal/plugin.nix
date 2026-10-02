{ opengoalRuntime }:
{
  packages.opengoal = opengoalRuntime;
  files.opengoal = "${opengoalRuntime}/bin/gk";
}
