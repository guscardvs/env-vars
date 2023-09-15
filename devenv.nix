{ pkgs, ... }:

{
  # https://devenv.sh/basics/

  # https://devenv.sh/packages/
  packages = with pkgs; [ git python39 poetry commitizen ];

  languages.python = {
      enable = true;
      package = pkgs.python39;
      poetry = {
          enable = true; 
          activate.enable = true; 
          install = {enable = true; allExtras = true;};
      };
  };


  # https://devenv.sh/languages/
  # languages.nix.enable = true;

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
