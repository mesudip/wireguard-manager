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

def validate_ip_address(address: str):
    if not address:
        return
    try:
        # Check if it's a valid IPv4 or IPv6 interface (address/prefix)
        ipaddress.ip_interface(address)
    except ValueError as e:
        raise ConfigurationException(f"Invalid IP address format: {str(e)}")

def validate_port(port: Any):
    if port is None:
        return
    
    try:
        p = int(port)
        if not (1 <= p <= 65535):
            raise ValueError()
    except (ValueError, TypeError):
        raise ConfigurationException(f"Invalid port '{port}'. Must be an integer between 1 and 65535.")
