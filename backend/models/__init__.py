"""Models package for WireGuard API."""

from .types import (
    InterfaceConfig,
    PeerConfig,
    WireGuardConfig,
    InterfaceResponse,
    InterfaceDetailResponse,
    PeerResponse,
    PeerStateInfo,
    InterfaceState,
    DiffResponse,
    ConfigDiffPeer,
    ConfigDiffData,
    ConfigDiffResponse,
    ErrorResponse,
    SuccessResponse,
)

__all__ = [
    "InterfaceConfig",
    "PeerConfig",
    "WireGuardConfig",
    "InterfaceResponse",
    "InterfaceDetailResponse",
    "PeerResponse",
    "PeerStateInfo",
    "InterfaceState",
    "DiffResponse",
    "ConfigDiffPeer",
    "ConfigDiffData",
    "ConfigDiffResponse",
    "ErrorResponse",
    "SuccessResponse",
]
