// The rich, merged object for UI display
export interface Peer {
    name: string;
    publicKey: string;
    privateKey: string | null;
    allowedIPs: string;
    endpoint: string;
    liveEndpoint?: string;
    persistentKeepalive: string;
    latestHandshake: string; // Formatted string (e.g., "22 hours, 32 minutes, 35 seconds")
    latestHandshakeValue: number; // For sorting (seconds elapsed since last handshake)
    transfer: {
        received: string; // Formatted string (e.g., "15.97 MiB")
        sent: string; // Formatted string (e.g., "14.75 MiB")
    };
    transferValue: {
        received: number; // Bytes (for sorting)
        sent: number;    // Bytes (for sorting)
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
    latestHandshake: number;
    transferRx?: number;
    transferTx?: number;
    transfer?: string;
}

export interface Interface {
    name: string;
    publicKey: string;
    address: string;
    listenPort: number;
    postUp?: string | null;
    postDown?: string | null;
    dns?: string | null;
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

export interface ConfigDiffPeer {
    name: string;
    publicKey: string;
    allowedIPs: string;
    endpoint: string | null;
    persistentKeepalive: string | null;
}

export interface ConfigDiffData {
    peers: ConfigDiffPeer[];
}

export interface ConfigDiffResult {
    currentConfig: ConfigDiffData;
    folderConfig: ConfigDiffData;
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
    post_up?: string | null;
    post_down?: string | null;
    dns?: string | null;
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
    latest_handshake: number;
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

export interface ApiConfigDiffStructured {
    current_config: {
        peers: Array<{
            name: string;
            public_key: string;
            allowed_ips: string;
            endpoint?: string;
            persistent_keepalive?: string;
        }>;
    };
    folder_config: {
        peers: Array<{
            name: string;
            public_key: string;
            allowed_ips: string;
            endpoint?: string;
            persistent_keepalive?: string;
        }>;
    };
}

export interface ApiStateDiff {
    diff: string;
    status: string;
}
