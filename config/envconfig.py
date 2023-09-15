import os
from pathlib import Path
from typing import Any, Callable, Sequence, Union, Optional

from gyver.attrs import call_init, define, info

from lazyfields import lazyfield, force_set
from config.config import Config, EnvMapping, default_mapping
from config.enums import Env
from config.interface import MISSING


@define
class DotFile:
    """
    Represents a configuration dotfile associated with a specific environment.

    Attributes:
        filename (Union[str, Path]): The filename or path of the dotfile.
        env (Env): The environment associated with the dotfile.
        apply_to_lower (bool): Indicates whether the dotfile should be applied to lower-priority environments.
    """

    filename: Union[str, Path] = info(order=False)
    env: Env = info(order=lambda env: env.weight)
    apply_to_lower: bool = info(default=False, order=False)

    def is_higher(self, env: Env) -> bool:
        """
        Check if the dotfile's environment is higher or equal to the given environment.

        Args:
            env (Env): The environment to compare against.

        Returns:
            bool: True if the dotfile's environment is higher or equal to the given environment, False otherwise.
        """
        return self.env.weight >= env.weight


def default_rule(_: Env):
    return False


@define
class EnvConfig(Config):
    """
    Extended configuration class that supports environment-specific configurations.
    """
    mapping: EnvMapping = default_mapping
    env_var: str = "CONFIG_ENV"
    env_cast: Callable[[str], Env] = Env.new
    dotfiles: Sequence[DotFile] = ()
    ignore_default_rule: Callable[[Env], bool] = default_rule

    def __init__(
        self,
        *dotfiles: DotFile,
        env_var: str = "CONFIG_ENV",
        mapping: EnvMapping = default_mapping,
        ignore_default_rule: Callable[[Env], bool] = default_rule,
        env_cast: Callable[[str], Env] = Env.new,
    ) -> None:
        """
        Initialize the EnvConfig instance.

        Args:
            *dotfiles (DotFile): One or more DotFile instances representing configuration dotfiles.
            env_var (str): The name of the environment variable to determine the current environment.
            mapping (EnvMapping): An environment mapping to use for configuration values.
            ignore_default_rule (Callable[[Env], bool]): A callable to determine whether to ignore default values.
            env_cast (Callable[[str], Env]): A callable to cast the environment name to an Env enum value.
        """
        call_init(
            self,
            env_var=env_var,
            mapping=mapping,
            dotfiles=dotfiles,
            ignore_default_rule=ignore_default_rule,
            env_cast=env_cast,
        )

    def __post_init__(self):
        if self.dotfile:
            force_set(self, "file_values", dict(self._read_file(self.dotfile.filename)))

    @lazyfield
    def env(self):
        """
        Get the current environment from the configuration.

        Returns:
            Env: The current environment.
        """
        return Config.get(self, self.env_var, self.env_cast)

    @lazyfield
    def ignore_default(self):
        """
        Determine whether to ignore default values based on the current environment.

        Returns:
            bool: True if default values should be ignored, False otherwise.
        """
        return self.ignore_default_rule(self.env)

    def get(
        self,
        name: str,
        cast: Callable[..., Any] = ...,
        default: Union[Any, type[MISSING]] = ...,
    ) -> Any:
        """
        Get a configuration value, with the option to cast and provide a default value.

        Args:
            name (str): The name of the configuration value.
            cast (Callable[..., Any]): A callable to cast the value.
            default (Union[Any, type[MISSING]]): The default value if the configuration is not found.

        Returns:
            Any: The configuration value.
        """
        default = MISSING if self.ignore_default else default
        return Config.get(self, name, cast, default)

    @lazyfield
    def dotfile(self) -> Optional[DotFile]:
        """
        Get the applicable dotfile for the current environment.

        Returns:
            DotFile: The applicable dotfile, or None if no matching dotfile is found.
        """

        for dot in sorted(self.dotfiles, reverse=True):
            if not dot.is_higher(self.env):
                break
            if dot.env is not self.env and not (
                dot.apply_to_lower and dot.is_higher(self.env)
            ):
                continue
            if not os.path.isfile(dot.filename):
                continue
            return dot
