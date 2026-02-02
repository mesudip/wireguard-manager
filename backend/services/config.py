import os
from typing import Optional
from pathlib import Path
from models.types import WireGuardConfig, InterfaceConfig, PeerConfig


def parse_config(config_path: str) -> Optional[WireGuardConfig]:
    """
    Parse a WireGuard config file.
    Handles comments anywhere in the file. Only comments immediately before [Peer]
    sections are captured as peer names.
    
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
    pending_peer_name = None  # Store comment that appears right before [Peer]
    last_line_was_comment = False
    
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines but reset pending peer name if we had one
            if not line:
                if last_line_was_comment and pending_peer_name:
                    # Empty line after comment - reset pending name
                    pending_peer_name = None
                last_line_was_comment = False
                continue
            
            # Handle comments
            if line.startswith('#'):
                # Extract comment text (remove leading # and whitespace)
                comment_text = line[1:].strip()
                # Only capture as potential peer name if not currently in a section
                # or if we're between peers
                if current_section != 'Interface' and comment_text:
                    pending_peer_name = comment_text
                    last_line_was_comment = True
                continue
            
            # Reset comment flag for non-comment lines
            last_line_was_comment = False
            
            if line == '[Interface]':
                current_section = 'Interface'
                pending_peer_name = None  # Clear any pending peer name
            elif line == '[Peer]':
                # Save previous peer if exists
                if current_peer:
                    config['Peers'].append(current_peer)
                current_peer = {}
                # Add peer name from comment if it was immediately before this [Peer]
                if pending_peer_name:
                    current_peer['_name'] = pending_peer_name
                pending_peer_name = None
                current_section = 'Peer'
            elif '=' in line:
                # Parse key-value pair
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if current_section == 'Interface':
                    config['Interface'][key] = value
                elif current_section == 'Peer':
                    current_peer[key] = value
                # Ignore key-value pairs outside of sections
            # Ignore any other lines that don't match expected format
        
        # Don't forget to add the last peer if exists
        if current_peer:
            config['Peers'].append(current_peer)
    
    return config


def write_config(config_path: str, config_data: WireGuardConfig, peer_name: Optional[str] = None) -> None:
    """
    Write a WireGuard config file with secure permissions (0640).
    Directories are created with 0750 permissions.
    
    Args:
        config_path: Path to write the config file
        config_data: Config data to write
        peer_name: Optional peer name to add as comment for peer configs
    """
    # Create parent directories with 0750 permissions
    Path(config_path).parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    
    # We use os.open and os.fdopen to set permissions at creation time or chmod after
    # But for simplicity and cross-platform (where supported), we'll write then chmod
    with open(config_path, 'w') as f:
        if config_data.get('Interface'):
            f.write('[Interface]\n')
            for key, value in config_data.get('Interface', {}).items():
                f.write(f'{key} = {value}\n')
        
        for idx, peer in enumerate(config_data.get('Peers', [])):
            # Add peer name as comment if provided (for single peer files)
            if peer_name and idx == 0:
                f.write(f'\n# {peer_name}\n')
            f.write('[Peer]\n')
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
