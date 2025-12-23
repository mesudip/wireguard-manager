import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from models.types import WireGuardConfig, InterfaceResponse, InterfaceDetailResponse
from services.config import parse_config, write_config
from services.crypto import generate_keys, get_public_key
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
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        Path(base_dir).mkdir(parents=True, exist_ok=True)
    
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
        listen_port: str = '51820'
    ) -> InterfaceResponse:
        """Create a new WireGuard interface."""
        validate_interface_name(name)
        validate_ip_address(address)
        validate_port(listen_port)
        
        interface_dir = os.path.join(self.base_dir, name)
        
        if os.path.exists(interface_dir):
            raise ConfigurationException(f"Interface '{name}' already exists")
        
        os.makedirs(interface_dir, exist_ok=True)
        
        # Generate keys
        private_key, public_key = generate_keys()
        
        # Create interface config
        config: WireGuardConfig = {
            "Interface": {
                "PrivateKey": private_key,
                "Address": address,
                "ListenPort": listen_port
            },
            "Peers": []
        }
        
        config_path = os.path.join(interface_dir, f"{name}.conf")
        write_config(config_path, config)
        
        return {
            "name": name,
            "public_key": public_key,
            "address": address,
            "listen_port": listen_port
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
        public_key = get_public_key(private_key) if private_key else ''
        
        return {
            "name": name,
            "public_key": public_key,
            "address": config['Interface'].get('Address', ''),
            "listen_port": config['Interface'].get('ListenPort', ''),
            "config": config
        }
    
    def update_interface(
        self, 
        name: str, 
        address: Optional[str] = None, 
        listen_port: Optional[str] = None
    ) -> None:
        """Update a specific interface."""
        validate_ip_address(address)
        validate_port(listen_port)
        
        interface_dir = os.path.join(self.base_dir, name)
        config_path = os.path.join(interface_dir, f"{name}.conf")
        
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
        
        write_config(config_path, config)
    
    def delete_interface(self, name: str) -> None:
        """Delete a specific interface."""
        interface_dir = os.path.join(self.base_dir, name)
        
        if not os.path.exists(interface_dir):
            raise InterfaceNotFoundException(name)
        
        shutil.rmtree(interface_dir)
    
    def get_interface_dir(self, name: str) -> str:
        """Get the directory path for an interface."""
        return os.path.join(self.base_dir, name)
