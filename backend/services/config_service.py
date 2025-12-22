import os
import json
import difflib
from typing import List
from models.types import WireGuardConfig, DiffResponse
from services.config import parse_config, write_config


class ConfigService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def apply_config(self, interface: str) -> str:
        """Generate the final config file from the interface folder."""
        interface_dir = os.path.join(self.base_dir, interface)
        interface_config_path = os.path.join(interface_dir, f"{interface}.conf")
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        
        if not os.path.exists(interface_config_path):
            raise FileNotFoundError("Interface not found")
        
        # Read interface config
        config = parse_config(interface_config_path)
        if not config:
            raise ValueError("Invalid interface config")
        
        # Add all peers from separate files
        for file in os.listdir(interface_dir):
            if file.endswith('.conf') and file != f"{interface}.conf":
                peer_path = os.path.join(interface_dir, file)
                peer_config = parse_config(peer_path)
                if peer_config and peer_config.get('Peers'):
                    config['Peers'].extend(peer_config['Peers'])
        
        # Write final config
        write_config(final_config_path, config)
        
        return final_config_path
    
    def reset_config(self, interface: str) -> None:
        """Generate the interface folder from the final config file."""
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        interface_dir = os.path.join(self.base_dir, interface)
        
        if not os.path.exists(final_config_path):
            raise FileNotFoundError("Config file not found")
        
        # Parse final config
        config = parse_config(final_config_path)
        if not config:
            raise ValueError("Invalid config file")
        
        # Create interface directory
        os.makedirs(interface_dir, exist_ok=True)
        
        # Write interface config (without peers)
        interface_config: WireGuardConfig = {"Interface": config['Interface'], "Peers": []}
        interface_config_path = os.path.join(interface_dir, f"{interface}.conf")
        write_config(interface_config_path, interface_config)
        
        # Write individual peer configs
        for idx, peer in enumerate(config.get('Peers', [])):
            peer_name = f"peer{idx + 1}"
            peer_path = os.path.join(interface_dir, f"{peer_name}.conf")
            peer_config: WireGuardConfig = {"Interface": {}, "Peers": [peer]}
            write_config(peer_path, peer_config)
    
    def get_config_diff(self, interface: str) -> str:
        """Get diff between folder structure and current conf file."""
        interface_dir = os.path.join(self.base_dir, interface)
        interface_config_path = os.path.join(interface_dir, f"{interface}.conf")
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        
        if not os.path.exists(interface_config_path):
            raise FileNotFoundError("Interface not found")
        
        # Build config from folder
        config = parse_config(interface_config_path)
        if not config:
            raise ValueError("Invalid interface config")
        
        for file in os.listdir(interface_dir):
            if file.endswith('.conf') and file != f"{interface}.conf":
                peer_path = os.path.join(interface_dir, file)
                peer_config = parse_config(peer_path)
                if peer_config and peer_config.get('Peers'):
                    config['Peers'].extend(peer_config['Peers'])
        
        # Get final config if exists
        final_config: WireGuardConfig = {"Interface": {}, "Peers": []}
        if os.path.exists(final_config_path):
            parsed = parse_config(final_config_path)
            if parsed:
                final_config = parsed
        
        # Generate diff
        folder_lines = json.dumps(config, indent=2, sort_keys=True).splitlines()
        final_lines = json.dumps(final_config, indent=2, sort_keys=True).splitlines()
        
        diff = list(difflib.unified_diff(
            final_lines, folder_lines, 
            lineterm='', 
            fromfile='current.conf',
            tofile='folder'
        ))
        
        return '\n'.join(diff)
