with import <nixpkgs> {};
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
