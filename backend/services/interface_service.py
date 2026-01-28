import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from models.types import WireGuardConfig, InterfaceResponse, InterfaceDetailResponse
from services.config import parse_config, write_config
from services.crypto import generate_keys, get_public_key
from services.config_service import ConfigService
from utils.lock import acquire_write_lock
from exceptions.wireguard_exceptions import (
    InterfaceNotFoundException,
    ConfigurationException
)
from utils.validators import (
    validate_interface_name,
    validate_ip_address,
    validate_port
)


class InterfaceService:
    def __init__(self, base_dir: str, config_service: ConfigService):
        self.base_dir = base_dir
        self.config_service = config_service
        Path(base_dir).mkdir(parents=True, exist_ok=True, mode=0o750)
    
    def _sync_interface(self, name: str) -> None:
        """Sync the interface folder into the final config file using ConfigService.

        Kept inside the service layer to avoid routes creating ConfigService.
        """
        try:
            self.config_service.sync_config(name)
        except Exception:
            # Best effort; do not raise to avoid breaking API flow when sync fails
            pass

    def list_interfaces(self) -> List[str]:
        """List all WireGuard interfaces."""
        interfaces = []
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    interfaces.append(item)
        return interfaces
    
    def create_interface(
        self, 
        name: str, 
        address: str = '10.0.0.1/24', 
        listen_port: str = '51820',
        post_up: Optional[str] = None,
        post_down: Optional[str] = None,
        dns: Optional[str] = None
    ) -> InterfaceResponse:
        """Create a new WireGuard interface."""
        validate_interface_name(name)
        validate_ip_address(address, allow_multiple=False)
        validate_port(listen_port)
        
        manager_lock = os.path.join(self.base_dir, ".manager.lock")
        with acquire_write_lock(manager_lock):
            interface_dir = os.path.join(self.base_dir, name)
            
            if os.path.exists(interface_dir):
                raise ConfigurationException(f"Interface '{name}' already exists")
            
            os.makedirs(interface_dir, exist_ok=True, mode=0o750)
            
            # Generate keys
            private_key, public_key, warnings = generate_keys()
            
            # Create interface config
            config: WireGuardConfig = {
                "Interface": {
                    "PrivateKey": private_key,
                    "Address": address,
                    "ListenPort": listen_port
                },
                "Peers": []
            }
            
            # Add optional fields if provided
            if post_up:
                config['Interface']['PostUp'] = post_up
            if post_down:
                config['Interface']['PostDown'] = post_down
            if dns:
                config['Interface']['DNS'] = dns
            
            config_path = os.path.join(interface_dir, f"{name}.conf")
            write_config(config_path, config)
            # Sync assembled interface folder into final config
            self._sync_interface(name)
        
        return {
            "name": name,
            "public_key": public_key,
            "address": address,
            "listen_port": listen_port,
            "post_up": post_up,
            "post_down": post_down,
            "dns": dns,
            "warnings": warnings
        }
    
    def get_interface(self, name: str) -> InterfaceDetailResponse:
        """Get details of a specific interface."""
        interface_dir = os.path.join(self.base_dir, name)
        config_path = os.path.join(interface_dir, f"{name}.conf")
        
        if not os.path.exists(config_path):
            raise InterfaceNotFoundException(name)
        
        config = parse_config(config_path)
        if not config:
            raise ConfigurationException(f"Invalid config file for interface '{name}'")
        
        # Get public key from private key
        private_key = config['Interface'].get('PrivateKey', '')
        public_key, warnings = get_public_key(private_key) if private_key else ('', None)
        
        # SECURITY: Never return the config object or private key to the frontend
        return {
            "name": name,
            "public_key": public_key,
            "address": config['Interface'].get('Address', ''),
            "listen_port": config['Interface'].get('ListenPort', ''),
            "post_up": config['Interface'].get('PostUp'),
            "post_down": config['Interface'].get('PostDown'),
            "dns": config['Interface'].get('DNS'),
            "warnings": warnings
        }
    
    def update_interface(
        self, 
        name: str, 
        address: Optional[str] = None, 
        listen_port: Optional[str] = None,
        post_up: Optional[str] = None,
        post_down: Optional[str] = None,
        dns: Optional[str] = None
    ) -> None:
        """Update a specific interface."""
        validate_ip_address(address, allow_multiple=False)
        validate_port(listen_port)
        
        interface_dir = os.path.join(self.base_dir, name)
        config_path = os.path.join(interface_dir, f"{name}.conf")
        
        with acquire_write_lock(config_path):
            if not os.path.exists(config_path):
                raise InterfaceNotFoundException(name)
            
            config = parse_config(config_path)
            if not config:
                raise ConfigurationException(f"Invalid config file for interface '{name}'")
            
            # Update interface config
            if address is not None:
                config['Interface']['Address'] = address
            if listen_port is not None:
                config['Interface']['ListenPort'] = str(listen_port)
            if post_up is not None:
                if post_up:
                    config['Interface']['PostUp'] = post_up
                elif 'PostUp' in config['Interface']:
                    del config['Interface']['PostUp']
            if post_down is not None:
                if post_down:
                    config['Interface']['PostDown'] = post_down
                elif 'PostDown' in config['Interface']:
                    del config['Interface']['PostDown']
            if dns is not None:
                if dns:
                    config['Interface']['DNS'] = dns
                elif 'DNS' in config['Interface']:
                    del config['Interface']['DNS']
            
            write_config(config_path, config)
            # Sync assembled interface folder into final config
            self._sync_interface(name)
    
    def delete_interface(self, name: str) -> None:
        """Delete a specific interface."""
        manager_lock = os.path.join(self.base_dir, ".manager.lock")
        with acquire_write_lock(manager_lock):
            interface_dir = os.path.join(self.base_dir, name)
            
            if not os.path.exists(interface_dir):
                raise InterfaceNotFoundException(name)
            
            shutil.rmtree(interface_dir)
    
    def get_interface_dir(self, name: str) -> str:
        """Get the directory path for an interface."""
        return os.path.join(self.base_dir, name)
