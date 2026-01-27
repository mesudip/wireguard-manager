
import {
    Interface, DiffResult, ConfigPeer, StatePeer, InterfaceState, HostInfo,
    ApiInterface, ApiPeer, ApiInterfaceState, ApiConfigDiff, ApiStateDiff, ApiInterfaceListResponse
} from '../types';

const API_BASE_URL = 'https://test1.gateway.sireto.net/api';

const apiFetch = async (url: string, options?: RequestInit) => {
    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            let errorDetails = `Request failed: ${response.status} ${response.statusText}`;
            try {
                // Try to get more specific error from JSON body
                const errorData = await response.json();
                errorDetails = errorData.error || errorData.details || JSON.stringify(errorData);
            } catch (e) {
                // Ignore JSON parse error, use the status text as fallback
            }
            throw new Error(errorDetails);
        }

        const contentLength = response.headers.get('Content-Length');
        if (response.status === 204 || (contentLength && parseInt(contentLength, 10) === 0)) {
            return { success: true };
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        }
        
        throw new Error(`Unexpected content type: ${contentType}. Expected a JSON response.`);

    } catch (error) {
        console.error("API Fetch Error:", url, error);
        throw error;
    }
};


// --- Data Transformers ---

const transformInterface = (apiIface: ApiInterface): Interface => ({
    name: apiIface.name,
    publicKey: apiIface.public_key,
    address: apiIface.address,
    listenPort: parseInt(apiIface.listen_port as any, 10), 
});

const transformConfigPeer = (apiPeer: ApiPeer): ConfigPeer => ({
    name: apiPeer.name,
    publicKey: apiPeer.public_key,
    privateKey: apiPeer.private_key,
    allowedIPs: apiPeer.allowed_ips,
    endpoint: apiPeer.endpoint,
});

const transformStatePeer = (apiPeerState: any): StatePeer => ({
    publicKey: apiPeerState.public_key,
    endpoint: apiPeerState.endpoint,
    allowedIPs: apiPeerState.allowed_ips,
    latestHandshake: apiPeerState.latest_handshake,
    transferRx: apiPeerState.transfer_rx,
    transferTx: apiPeerState.transfer_tx,
});


const transformInterfaceState = (apiState: ApiInterfaceState): InterfaceState => ({
    name: apiState.interface,
    publicKey: apiState.public_key,
    listenPort: apiState.listening_port,
    peers: apiState.peers.map(transformStatePeer),
});


// --- API Service Implementation ---

export const getInterfaces = async (): Promise<{ interfaces: Interface[], hostInfo: HostInfo }> => {
    const response: ApiInterfaceListResponse = await apiFetch(`${API_BASE_URL}/interfaces`);
    
    const interfaceNames = response.wireguard;
    
    const interfaceDetailsPromises = interfaceNames.map(name =>
        apiFetch(`${API_BASE_URL}/interfaces/${name}`) as Promise<ApiInterface>
    );
    
    const apiInterfaces = await Promise.all(interfaceDetailsPromises);
    
    return {
        interfaces: apiInterfaces.map(transformInterface),
        hostInfo: response.host
    };
};

export const createInterface = async (newInterface: { name: string, address: string, listen_port: string }): Promise<Interface> => {
     const data: ApiInterface = await apiFetch(`${API_BASE_URL}/interfaces`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newInterface),
    });
    return transformInterface(data);
};

export const deleteInterface = async (interfaceName: string): Promise<{success: boolean}> => {
    return apiFetch(`${API_BASE_URL}/interfaces/${encodeURIComponent(interfaceName)}`, {
        method: 'DELETE'
    });
};

export const getPeers = async (interfaceName: string): Promise<ConfigPeer[]> => {
    const data: ApiPeer[] = await apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/peers`);
    return data.map(transformConfigPeer);
};

export const addPeer = async (interfaceName: string, peer: { name: string, allowed_ips: string, endpoint?: string, public_key?: string }): Promise<ConfigPeer> => {
    const data: ApiPeer = await apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/peers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(peer),
    });
    return transformConfigPeer(data);
};

export const updatePeer = async (interfaceName: string, peerName: string, peerData: { allowed_ips?: string, endpoint?: string, public_key?: string }): Promise<{success: boolean}> => {
    return apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/peers/${encodeURIComponent(peerName)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(peerData)
    });
};

export const deletePeer = async (interfaceName: string, peerName: string): Promise<{success: boolean}> => {
    return apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/peers/${encodeURIComponent(peerName)}`, {
        method: 'DELETE'
    });
};

export const getInterfaceState = async (interfaceName: string): Promise<InterfaceState> => {
    const data: ApiInterfaceState = await apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/state`);
    return transformInterfaceState(data);
};

export const getConfigDiff = async (interfaceName: string): Promise<DiffResult> => {
    const data: ApiConfigDiff = await apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/config/diff`);
    return { diff: data.diff, hasChanges: !!data.diff && data.diff.trim() !== '' };
};

export const getStateDiff = async (interfaceName: string): Promise<DiffResult> => {
    const data: ApiStateDiff = await apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/state/diff`);
    return { diff: data.diff, hasChanges: !!data.diff && data.diff.trim() !== '' };
};

export const applyConfig = async (interfaceName: string): Promise<{ success: boolean }> => {
    return apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/config/apply`, { method: 'POST' });
};

export const syncConfig = async (interfaceName: string): Promise<{ success: boolean }> => {
    return apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/config/sync`, { method: 'POST' });
};

export const resetConfig = async (interfaceName: string): Promise<{ success: boolean }> => {
    return apiFetch(`${API_BASE_URL}/interfaces/${interfaceName}/config/reset`, { method: 'POST' });
};

export const updateHostIPs = async (ips: string[]): Promise<HostInfo> => {
    return apiFetch(`${API_BASE_URL}/host/info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ips: ips })
    });
};

export const rescanHostIPs = async (): Promise<HostInfo> => {
    return apiFetch(`${API_BASE_URL}/host/info/rescan`, {
        method: 'POST'
    });
};