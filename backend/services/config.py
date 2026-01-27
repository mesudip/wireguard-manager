import os
from typing import Optional
from pathlib import Path
from models.types import WireGuardConfig, InterfaceConfig, PeerConfig


def parse_config(config_path: str) -> Optional[WireGuardConfig]:
    """
    Parse a WireGuard config file.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Parsed config dict or None if file doesn't exist
    """
    if not os.path.exists(config_path):
        return None
    
    config: WireGuardConfig = {"Interface": {}, "Peers": []}
    current_section = None
    current_peer: PeerConfig = {}
    
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line == '[Interface]':
                current_section = 'Interface'
            elif line == '[Peer]':
                if current_peer:
                    config['Peers'].append(current_peer)
                current_peer = {}
                current_section = 'Peer'
            elif '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if current_section == 'Interface':
                    config['Interface'][key] = value
                elif current_section == 'Peer':
                    current_peer[key] = value
        
        if current_peer:
            config['Peers'].append(current_peer)
    
    return config


def write_config(config_path: str, config_data: WireGuardConfig) -> None:
    """
    Write a WireGuard config file with secure permissions (0640).
    Directories are created with 0750 permissions.
    """
    # Create parent directories with 0750 permissions
    Path(config_path).parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    
    # We use os.open and os.fdopen to set permissions at creation time or chmod after
    # But for simplicity and cross-platform (where supported), we'll write then chmod
    with open(config_path, 'w') as f:
        f.write('[Interface]\n')
        for key, value in config_data.get('Interface', {}).items():
            f.write(f'{key} = {value}\n')
        
        for peer in config_data.get('Peers', []):
            f.write('\n[Peer]\n')
            for key, value in peer.items():
                if value:  # Only write non-empty values
                    f.write(f'{key} = {value}\n')
    
    # Set secure permissions:
    # - If the config contains a PrivateKey, restrict to owner read/write (0600)
    # - Otherwise allow owner read/write and group read (0640)
    try:
        contains_private = False
        iface = config_data.get('Interface', {}) or {}
        if 'PrivateKey' in iface and iface.get('PrivateKey'):
            contains_private = True
        else:
            # Also check peers for any private key fields (defensive)
            for p in config_data.get('Peers', []) or []:
                if p.get('PrivateKey'):
                    contains_private = True
                    break

        mode = 0o600 if contains_private else 0o640
        os.chmod(config_path, mode)
    except OSError as err:
        print(f"Warning: Could not set permissions on {config_path}: {err}")
        pass
