// The rich, merged object for UI display
export interface Peer {
    name: string;
    publicKey: string;
    privateKey: string | null;
    allowedIPs: string;
    endpoint: string;
    liveEndpoint?: string;
    persistentKeepalive: string;
    latestHandshake: string; // Formatted string
    latestHandshakeValue: number; // For sorting (epoch timestamp)
    transfer: {
        received: string; // Formatted string
        sent: string; // Formatted string
    };
    transferValue: {
        received: number; // For sorting
        sent: number;    // For sorting
    };
}

// Represents a configured peer from /interfaces/{iface}/peers
export interface ConfigPeer {
    name: string;
    publicKey: string;
    privateKey: string | null;
    allowedIPs: string;
    endpoint: string | null;
    persistentKeepalive: string | null;
}

// Represents a live peer from the /interfaces/{iface}/state endpoint
export interface StatePeer {
    publicKey: string;
    endpoint: string;
    allowedIPs: string;
    persistentKeepalive: string | null;
    latestHandshake: string | number;
    transferRx?: number;
    transferTx?: number;
    transfer?: string;
}

export interface Interface {
    name: string;
    publicKey: string;
    address: string;
    listenPort: number;
}

export interface InterfaceState {
    name: string;
    publicKey: string;
    listenPort: number;
    peers: StatePeer[];
}

export interface DiffResult {
    diff: string;
    hasChanges: boolean;
}

export interface HostInfo {
    ips: string[];
    message?: string;
    manual?: boolean;
}


// --- API Response Types (snake_case) ---

export interface ApiInterface {
    name: string;
    public_key: string;
    address: string;
    listen_port: number;
}

export interface ApiInterfaceListResponse {
    host: HostInfo;
    wireguard: string[];
}

export interface ApiPeer {
    name: string;
    public_key: string;
    private_key: string | null;
    allowed_ips: string;
    endpoint: string | null;
    persistent_keepalive: string | null;
}

export interface ApiPeerState {
    public_key: string;
    endpoint: string;
    allowed_ips: string;
    persistent_keepalive: string | null;
    latest_handshake: string | number;
    transfer_rx?: number;
    transfer_tx?: number;
    transfer?: string;
}

export interface ApiInterfaceState {
    interface: string;
    public_key: string;
    listening_port: number;
    peers: ApiPeerState[];
}

export interface ApiConfigDiff {
    diff: string;
}

export interface ApiStateDiff {
    diff: string;
    status: string;
}
