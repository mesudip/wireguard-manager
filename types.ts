
// The rich, merged object for UI display
export interface Peer {
    name: string;
    publicKey: string;
    allowedIPs: string;
    endpoint: string;
    latestHandshake: string; // Formatted string
    transfer: {
        received: string; // Formatted string
        sent: string; // Formatted string
    };
}

// Represents a configured peer from /interfaces/{iface}/peers
export interface ConfigPeer {
    name: string;
    publicKey: string;
    allowedIPs: string;
    endpoint: string | null;
}

// Represents a live peer from the /interfaces/{iface}/state endpoint
export interface StatePeer {
    publicKey: string;
    endpoint: string;
    allowedIPs: string;
    latestHandshake: number; // Unix timestamp
    transferRx: number; // Bytes
    transferTx: number; // Bytes
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

// --- API Response Types (snake_case) ---

export interface ApiInterface {
    name: string;
    public_key: string;
    address: string;
    listen_port: number;
}

export interface ApiPeer {
    name: string;
    public_key: string;
    allowed_ips: string;
    endpoint: string | null;
}

export interface ApiPeerState {
    public_key: string;
    endpoint: string;
    allowed_ips: string;
    latest_handshake: number;
    transfer_rx: number;
    transfer_tx: number;
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
