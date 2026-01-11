import re
import ipaddress
from typing import Any
from exceptions.wireguard_exceptions import ConfigurationException

def validate_interface_name(name: str):
    if not name:
        raise ConfigurationException("Interface name is required")
    
    # WireGuard interface names must be between 1 and 15 characters
    if len(name) > 15:
        raise ConfigurationException("Interface name must be at most 15 characters")
    
    # Must start with a letter and contain only alphanumeric characters, underscores, or dashes
    # Most Linux systems are strict about this. 
    # Let's enforce: start with letter, then alphanumeric/underscore/dash.
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        raise ConfigurationException(
            f"Invalid interface name '{name}'. Must start with a letter and contain only alphanumeric characters, underscores, or dashes."
        )

def validate_ip_address(address: str, allow_multiple: bool = False):
    if not address:
        return
    
    if not allow_multiple and ',' in address:
        raise ConfigurationException("Multiple IP addresses are not allowed in this field")

    # Support multiple comma-separated IP addresses if allowed
    addresses = [a.strip() for a in address.split(',')]
    
    for addr in addresses:
        if not addr:
            continue
        try:
            # Check if it's a valid IPv4 or IPv6 interface (address/prefix)
            ipaddress.ip_interface(addr)
        except ValueError as e:
            raise ConfigurationException(f"Invalid IP address format '{addr}': {str(e)}")

def validate_port(port: Any):
    if port is None:
        return
    
    try:
        p = int(port)
        if not (1 <= p <= 65535):
            raise ValueError()
    except (ValueError, TypeError):
        raise ConfigurationException(f"Invalid port '{port}'. Must be an integer between 1 and 65535.")

def validate_endpoint(endpoint: str):
    """
    Validate WireGuard endpoint format (address:port).
    Supports IPv4, IPv6 (with brackets), and hostnames.
    """
    if not endpoint:
        return

    # Check for port at the end
    if ':' not in endpoint:
        raise ConfigurationException(f"Invalid endpoint '{endpoint}'. Port is required (e.g., address:port).")

    # Handle IPv6 with brackets [addr]:port
    if endpoint.startswith('['):
        if ']:' not in endpoint:
            raise ConfigurationException(f"Invalid IPv6 endpoint '{endpoint}'. Must be in [address]:port format.")
        address_part = endpoint[1:endpoint.find(']:')]
        port_part = endpoint[endpoint.find(']:')+2:]
        
        try:
            ipaddress.IPv6Address(address_part)
        except ValueError:
            raise ConfigurationException(f"Invalid IPv6 address in endpoint: {address_part}")
    else:
        # IPv4 or Hostname: address:port
        # Note: IPv6 without brackets is ambiguous if it contains multiple colons
        parts = endpoint.rsplit(':', 1)
        address_part = parts[0]
        port_part = parts[1]

        # Basic hostname/IPv4 check
        if not address_part:
            raise ConfigurationException(f"Invalid endpoint '{endpoint}'. Address part is missing.")
        
        # IPv6 without brackets is ambiguous and often rejected by wg tools
        if ':' in address_part:
            raise ConfigurationException(f"Invalid endpoint '{endpoint}'. IPv6 addresses must be wrapped in square brackets (e.g., [address]:port).")
        
        # If it's not an IP, we assume it's a hostname (basic check)
        try:
            ipaddress.ip_address(address_part)
        except ValueError:
            # Check if it looks like a valid hostname
            if not re.match(r'^[a-zA-Z0-9.-]+$', address_part):
                 raise ConfigurationException(f"Invalid address in endpoint: {address_part}")

    validate_port(port_part)
