"""
Shared configuration system.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class BaseConfig:
    """Base configuration class."""

    def __init__(self, default_config: Dict[str, Any] = None):
        """Initialize base configuration.

        Args:
            default_config: Default configuration values
        """
        self._config = default_config or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value

    def delete(self, key: str) -> None:
        """Delete a configuration value.

        Args:
            key: Configuration key
        """
        if key in self._config:
            del self._config[key]

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.

        Returns:
            Dictionary of all configuration values
        """
        return self._config.copy()

    def clear(self) -> None:
        """Clear all configuration values."""
        self._config = {}

    def validate(self) -> bool:
        """Override in subclasses for validation logic."""
        return True

    def get_env_or_config(
        self, key: str, env_var: Optional[str] = None
    ) -> Optional[str]:
        """Get value from environment variable or config.

        Args:
            key: Configuration key
            env_var: Environment variable name (defaults to key.upper())
        """
        env_var = env_var or key.upper()
        return self._config.get(key) or os.getenv(env_var)


class Config(BaseConfig):
    """Configuration manager for devtools."""

    def __init__(self):
        """Initialize configuration."""
        super().__init__()
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.yaml"
        self._ensure_config_dir()
        self._load_config()

    def _get_config_dir(self) -> Path:
        """Get the configuration directory.

        Returns:
            Path to config directory
        """
        return Path.home() / ".devtools"

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}

    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        super().set(key, value)
        self._save_config()

    def delete(self, key: str) -> None:
        """Delete a configuration value.

        Args:
            key: Configuration key
        """
        super().delete(key)
        self._save_config()

    def clear(self) -> None:
        """Clear all configuration values."""
        super().clear()
        self._save_config()
