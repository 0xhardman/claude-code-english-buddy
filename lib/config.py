"""
Configuration management for English Buddy.
Handles loading and saving of user configuration.
"""

import json
from pathlib import Path
from typing import Any


# Default configuration values
DEFAULT_CONFIG = {
    "data_dir": "~/.english-buddy",
    "obsidian_dir": "~/obsidian/learning/english",
    "api_timeout": 15,
    "retry_queue_max": 50,
    "notification_enabled": True
}

# Config file location
CONFIG_PATH = Path.home() / ".english-buddy" / "config.json"

# Cached config
_config_cache: dict = None


def _expand_path(path: str) -> Path:
    """Expand ~ in path and return Path object."""
    return Path(path).expanduser()


def load_config() -> dict:
    """
    Load configuration from file or create with defaults.

    Returns:
        Configuration dictionary with all settings.
    """
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    config = DEFAULT_CONFIG.copy()

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                user_config = json.load(f)
                # Merge user config with defaults
                config.update(user_config)
        except (json.JSONDecodeError, IOError):
            pass

    _config_cache = config
    return config


def save_config(config: dict) -> bool:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary to save.

    Returns:
        True if saved successfully, False otherwise.
    """
    global _config_cache

    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        _config_cache = config
        return True
    except IOError:
        return False


def get_config() -> dict:
    """
    Get configuration, creating default config file if needed.

    Returns:
        Configuration dictionary.
    """
    config = load_config()

    # Create config file with defaults if it doesn't exist
    if not CONFIG_PATH.exists():
        save_config(config)

    return config


def get(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.

    Args:
        key: Configuration key to retrieve.
        default: Default value if key not found.

    Returns:
        Configuration value or default.
    """
    config = get_config()
    return config.get(key, default)


def get_data_dir() -> Path:
    """Get the data directory path."""
    return _expand_path(get("data_dir", DEFAULT_CONFIG["data_dir"]))


def get_obsidian_dir() -> Path:
    """Get the Obsidian directory path."""
    return _expand_path(get("obsidian_dir", DEFAULT_CONFIG["obsidian_dir"]))


def get_api_timeout() -> int:
    """Get the API timeout in seconds."""
    return get("api_timeout", DEFAULT_CONFIG["api_timeout"])


def get_retry_queue_max() -> int:
    """Get the maximum number of items in retry queue."""
    return get("retry_queue_max", DEFAULT_CONFIG["retry_queue_max"])


def is_notification_enabled() -> bool:
    """Check if notifications are enabled."""
    return get("notification_enabled", DEFAULT_CONFIG["notification_enabled"])


def clear_cache():
    """Clear the cached configuration."""
    global _config_cache
    _config_cache = None


if __name__ == "__main__":
    # Test configuration
    print(f"Config path: {CONFIG_PATH}")
    config = get_config()
    print(f"Configuration: {json.dumps(config, indent=2)}")
    print(f"Data dir: {get_data_dir()}")
    print(f"Obsidian dir: {get_obsidian_dir()}")
