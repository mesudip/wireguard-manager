import configparser
import os
from typing import Dict, Any, Optional
from pathlib import Path


class AppConfig:
    """Application configuration manager that reads from /etc/wireguard/backend.conf"""
    
    DEFAULT_CONFIG_PATH = "/etc/wireguard/backend.conf"
    
    # Default configuration values
    DEFAULTS = {
        'server': {
            'host': '::',
            'port': '5000',
            'debug': 'false',
        },
        'cors': {
            'enabled': 'true',
            'origins': '*',
            'methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'allow_headers': 'Content-Type,Authorization',
            'expose_headers': '',
            'supports_credentials': 'false',
            'max_age': '3600',
        },
        'wireguard': {
            'base_dir': '/etc/wireguard',
        },
        'logging': {
            'method': 'console',
            'level': 'INFO',
            'dir': '/var/log/wireguard-manager',
            'max_bytes': '10485760',  # 10MB
            'backup_count': '5',
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config file (defaults to /etc/wireguard/backend.conf)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file with defaults."""
        # Load defaults first
        self.config.read_dict(self.DEFAULTS)
        
        # Override with file config if it exists
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path)
                print(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                print(f"Warning: Failed to read config file {self.config_path}: {e}")
                print("Using default configuration")
        else:
            print(f"Config file {self.config_path} not found, using defaults")
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if not found
            
        Returns:
            Configuration value
        """
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.get(section, key, str(fallback))
        return value.lower() in ('true', 'yes', '1', 'on')
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value."""
        try:
            return int(self.get(section, key, str(fallback)))
        except ValueError:
            return fallback
    
    def get_list(self, section: str, key: str, fallback: list = None) -> list:
        """Get list configuration value (comma-separated)."""
        value = self.get(section, key, '')
        if not value:
            return fallback or []
        return [item.strip() for item in value.split(',')]
    
    # Convenience properties
    @property
    def server_host(self) -> str:
        return self.get('server', 'host')
    
    @property
    def server_port(self) -> int:
        return self.get_int('server', 'port')
    
    @property
    def debug(self) -> bool:
        return self.get_bool('server', 'debug')
    
    @property
    def cors_enabled(self) -> bool:
        return self.get_bool('cors', 'enabled')
    
    @property
    def cors_origins(self) -> str:
        return self.get('cors', 'origins')
    
    @property
    def cors_methods(self) -> list:
        return self.get_list('cors', 'methods')
    
    @property
    def cors_allow_headers(self) -> list:
        return self.get_list('cors', 'allow_headers')
    
    @property
    def cors_expose_headers(self) -> list:
        return self.get_list('cors', 'expose_headers')
    
    @property
    def cors_supports_credentials(self) -> bool:
        return self.get_bool('cors', 'supports_credentials')
    
    @property
    def cors_max_age(self) -> int:
        return self.get_int('cors', 'max_age')
    
    @property
    def wireguard_base_dir(self) -> str:
        return self.get('wireguard', 'base_dir')
    
    @property
    def logging_method(self) -> str:
        return self.get('logging', 'method')
    
    @property
    def logging_level(self) -> str:
        return self.get('logging', 'level')
    
    @property
    def logging_dir(self) -> str:
        return self.get('logging', 'dir')
    
    @property
    def logging_max_bytes(self) -> int:
        return self.get_int('logging', 'max_bytes')
    
    @property
    def logging_backup_count(self) -> int:
        return self.get_int('logging', 'backup_count')
    
    def create_default_config(self) -> None:
        """Create a default configuration file."""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            f.write("# WireGuard Manager Backend Configuration\n")
            f.write("# This file configures the backend API server\n\n")
            
            for section, options in self.DEFAULTS.items():
                f.write(f"[{section}]\n")
                for key, value in options.items():
                    # Add comments for important options
                    if section == 'server' and key == 'host':
                        f.write("# Server host - use '::' for IPv4+IPv6, '0.0.0.0' for IPv4 only\n")
                    elif section == 'cors' and key == 'origins':
                        f.write("# CORS origins - use '*' for all, or comma-separated list of domains\n")
                    elif section == 'cors' and key == 'enabled':
                        f.write("# Enable CORS support\n")
                    
                    f.write(f"{key} = {value}\n")
                f.write("\n")
        
        print(f"Created default configuration file at {self.config_path}")
