import json
import os
from typing import Any, Dict, Union


class SimpleConfigManager:
    """Simple configuration manager to replace pyutils_lib ConfigManager"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # Default config file location
            config_file = os.path.join(
                os.path.expanduser("~"), 
                ".bigfix_universal_qna_config.json"
            )
        
        self.config_file = config_file
        self.config_data = {}
        self.defaults = {}
        
        # Ensure config directory exists
        config_dir = os.path.dirname(self.config_file)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                self.config_data = {}
                self._save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config_data = {}
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def define_setting(self, key: str, persistent: bool, default_value: Any, 
                      value_type: type, description: str = ""):
        """Define a setting with default value (for compatibility)"""
        self.defaults[key] = default_value
        
        # If setting doesn't exist, use default
        if key not in self.config_data:
            self.config_data[key] = default_value
            if persistent:
                self._save_config()
    
    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """Get a setting value"""
        return self.config_data.get(key, self.defaults.get(key, default_value))
    
    def set_setting(self, key: str, value: Any, persistent: bool = True):
        """Set a setting value"""
        self.config_data[key] = value
        if persistent:
            self._save_config()
    
    def load_configuration(self):
        """Load configuration (for compatibility)"""
        self._load_config()