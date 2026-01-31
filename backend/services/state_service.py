import os
import json
import subprocess
import difflib
import ipaddress
from typing import List, Dict, Any, Optional
from models.types import InterfaceState, PeerStateInfo, WireGuardConfig
from services.config import parse_config
from services.crypto import get_public_key
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
                
                if line.startswith('interface:'):
                    pass # We already have interface name
                elif line.startswith('peer:'):
                    if current_peer:
                        state['peers'].append(current_peer)
                    current_peer = {"public_key": line.split(':', 1)[1].strip()}
                elif ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    if current_peer:
                        key = key.replace(' ', '_')
                        # Convert latest_handshake to integer
                        if key == 'latest_handshake':
                            try:
                                current_peer[key] = int(value.strip())
                            except (ValueError, TypeError):
                                current_peer[key] = 0
                        # Parse transfer data: "X bytes received, Y bytes sent"
                        elif key == 'transfer':
                            rx_bytes, tx_bytes = self._parse_transfer(value.strip())
                            current_peer['transfer_rx'] = rx_bytes
                            current_peer['transfer_tx'] = tx_bytes
                        else:
                            current_peer[key] = value.strip()
                    else:
                        # Interface level property
                        if key == 'public key':
                            state['public_key'] = value.strip()
                        elif key == 'listening port':
                            state['listening_port'] = value.strip()
            
            if current_peer:
                state['peers'].append(current_peer)
            
            # Fetch IP address as well
            state['address'] = self._get_interface_address(interface)
            
            state['status'] = 'active'
            
            # Capture warnings from stderr
            if result.stderr:
                state['warnings'] = result.stderr.decode()
                
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
    
    def _get_interface_address(self, interface: str) -> Optional[str]:
        """Get IP address of interface using ip addr show."""
        try:
            result = run_command(["ip", "-j", "addr", "show", interface])
            data = json.loads(result.stdout.decode())
            if data and "addr_info" in data[0]:
                for addr in data[0]["addr_info"]:
                    if addr.get("family") == "inet":
                        return f"{addr.get('local')}/{addr.get('prefixlen')}"
            return None
        except Exception:
            return None

    def _parse_transfer(self, transfer_str: str) -> tuple[int, int]:
        """Parse transfer string like '15.97 MiB received, 14.75 MiB sent' into (rx_bytes, tx_bytes)."""
        rx_bytes = 0
        tx_bytes = 0
        
        # Unit conversion factors (case-insensitive)
        unit_factors = {
            'b': 1,
            'kib': 1024,
            'mib': 1024 ** 2,
            'gib': 1024 ** 3,
            'tib': 1024 ** 4,
            'kb': 1000,
            'mb': 1000 ** 2,
            'gb': 1000 ** 3,
            'tb': 1000 ** 4,
        }
        
        try:
            # Expected format: "15.97 MiB received, 14.75 MiB sent"
            parts = transfer_str.split(',')
            for part in parts:
                part = part.strip()
                if 'received' in part.lower():
                    rx_bytes = self._parse_bytes_with_unit(part, unit_factors)
                elif 'sent' in part.lower():
                    tx_bytes = self._parse_bytes_with_unit(part, unit_factors)
        except (ValueError, IndexError):
            pass
        
        return rx_bytes, tx_bytes

    def _parse_bytes_with_unit(self, value_str: str, unit_factors: dict) -> int:
        """Parse a string like '15.97 MiB' into bytes."""
        try:
            # Remove 'received' or 'sent' keywords
            value_str = value_str.replace('received', '').replace('sent', '').strip().lower()
            
            # Split into number and unit parts
            parts = value_str.split()
            if len(parts) < 1:
                return 0
            
            # Get the numeric value
            numeric_value = float(parts[0])
            
            # Get the unit if present
            if len(parts) >= 2:
                unit = parts[1].lower()
                factor = unit_factors.get(unit, 1)
                return int(numeric_value * factor)
            else:
                # If no unit, assume bytes
                return int(numeric_value)
        except (ValueError, IndexError):
            return 0


    def _normalize_allowed_ips(self, allowed_ips: Optional[str]) -> Optional[str]:
        """Normalize AllowedIPs into a canonical sorted comma-separated string."""
        if not allowed_ips:
            return allowed_ips
        
        normalized = []
        for part in allowed_ips.split(','):
            part = part.strip()
            if not part:
                continue
            try:
                # Use ip_network to handle both bare IPs and CIDR
                # strict=False allows host bits to be set, which WireGuard ignores anyway
                network = ipaddress.ip_network(part, strict=False)
                normalized.append(str(network))
            except ValueError:
                # If it's invalid, just keep it as is (should have been validated anyway)
                normalized.append(part)
        
        return ",".join(sorted(normalized))

    def _get_comparable_state(self, interface: str) -> Dict[str, Any]:
        """Normalize live state into a comparable format."""
        state = self.get_state(interface)
        if state.get('status') == 'not_found':
            return {}

        normalized = {
            "Interface": {
                "Address": state.get('address'),
                "ListenPort": state.get('listening_port'),
                "PublicKey": state.get('public_key')
            },
            "Peers": []
        }

        for peer in state.get('peers', []):
            normalized_peer = {
                "PublicKey": peer.get('public_key'),
                "AllowedIPs": self._normalize_allowed_ips(peer.get('allowed_ips')),
                "Endpoint": peer.get('endpoint'),
                # PersistentKeepalive might be in peers if configured
                "PersistentKeepalive": peer.get('persistent_keepalive')
            }
            # Remove None values
            normalized_peer = {k: v for k, v in normalized_peer.items() if v is not None}
            normalized["Peers"].append(normalized_peer)

        # Sort peers by PublicKey for consistent diff
        normalized["Peers"].sort(key=lambda x: x.get('PublicKey', ''))
        
        return normalized

    def _get_comparable_config(self, config: WireGuardConfig) -> Dict[str, Any]:
        """Normalize config into a comparable format."""
        # Derive public key from private key
        private_key = config['Interface'].get('PrivateKey')
        public_key = None
        if private_key:
            public_key, _ = get_public_key(private_key)

        normalized = {
            "Interface": {
                "Address": config['Interface'].get('Address'),
                "ListenPort": config['Interface'].get('ListenPort'),
                "PublicKey": public_key
            },
            "Peers": []
        }

        for peer in config.get('Peers', []):
            normalized_peer = {
                "PublicKey": peer.get('PublicKey'),
                "AllowedIPs": self._normalize_allowed_ips(peer.get('AllowedIPs')),
                "Endpoint": peer.get('Endpoint'),
                "PersistentKeepalive": peer.get('PersistentKeepalive')
            }
            # Remove None values
            normalized_peer = {k: v for k, v in normalized_peer.items() if v is not None}
            normalized["Peers"].append(normalized_peer)

        # Sort peers by PublicKey
        normalized["Peers"].sort(key=lambda x: x.get('PublicKey', ''))

        return normalized

    def get_state_diff(self, interface: str) -> Dict[str, Any]:
        """Get diff between wg command output and current conf file."""
        final_config_path = os.path.join(self.base_dir, f"{interface}.conf")
        
        # Get config
        config: WireGuardConfig = {"Interface": {}, "Peers": []}
        if os.path.exists(final_config_path):
            parsed = parse_config(final_config_path)
            if parsed:
                config = parsed
        
        comparable_config = self._get_comparable_config(config)
        comparable_state = self._get_comparable_state(interface)

        config_lines = json.dumps(comparable_config, indent=2, sort_keys=True).splitlines()
        state_lines = json.dumps(comparable_state, indent=2, sort_keys=True).splitlines()
        
        diff = list(difflib.unified_diff(
            config_lines, state_lines,
            lineterm='',
            fromfile='config',
            tofile='state'
        ))
        
        result_dict = {
            "diff": '\n'.join(diff),
            "status": "success"
        }
        
        return result_dict
