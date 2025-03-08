"""
Configuration module for Blood Bond Enhanced Tools.

This module provides a centralized configuration management system for
the application, handling default values, user configurations, and 
persistent settings storage.
"""

import os
import json
import logging
import copy
from typing import Dict, Any, Optional, List, Union
from pathlib import Path


class Config:
    """
    Configuration management for the Blood Bond Enhanced Tools.
    
    This class handles loading, saving, and accessing configuration settings
    for the application. It supports default values, user overrides, and
    persistent storage.
    
    Attributes:
        config_file (Path): Path to the configuration file
        data (Dict): Dictionary containing configuration values
        defaults (Dict): Dictionary containing default configuration values
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration system.
        
        Args:
            config_file: Optional path to configuration file.
                         If None, uses default location.
        """
        self.logger = logging.getLogger(__name__)
        
        # Set up config file path
        if config_file is None:
            # Default location for config file
            app_dir = self._get_app_directory()
            self.config_file = app_dir / "config.json"
        else:
            self.config_file = Path(config_file)
        
        # Define default configuration values
        self.defaults = {
            "app": {
                "name": "Blood Bond Enhanced Tools",
                "version": "1.0.0",
                "theme": "dark",
                "debug": False,
                "locale": "en-US"
            },
            "paths": {
                "data_dir": str(self._get_app_directory() / "data"),
                "user_spells": str(self._get_app_directory() / "user_spells")
            },
            "spell_creation": {
                "similarity_threshold": 0.7,
                "max_recent_spells": 10,
                "default_element": "fire",
                "default_effect": "damage",
                "default_duration": "instant",
                "default_range": "30ft"
            },
            "ui": {
                "font_family": "Arial",
                "font_size": 12,
                "window_width": 900,
                "window_height": 700,
                "show_tooltips": True,
                "autosave": True
            }
        }
        
        # Initialize with defaults
        self.data = {}
        self.data.update(self.defaults)
        
        # Load user configuration if available
        self._load_config()
    
    def _get_app_directory(self) -> Path:
        """
        Get the application directory path, creating it if it doesn't exist.
        
        Returns:
            Path to the application directory
        """
        # Determine the appropriate location for application data
        home = Path.home()
        if os.name == 'nt':  # Windows
            app_dir = home / "AppData" / "Local" / "BloodBondTools"
        else:  # macOS, Linux, etc.
            app_dir = home / ".bloodbondtools"
        
        # Create directory if it doesn't exist
        app_dir.mkdir(parents=True, exist_ok=True)
        
        return app_dir
    
    def _load_config(self) -> None:
        """
        Load configuration from file, falling back to defaults if necessary.
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    
                # Update config with user values, preserving defaults for missing keys
                self._update_nested_dict(self.data, user_config)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.logger.info("No configuration file found, using defaults")
                self.save()  # Create default config file
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            # Continue with defaults
    
    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """
        Update a nested dictionary with values from another nested dictionary.
        
        Args:
            d: Dictionary to update
            u: Dictionary with update values
            
        Returns:
            Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
        return d
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation for nested keys.
        
        Args:
            key_path: Path to configuration value using dot notation (e.g., "ui.theme")
            default: Default value to return if key not found
            
        Returns:
            Configuration value or default if not found
        """
        keys = key_path.split('.')
        value = self.data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any, save: bool = True) -> None:
        """
        Set a configuration value using dot notation for nested keys.
        
        Args:
            key_path: Path to configuration value using dot notation (e.g., "ui.theme")
            value: Value to set
            save: Whether to save configuration to file after setting
        """
        keys = key_path.split('.')
        config = self.data
        
        # Navigate to the innermost dictionary
        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file if requested
        if save:
            self.save()
    
    def save(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Create parent directories if they don't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def reset(self, key_path: Optional[str] = None, save: bool = True) -> None:
        """
        Reset configuration to defaults, either a specific key or the entire config.
        
        Args:
            key_path: Optional path to specific config key to reset
            save: Whether to save configuration to file after resetting
        """
        if key_path is None:
            # Reset entire configuration
            self.data = {}
            self.data.update(self.defaults)
        else:
            # Reset specific configuration key
            keys = key_path.split('.')
            default_value = self.defaults
            
            # Find default value for the specified key
            try:
                for key in keys:
                    default_value = default_value[key]
                
                # Set value back to default
                self.set(key_path, default_value, save=False)
            except (KeyError, TypeError):
                self.logger.warning(f"No default value found for {key_path}")
        
        if save:
            self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary containing all configuration values (deep copy to prevent modification)
        """
        return copy.deepcopy(self.data)

