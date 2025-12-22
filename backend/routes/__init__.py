"""Routes package for WireGuard API."""

from .interface_routes import create_interface_routes
from .peer_routes import create_peer_routes
from .config_routes import create_config_routes
from .state_routes import create_state_routes

__all__ = [
    "create_interface_routes",
    "create_peer_routes",
    "create_config_routes",
    "create_state_routes",
]
