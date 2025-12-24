import os
import json
import subprocess
import difflib
from typing import List, Dict, Any, Optional
from models.types import InterfaceState, PeerStateInfo, WireGuardConfig
from services.config import parse_config
from utils.command import run_command
from exceptions.wireguard_exceptions import StateException, InterfaceNotFoundException


class StateService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def get_state(self, interface: str) -> InterfaceState:
        """Get current state (equivalent to wg show)."""
        try:
            result = run_command(["wg", "show", interface])
            output = result.stdout.decode()
            
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
            
            state['status'] = 'active'
            return state
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            if "does not exist" in error_msg.lower() or "no such device" in error_msg.lower():
                return {
                    "interface": interface,
                    "status": "not_found",
                    "message": f"Interface '{interface}' not found",
                    "peers": []
                }
            return {
                "interface": interface,
                "status": "inactive",
                "message": error_msg,
                "peers": []
            }
        except Exception as e:
            return {
                "interface": interface,
                "status": "inactive",
                "message": str(e),
                "peers": []
            }
    
    def get_state_diff(self, interface: str) -> Dict[str, Any]:
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
            result = run_command(["wg", "show", interface])
            state_output = result.stdout.decode()
            
            config_lines = json.dumps(config, indent=2, sort_keys=True).splitlines()
            state_lines = state_output.splitlines()
            
            diff = list(difflib.unified_diff(
                config_lines, state_lines,
                lineterm='',
                fromfile='config',
                tofile='state'
            ))
            
            return {
                "diff": '\n'.join(diff),
                "status": "success"
            }
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            status = "not_found" if ("does not exist" in error_msg.lower() or "no such device" in error_msg.lower()) else "inactive"
            return {
                "diff": "",
                "status": status,
                "message": f"Unable to get state for diff: {error_msg.strip()}"
            }
        except Exception as e:
            return {
                "diff": "",
                "status": "error",
                "message": f"Error getting state for diff: {str(e)}"
            }
