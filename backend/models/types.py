"""TypedDict definitions for WireGuard API data structures."""

from typing import TypedDict, List, Optional, Dict, Any


class InterfaceConfig(TypedDict):
    """WireGuard [Interface] section configuration."""
    PrivateKey: str
    Address: str
    ListenPort: str


class PeerConfig(TypedDict):
    """WireGuard [Peer] section configuration."""
    PublicKey: str
    AllowedIPs: str
    Endpoint: Optional[str]
    PersistentKeepalive: Optional[str]


class WireGuardConfig(TypedDict):
    """Complete WireGuard configuration file structure."""
    Interface: InterfaceConfig
    Peers: List[PeerConfig]


class InterfaceResponse(TypedDict):
    """Response for interface creation/retrieval."""
    name: str
    public_key: str
    address: str
    listen_port: str


class InterfaceDetailResponse(InterfaceResponse):
    """Detailed interface response with full config."""
    config: WireGuardConfig


class PeerResponse(TypedDict):
    """Response for peer operations."""
    name: str
    public_key: str
    allowed_ips: str
    endpoint: str


class PeerStateInfo(TypedDict, total=False):
    """Live peer state from wg command."""
    public_key: str
    endpoint: Optional[str]
    allowed_ips: Optional[str]
    latest_handshake: Optional[str]
    transfer_rx: Optional[str]
    transfer_tx: Optional[str]
    persistent_keepalive: Optional[str]


class InterfaceState(TypedDict, total=False):
    """Live interface state with all peers."""
    interface: str
    status: str  # active, inactive, not_found
    message: Optional[str]
    peers: List[PeerStateInfo]


class DiffResponse(TypedDict, total=False):
    """Diff comparison result."""
    diff: str
    status: str
    message: Optional[str]


class ErrorResponse(TypedDict, total=False):
    """Error response with optional output."""
    error: str
    output: Optional[str]


class SuccessResponse(TypedDict, total=False):
    """Success response with optional path."""
    message: str
    path: Optional[str]
