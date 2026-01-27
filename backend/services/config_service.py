import os
import json
import difflib
import shutil
import subprocess
from typing import List, Optional
from models.types import WireGuardConfig, DiffResponse
from services.config import parse_config, write_config
from utils.command import run_command


class ConfigService:
    def __init__(self, base_dir: str, use_systemd: bool = True):
        self.base_dir = base_dir
        self.use_systemd = use_systemd
    
    def sync_config(self, interface: str) -> str:
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
        
        # Clean and Recreate interface directory
        if os.path.exists(interface_dir):
            shutil.rmtree(interface_dir)
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

    def apply_config(self, interface: str) -> Optional[str]:
        """Apply the final config file to the running interface."""
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        
        if not os.path.exists(final_config_path):
            raise FileNotFoundError(f"Config file for {interface} not found. Run sync first.")
        
        # 1. Parse the config to filter out non-wg fields (like Address)
        config = parse_config(final_config_path)
        if not config:
            raise ValueError(f"Could not parse config file at {final_config_path}")
            
        # 2. Create a temporary clean config for 'wg syncconf'
        # wg syncconf only supports PrivateKey, ListenPort, FwMark in [Interface]
        clean_config_path = f"{final_config_path}.tmp"
        try:
            with open(clean_config_path, 'w') as f:
                f.write('[Interface]\n')
                # Only include fields supported by 'wg syncconf'
                for key in ['PrivateKey', 'ListenPort', 'FwMark']:
                    if key in config['Interface']:
                        f.write(f"{key} = {config['Interface'][key]}\n")
                
                for peer in config.get('Peers', []):
                    f.write('\n[Peer]\n')
                    for key, value in peer.items():
                        if value:
                            f.write(f"{key} = {value}\n")
            
            # 3. Apply the clean config using wg syncconf
            warnings = []
            try:
                result = run_command(["wg", "syncconf", interface, clean_config_path])
                if result.stderr:
                    warnings.append(result.stderr.decode())
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.decode() if e.stderr else str(e)
                if "No such device" in error_msg or "not found" in error_msg.lower():
                    # If the interface doesn't exist, bring it up
                    if self.use_systemd:
                        # Try systemctl start wg-quick@<interface>
                        result = run_command(["systemctl", "restart", f"wg-quick@{interface}"])
                    else:
                        # Direct wg-quick up
                        result = run_command(["wg-quick", "up", final_config_path])
                        
                    if result.stderr:
                        warnings.append(result.stderr.decode())
                else:
                    raise
            
            return "\n".join(warnings) if warnings else None
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"Failed to apply WireGuard state: {error_msg}")
        except Exception as e:
            # Re-wrap other exceptions (like PermissionDeniedException) to provide context
            if not isinstance(e, (RuntimeError, FileNotFoundError, ValueError)):
                raise RuntimeError(f"Failed to apply WireGuard state: {str(e)}")
            raise
        finally:
            if os.path.exists(clean_config_path):
                os.remove(clean_config_path)
