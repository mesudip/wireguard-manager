"""TypedDict definitions for WireGuard API data structures."""

from typing import TypedDict, List, Optional, Dict, Any


class InterfaceConfig(TypedDict, total=False):
    """WireGuard [Interface] section configuration."""
    PrivateKey: str
    Address: str
    ListenPort: str
    PostUp: Optional[str]
    PostDown: Optional[str]
    DNS: Optional[str]


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


class CommandLog(TypedDict):
    """Log of executed system command."""
    command: str
    return_code: int
    stdout: str
    stderr: str


class HostInfo(TypedDict, total=False):
    """Host public IP information."""
    ips: List[str]
    manual: Optional[bool]
    message: Optional[str]
    error: Optional[str]
    updated_at: Optional[str]


class InterfaceListResponse(TypedDict):
    """Response for listing interfaces with host info."""
    host: HostInfo
    wireguard: List[str]


class InterfaceResponse(TypedDict, total=False):
    """Response for interface creation/retrieval."""
    name: str
    public_key: str
    address: str
    listen_port: str
    post_up: Optional[str]
    post_down: Optional[str]
    dns: Optional[str]
    warnings: Optional[str]
    commands: Optional[List[CommandLog]]


class InterfaceDetailResponse(InterfaceResponse):
    """Detailed interface response (same as InterfaceResponse, no config exposed)."""
    pass


class PeerResponse(TypedDict, total=False):
    """Response for peer operations."""
    name: str
    public_key: str
    private_key: Optional[str]
    allowed_ips: str
    endpoint: str
    persistent_keepalive: Optional[str]
    warnings: Optional[str]
    commands: Optional[List[CommandLog]]


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
    warnings: Optional[str]
    commands: Optional[List[CommandLog]]


class DiffResponse(TypedDict, total=False):
    """Diff comparison result."""
    diff: str
    status: str
    message: Optional[str]
    warnings: Optional[str]
    commands: Optional[List[CommandLog]]


class ErrorResponse(TypedDict, total=False):
    """Error response with optional output."""
    error: str
    output: Optional[str]


class SuccessResponse(TypedDict, total=False):
    """Success response with optional path."""
    message: str
    path: Optional[str]
    warnings: Optional[str]
    commands: Optional[List[CommandLog]]
