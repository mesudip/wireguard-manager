import os
import json
import difflib
import shutil
import copy
import subprocess
from typing import List, Optional, Dict, Any
from models.types import WireGuardConfig, DiffResponse, ConfigDiffResponse, ConfigDiffData, ConfigDiffPeer
from services.config import parse_config, write_config
from services.crypto import get_public_key
from utils.command import run_command
from utils.lock import acquire_write_lock


class ConfigService:
    def __init__(self, base_dir: str, use_systemd: bool = True):
        self.base_dir = base_dir
        self.use_systemd = use_systemd
    
    def sync_config(self, interface: str) -> str:
        """Generate the final config file from the interface folder."""
        interface_dir = os.path.join(self.base_dir, interface)
        interface_config_path = os.path.join(interface_dir, f"{interface}.conf")
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        
        with acquire_write_lock(final_config_path):
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
                        # Remove _name field before adding to final config
                        for peer in peer_config['Peers']:
                            peer_data = {k: v for k, v in peer.items() if k != '_name'}
                            config['Peers'].append(peer_data)
            
            # Write final config
            write_config(final_config_path, config)
        
        return final_config_path
    
    def reset_config(self, interface: str) -> None:
        """Generate the interface folder from the final config file."""
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        interface_dir = os.path.join(self.base_dir, interface)
        
        with acquire_write_lock(final_config_path):
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
                # Try to get peer name from comment in config, otherwise generate
                peer_name = peer.get('_name') or f"peer{idx + 1}"
                peer_path = os.path.join(interface_dir, f"{peer_name}.conf")
                # Remove _name from peer data before writing
                peer_data = {k: v for k, v in peer.items() if k != '_name'}
                peer_config: WireGuardConfig = {"Interface": {}, "Peers": [peer_data]}
                write_config(peer_path, peer_config, peer_name=peer_name)
    
    def _redact_config(self, config: WireGuardConfig) -> dict:
        """Deep copy and redact sensitive fields from config."""
        redacted = copy.deepcopy(config)
        if 'Interface' in redacted:
             private_key = redacted['Interface'].get('PrivateKey')
             if private_key:
                 # Derive public key so change is visible in diff even when redacted
                 try:
                     public_key, _ = get_public_key(private_key)
                     redacted['Interface']['PublicKey (derived)'] = public_key
                 except Exception:
                     pass
                 redacted['Interface']['PrivateKey'] = '(REDACTED)'
        
        for peer in redacted.get('Peers', []):
            if 'PresharedKey' in peer:
                peer['PresharedKey'] = '(REDACTED)'
        return redacted

    def get_config_diff(self, interface: str) -> ConfigDiffResponse:
        """Get structured config diff between folder structure and current conf file."""
        interface_dir = os.path.join(self.base_dir, interface)
        interface_config_path = os.path.join(interface_dir, f"{interface}.conf")
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        
        if not os.path.exists(interface_config_path):
            raise FileNotFoundError("Interface not found")
        
        # Build config from folder with peer names
        folder_peers: List[ConfigDiffPeer] = []
        for file in sorted(os.listdir(interface_dir)):
            if file.endswith('.conf') and file != f"{interface}.conf":
                peer_name = file[:-5]  # Remove .conf extension
                peer_path = os.path.join(interface_dir, file)
                peer_config = parse_config(peer_path)
                if peer_config and peer_config.get('Peers'):
                    for peer in peer_config['Peers']:
                        # Use name from comment if available, otherwise use filename
                        name = peer.get('_name') or peer_name
                        folder_peers.append({
                            'name': name,
                            'public_key': peer.get('PublicKey', ''),
                            'allowed_ips': peer.get('AllowedIPs', ''),
                            'endpoint': peer.get('Endpoint'),
                            'persistent_keepalive': peer.get('PersistentKeepalive')
                        })
        
        # Get final config peers
        current_peers: List[ConfigDiffPeer] = []
        if os.path.exists(final_config_path):
            final_config = parse_config(final_config_path)
            if final_config and final_config.get('Peers'):
                for idx, peer in enumerate(final_config['Peers']):
                    # Try to match with folder peer to get name
                    peer_name = peer.get('_name') or f"peer{idx + 1}"
                    public_key = peer.get('PublicKey', '')
                    allowed_ips = peer.get('AllowedIPs', '')
                    
                    # Try to find matching peer in folder by name or allowed IPs
                    for folder_peer in folder_peers:
                        if (folder_peer['public_key'] == public_key or
                            folder_peer['name'] == peer_name or
                            folder_peer['allowed_ips'] == allowed_ips):
                            peer_name = folder_peer['name']
                            break
                    
                    current_peers.append({
                        'name': peer_name,
                        'public_key': public_key,
                        'allowed_ips': allowed_ips,
                        'endpoint': peer.get('Endpoint'),
                        'persistent_keepalive': peer.get('PersistentKeepalive')
                    })
        
        return {
            'current_config': {'peers': current_peers},
            'folder_config': {'peers': folder_peers}
        }

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
            # Write the temporary clean config and ensure it's only readable by owner
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

            # Ensure the temp clean config is not world-readable since it may contain PrivateKey
            try:
                os.chmod(clean_config_path, 0o600)
            except OSError:
                # Best effort; do not fail the whole operation if chmod isn't supported
                pass
            
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
