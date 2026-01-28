import os
from typing import List, Optional
from models.types import WireGuardConfig, PeerResponse
from services.config import parse_config, write_config
from services.crypto import generate_keys
from services.config_service import ConfigService
from utils.validators import validate_ip_address, validate_endpoint

class PeerService:
    def __init__(self, base_dir: str, config_service: ConfigService):
        self.base_dir = base_dir
        self.config_service = config_service

    def _sync_interface(self, interface: str) -> None:
        """Attempt to sync the interface folder into the final config file.

        This helper keeps ConfigService usage inside the service layer so
        routes don't need to construct ConfigService objects.
        """
        try:
            self.config_service.sync_config(interface)
        except Exception:
            # Best effort: do not raise to avoid breaking API flow when sync fails
            pass
    
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
                        "endpoint": peer_data.get('Endpoint', ''),
                        "persistent_keepalive": peer_data.get('PersistentKeepalive', '')
                    })
        
        return peers
    
    def add_peer(
        self, 
        interface: str, 
        name: str, 
        allowed_ips: Optional[str] = None,
        endpoint: str = '',
        public_key: Optional[str] = None,
        persistent_keepalive: Optional[str] = None
    ) -> PeerResponse:
        """Add a new peer to an interface."""
        interface_dir = os.path.join(self.base_dir, interface)
        
        if not os.path.isdir(interface_dir):
            raise FileNotFoundError("Interface not found")
        
        peer_path = os.path.join(interface_dir, f"{name}.conf")
        if os.path.exists(peer_path):
            raise ValueError("Peer already exists")
        
        # Load interface config to check its network
        if_config_path = os.path.join(interface_dir, f"{interface}.conf")
        if_config = parse_config(if_config_path)
        if not if_config:
            raise ValueError("Could not read interface config")
        
        if_address = if_config['Interface'].get('Address', '')
        if not if_address:
            raise ValueError("Interface has no Address defined")
        
        import ipaddress
        try:
            if_net = ipaddress.ip_interface(if_address).network
        except ValueError:
            raise ValueError(f"Invalid interface address: {if_address}")

        # Determine if discovery is requested
        is_automatic = False
        target_network = None
        
        # If no allowed_ips provided, default to interface network discovery
        if not allowed_ips:
            is_automatic = True
            target_network = if_net
        
        # Check for shorthand or CIDR-based discovery (requires single segment for now)
        if allowed_ips and not is_automatic and ',' not in allowed_ips:
            if '/' not in allowed_ips and ':' not in allowed_ips:
                # Clean parts
                parts = [p.strip() for p in allowed_ips.split('.') if p.strip()]
                # Determine if it's a subnet discovery request
                if len(parts) < 4 or (len(parts) == 4 and parts[-1] == '0'):
                    is_automatic = True
                    if len(parts) < 4:
                        prefix_len = 8 * len(parts)
                    else: 
                        prefix_len = 24
                    full_ip = ".".join(parts + ['0'] * (4 - len(parts)))
                    try:
                        target_network = ipaddress.IPv4Network(f"{full_ip}/{prefix_len}", strict=False)
                    except ValueError:
                        raise ValueError(f"Invalid subnet format: {allowed_ips}")
            else:
                # Looks like a CIDR. Only enable discovery if it's a subset of the interface network.
                try:
                    temp_net = ipaddress.ip_network(allowed_ips, strict=False)
                    if temp_net.prefixlen < 32 and temp_net.subnet_of(if_net):
                        is_automatic = True
                        target_network = temp_net
                except ValueError:
                    pass

        if is_automatic:
            # Verify target_network is compatible with if_net (must be a subset)
            # This is primarily for partial IP inputs which are always automatic
            if not target_network.subnet_of(if_net):
                 raise ValueError(f"Subnet {target_network} is not a subset of interface network {if_net}. Automatic IP discovery is only possible within the interface network.")
            
            # Find next available IP
            used_ips = set()
            # 1. Interface IP
            used_ips.add(ipaddress.ip_interface(if_address).ip)
            # 2. Peer IPs
            for peer in self.list_peers(interface):
                for ip_str in peer['allowed_ips'].split(','):
                    try:
                        used_ips.add(ipaddress.ip_interface(ip_str.strip()).ip)
                    except ValueError:
                        continue
            
            found_ip = None
            for host in target_network.hosts():
                if host not in used_ips:
                    found_ip = f"{host}/32"
                    break
            
            if not found_ip:
                raise ValueError(f"No available IPs in subnet {target_network}")
            
            allowed_ips = found_ip
        else:
            # Literal list or IP provided. 
            # Normalize first
            if allowed_ips:
                allowed_ips = ",".join([a.strip() for a in allowed_ips.split(',') if a.strip()])
            
            # Ensure at least one listed IP is within the interface subnet
            is_peer_in_vpn_subnet = False
            for addr in allowed_ips.split(','):
                try:
                    # Use overlaps to check if the address/range has any common ground with the VPN
                    net = ipaddress.ip_network(addr, strict=False)
                    if net.overlaps(if_net):
                        is_peer_in_vpn_subnet = True
                        break
                except ValueError:
                    continue
            
            if not is_peer_in_vpn_subnet:
                 raise ValueError(f"At least one IP address must be within the interface network {if_net}")

        # Validate final inputs
        if allowed_ips:
            allowed_ips = ",".join([a.strip() for a in allowed_ips.split(',') if a.strip()])
        validate_ip_address(allowed_ips, allow_multiple=True)
        validate_endpoint(endpoint)
        
        private_key = None
        warnings = None
        
        if not public_key:
            # Generate keys for peer if not provided
            private_key, public_key, warnings = generate_keys()
        
        # Create peer config
        peer_config: WireGuardConfig = {
            "Interface": {},
            "Peers": [{
                "PublicKey": public_key,
                "AllowedIPs": allowed_ips,
                "Endpoint": endpoint,
                "PersistentKeepalive": persistent_keepalive
            }]
        }
        
        write_config(peer_path, peer_config)
        # Attempt to sync the assembled interface config into the final file
        self._sync_interface(interface)

        return {
            "name": name,
            "public_key": public_key,
            "private_key": private_key,
            "allowed_ips": allowed_ips,
            "endpoint": endpoint,
            "persistent_keepalive": persistent_keepalive,
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
            "endpoint": peer_data.get('Endpoint', ''),
            "persistent_keepalive": peer_data.get('PersistentKeepalive', '')
        }
    
    def update_peer(
        self, 
        interface: str, 
        peer_name: str,
        allowed_ips: Optional[str] = None,
        endpoint: Optional[str] = None,
        new_name: Optional[str] = None,
        public_key: Optional[str] = None,
        persistent_keepalive: Optional[str] = None
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
            
            # Subnet overlap check
            if allowed_ips:
                import ipaddress
                # Load interface config to check its network
                if_config_path = os.path.join(self.base_dir, interface, f"{interface}.conf")
                if_config = parse_config(if_config_path)
                if_address = if_config['Interface'].get('Address', '')
                try:
                    if_net = ipaddress.ip_interface(if_address).network
                    is_peer_in_vpn_subnet = False
                    for addr in allowed_ips.split(','):
                        try:
                            # Use overlaps to check if the address/range has any common ground with the VPN
                            net = ipaddress.ip_network(addr, strict=False)
                            if net.overlaps(if_net):
                                is_peer_in_vpn_subnet = True
                                break
                        except ValueError:
                            continue
                    
                    if not is_peer_in_vpn_subnet:
                        raise ValueError(f"At least one IP address must be within the interface network {if_net}")
                except (ValueError, KeyError):
                    pass # Interface address issues handled in other parts
            
            peer_data['AllowedIPs'] = allowed_ips
        if endpoint is not None:
            validate_endpoint(endpoint)
            peer_data['Endpoint'] = endpoint
        
        if persistent_keepalive is not None:
            peer_data['PersistentKeepalive'] = persistent_keepalive
        
        # Allow updating public key
        if public_key is not None:
            if public_key:
                peer_data['PublicKey'] = public_key
            else:
                # If explicitly blanked, remove the key
                if 'PublicKey' in peer_data:
                    del peer_data['PublicKey']

        # Handle renaming: write to new file and remove old if requested
        if new_name and new_name != peer_name:
            # Validate new name
            from utils.validators import validate_peer_name
            validate_peer_name(new_name)
            new_peer_path = os.path.join(self.base_dir, interface, f"{new_name}.conf")
            if os.path.exists(new_peer_path):
                raise ValueError("A peer with the new name already exists")

            write_config(new_peer_path, peer_config)
            os.remove(peer_path)
        else:
            write_config(peer_path, peer_config)

        # Sync final interface config after update/rename
        self._sync_interface(interface)
    
    def delete_peer(self, interface: str, peer_name: str) -> None:
        """Delete a specific peer."""
        peer_path = os.path.join(self.base_dir, interface, f"{peer_name}.conf")
        
        if not os.path.exists(peer_path):
            raise FileNotFoundError("Peer not found")
        os.remove(peer_path)

        # Sync final interface config after deletion
        self._sync_interface(interface)
