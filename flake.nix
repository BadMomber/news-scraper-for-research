{
  description = "Marianne Crawler – Python news article search crawler";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
        pythonPackages = python.pkgs;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            python
            pythonPackages.playwright
            pythonPackages.pyyaml
            pythonPackages.pytest
            pythonPackages.pip
          ];

          shellHook = ''
            echo "Marianne Crawler dev shell"
            echo "Python: $(python --version)"

            # Local venv for pip-only packages (e.g. claude-agent-sdk)
            if [ ! -d .venv ]; then
              python -m venv .venv --system-site-packages
              .venv/bin/pip install claude-agent-sdk
            fi
            source .venv/bin/activate
          '';
        };
      });
}
