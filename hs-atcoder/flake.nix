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
        atcoder-cli = pkgs.buildNpmPackage {
          pname = "atcoder-cli";
          version = "2.2.0";
          src = pkgs.fetchFromGitHub {
            owner = "Tatamo";
            repo  = "atcoder-cli";
            rev   = "v2.2.0";
            hash  = "sha256-7pbCTgWt+khKVyMV03HanvuOX2uAC0PL9OLmqly7IWE=";
          };
          npmDepsHash = "sha256-ufG7Fq5D2SOzUp8KYRYUB5tYJYoADuhK+2zDfG0a3ks=";
          NODE_OPTIONS = "--openssl-legacy-provider";
        };
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            hpkgs.ghc
            hpkgs.haskell-language-server
            hpkgs.fourmolu
            fmt
            run
            atcoder-cli
          ];
        };
      });
}
