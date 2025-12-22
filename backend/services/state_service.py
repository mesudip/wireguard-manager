import os
import json
import subprocess
import difflib
from typing import List, Dict, Any, Optional
from models.types import InterfaceState, PeerStateInfo, WireGuardConfig
from services.config import parse_config


class StateService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def get_state(self, interface: str) -> InterfaceState:
        """Get current state (equivalent to wg show)."""
        try:
            output = subprocess.check_output(
                ["wg", "show", interface], 
                stderr=subprocess.STDOUT
            ).decode()
            
            # Parse wg show output
            state: InterfaceState = {"interface": interface, "peers": []}
            current_peer: Optional[Dict[str, Any]] = None
            
            for line in output.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('peer:'):
                    if current_peer:
                        state['peers'].append(current_peer)
                    current_peer = {"public_key": line.split(':', 1)[1].strip()}
                elif current_peer and ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().replace(' ', '_')
                    current_peer[key] = value.strip()
            
            if current_peer:
                state['peers'].append(current_peer)
            
            return state
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Interface not active or not found: {e.output.decode()}")
    
    def get_state_diff(self, interface: str) -> str:
        """Get diff between wg command output and current conf file."""
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        
        # Get config file
        config: WireGuardConfig = {"Interface": {}, "Peers": []}
        if os.path.exists(final_config_path):
            parsed = parse_config(final_config_path)
            if parsed:
                config = parsed
        
        # Get current state
        try:
            state_output = subprocess.check_output(
                ["wg", "show", interface], 
                stderr=subprocess.STDOUT
            ).decode()
            
            config_lines = json.dumps(config, indent=2, sort_keys=True).splitlines()
            state_lines = state_output.splitlines()
            
            diff = list(difflib.unified_diff(
                config_lines, state_lines,
                lineterm='',
                fromfile='config',
                tofile='state'
            ))
            
            return '\n'.join(diff)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Interface not active: {e.output.decode()}")
