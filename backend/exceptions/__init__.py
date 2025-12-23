"""Custom exceptions for WireGuard Manager."""

from .wireguard_exceptions import (
    WireGuardException,
    CommandNotFoundException,
    PermissionDeniedException,
    InterfaceNotFoundException,
    PeerNotFoundException,
    ConfigurationException,
    StateException
)

__all__ = [
    'WireGuardException',
    'CommandNotFoundException',
    'PermissionDeniedException',
    'InterfaceNotFoundException',
    'PeerNotFoundException',
    'ConfigurationException',
    'StateException'
]
