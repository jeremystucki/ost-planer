{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/48a50c96e36c3f47e8667998923993f6ba1602db.tar.gz") {}}:

with pkgs;
let
  pythonEnv = python3.withPackages (ps: [
    ps.requests
    ps.lxml
  ]);
in mkShell {
  packages = [
    pythonEnv
  ];
}
