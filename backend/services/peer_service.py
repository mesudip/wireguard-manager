import os
from typing import List, Optional
from models.types import WireGuardConfig, PeerResponse
from services.config import parse_config, write_config
from services.crypto import generate_keys
from utils.validators import validate_ip_address, validate_endpoint


class PeerService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def list_peers(self, interface: str) -> List[PeerResponse]:
        """List all peers for an interface."""
        interface_dir = os.path.join(self.base_dir, interface)
        
        if not os.path.isdir(interface_dir):
            raise FileNotFoundError("Interface not found")
        
        peers = []
        for file in os.listdir(interface_dir):
            if file.endswith('.conf') and file != f"{interface}.conf":
                peer_name = file[:-5]  # Remove .conf extension
                peer_path = os.path.join(interface_dir, file)
                peer_config = parse_config(peer_path)
                
                if peer_config and peer_config.get('Peers'):
                    peer_data = peer_config['Peers'][0]
                    peers.append({
                        "name": peer_name,
                        "public_key": peer_data.get('PublicKey', ''),
                        "allowed_ips": peer_data.get('AllowedIPs', ''),
                        "endpoint": peer_data.get('Endpoint', '')
                    })
        
        return peers
    
    def add_peer(
        self, 
        interface: str, 
        name: str, 
        allowed_ips: str = '10.0.0.2/32',
        endpoint: str = ''
    ) -> PeerResponse:
        """Add a new peer to an interface."""
        interface_dir = os.path.join(self.base_dir, interface)
        
        if not os.path.isdir(interface_dir):
            raise FileNotFoundError("Interface not found")
        
        peer_path = os.path.join(interface_dir, f"{name}.conf")
        if os.path.exists(peer_path):
            raise ValueError("Peer already exists")
        
        # Validate inputs
        if allowed_ips:
            allowed_ips = ",".join([a.strip() for a in allowed_ips.split(',') if a.strip()])
        validate_ip_address(allowed_ips, allow_multiple=True)
        validate_endpoint(endpoint)
        
        # Generate keys for peer
        private_key, public_key, warnings = generate_keys()
        
        # Create peer config
        peer_config: WireGuardConfig = {
            "Interface": {},
            "Peers": [{
                "PublicKey": public_key,
                "AllowedIPs": allowed_ips,
                "Endpoint": endpoint
            }]
        }
        
        write_config(peer_path, peer_config)
        
        return {
            "name": name,
            "public_key": public_key,
            "allowed_ips": allowed_ips,
            "endpoint": endpoint,
            "warnings": warnings
        }
    
    def get_peer(self, interface: str, peer_name: str) -> PeerResponse:
        """Get details of a specific peer."""
        peer_path = os.path.join(self.base_dir, interface, f"{peer_name}.conf")
        
        if not os.path.exists(peer_path):
            raise FileNotFoundError("Peer not found")
        
        peer_config = parse_config(peer_path)
        
        if not peer_config or not peer_config.get('Peers'):
            raise ValueError("Invalid peer config")
        
        peer_data = peer_config['Peers'][0]
        return {
            "name": peer_name,
            "public_key": peer_data.get('PublicKey', ''),
            "allowed_ips": peer_data.get('AllowedIPs', ''),
            "endpoint": peer_data.get('Endpoint', '')
        }
    
    def update_peer(
        self, 
        interface: str, 
        peer_name: str,
        allowed_ips: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> None:
        """Update a specific peer."""
        peer_path = os.path.join(self.base_dir, interface, f"{peer_name}.conf")
        
        if not os.path.exists(peer_path):
            raise FileNotFoundError("Peer not found")
        
        peer_config = parse_config(peer_path)
        
        if not peer_config or not peer_config.get('Peers'):
            raise ValueError("Invalid peer config")
        
        peer_data = peer_config['Peers'][0]
        
        if allowed_ips is not None:
            if allowed_ips:
                allowed_ips = ",".join([a.strip() for a in allowed_ips.split(',') if a.strip()])
            validate_ip_address(allowed_ips, allow_multiple=True)
            peer_data['AllowedIPs'] = allowed_ips
        if endpoint is not None:
            validate_endpoint(endpoint)
            peer_data['Endpoint'] = endpoint
        
        write_config(peer_path, peer_config)
    
    def delete_peer(self, interface: str, peer_name: str) -> None:
        """Delete a specific peer."""
        peer_path = os.path.join(self.base_dir, interface, f"{peer_name}.conf")
        
        if not os.path.exists(peer_path):
            raise FileNotFoundError("Peer not found")
        
        os.remove(peer_path)
