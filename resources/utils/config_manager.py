"""Reads resources/config/config_<env>.ini, like the real ConfigManager (CONFIG_SOURCE=local): credentials never in code."""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UserCredentials:
    default_email: str
    default_password: str


class ConfigManager:
    _config_dir = Path(__file__).resolve().parent.parent / "config"

    def __init__(self, environment: str = "qa") -> None:
        self._config = configparser.ConfigParser()
        config_path = self._config_dir / f"config_{environment}.ini"
        if not self._config.read(config_path):
            raise FileNotFoundError(f"No config file at {config_path}")
        self._environment = environment

    def user_credentials(self) -> UserCredentials:
        credentials_section = self._config[self._environment]
        return UserCredentials(default_email=credentials_section["default_email"], default_password=credentials_section["default_password"])
