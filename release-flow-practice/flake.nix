{
  description = "Release Flow Practice - Blue-Green & Canary Deployment with Vite + Hono";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    nix-vite-plus.url = "github:ryoppippi/nix-vite-plus";
  };

  outputs = { self, nixpkgs, flake-utils, nix-vite-plus }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShellNoCC {
          name = "release-flow-practice";

          buildInputs = with pkgs; [
            nodejs_18
            nodePackages.npm
            nodePackages.pnpm
            git
            curl
            docker
            google-cloud-sdk
          ];

          shellHook = ''
            echo "🚀 Release Flow Practice dev environment"
            echo "Node.js: $(node --version)"
            echo "npm: $(npm --version)"
            echo ""
            echo "Available commands:"
            echo "  cd api && npm install              # Install dependencies"
            echo "  npm run dev                        # Start Vite dev server"
            echo "  npm run build                      # Build for production"
            echo ""
          '';
        };
      }
    );
}
