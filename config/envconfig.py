import os
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from gyver.attrs import call_init, define, info
from lazyfields import force_set, lazyfield

from config._helpers import maybe_result
from config.config import Config, EnvMapping, default_cast, default_mapping
from config.enums import Env
from config.exceptions import ConfigError
from config.interface import MISSING
from config.utils import none_is_missing, valid_path


@define
class DotFile:
    """
    Represents a configuration dotfile associated with a specific environment.

    Attributes:
        filename (Union[str, Path]): The filename or path of the dotfile.
        env (Env): The environment associated with the dotfile.
        apply_to_lower (bool): Indicates whether the dotfile should be applied to lower-priority environments.
    """

    filename: str | Path = info(order=False)
    env: Env = info(order=lambda env: env.weight)
    cascade: bool = info(default=False, order=False)

    def __ge__(self, other: "Env | DotFile | Any") -> bool:
        """
        Check if the dotfile's environment is higher or equal to the given environment.

        Args:
            env (Env): The environment to compare against.

        Returns:
            bool: True if the dotfile's environment is higher or equal to the given environment, False otherwise.
        """
        if isinstance(other, Env):
            return self.env.ordering >= other.ordering
        if isinstance(other, DotFile):
            return self.env.ordering >= other.env.ordering
        return NotImplemented


def default_rule(_: Env):
    return False


@define
class EnvConfig(Config):
    """
    Extended configuration class that supports environment-specific configurations.
    """

    mapping: EnvMapping = default_mapping
    env_var: str = "CONFIG_ENV"
    env_cast: Callable[[str], Env] = Env
    dotfiles: Sequence[DotFile] = ()
    ignore_default_rule: Callable[[Env], bool] = default_rule
    default_env: Env | None = None
    strict: bool = True

    def __init__(
        self,
        *dotfiles: DotFile,
        env_var: str = "CONFIG_ENV",
        mapping: EnvMapping = default_mapping,
        ignore_default_rule: Callable[[Env], bool] = default_rule,
        env_cast: Callable[[str], Env] = Env,
        default_env: Env | None = None,
        strict: bool = True,
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
            default_env=default_env,
            strict=strict,
        )

    def __post_init__(self):
        if self.dotfile:
            with open(self.dotfile.filename) as buffer:
                self.file_values.update(self._read_file(buffer))

    @lazyfield
    def env(self) -> Env | None:
        """
        Get the current environment from the configuration.

        Returns:
            Env | None: The current environment.
        """

        caster = none_is_missing(self.env_cast)
        if not self.strict:
            caster = maybe_result(caster).optional
        try:
            result = Config.get(
                self,
                self.env_var,
                caster,
                self.default_env,
            )
        except ConfigError:
            if not self.default_env:
                raise
            result = None
        return result or self.default_env

    @lazyfield
    def ignore_default(self) -> bool:
        """
        Determine whether to ignore default values based on the current environment.

        Returns:
            bool: True if default values should be ignored, False otherwise.
        """
        env = self.env or self.default_env
        if not env:
            return False
        return self.ignore_default_rule(env)

    def get(
        self,
        name: str,
        cast: Callable[..., Any] = default_cast,
        default: Any | type[MISSING] = MISSING,
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
    def dotfile(self) -> DotFile | None:
        """
        Get the applicable dotfile for the current environment.

        Returns:
            DotFile: The applicable dotfile, or None if no matching dotfile is found.
        """
        if dotfile_path := Config.get(
            self,
            "CONFIG_DOTFILE",
            maybe_result(valid_path).optional,
            None,
        ):
            print(dotfile_path)
            if dotfile_path.exists():
                force_set(self, "env", Env.ALWAYS)
                return DotFile(
                    filename=dotfile_path,
                    env=Env.ALWAYS,
                    cascade=True,
                )
        if not self.env:
            return None
        for dot in sorted(self.dotfiles, reverse=True):
            if not dot >= self.env:
                break
            if dot.env is not self.env and not (dot.cascade and dot >= self.env):
                continue
            if not os.path.isfile(dot.filename):
                continue
            return dot
