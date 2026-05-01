{
  description = "Haskell AtCoder environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        hpkgs = pkgs.haskellPackages;
        fmt = pkgs.writeShellScriptBin "fmt" "fourmolu --mode inplace \"$@\"";
        run = pkgs.writeShellScriptBin "run" "runghc \"$@\"";
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            hpkgs.ghc
            hpkgs.haskell-language-server
            hpkgs.fourmolu
            fmt
            run
          ];
        };
      });
}
