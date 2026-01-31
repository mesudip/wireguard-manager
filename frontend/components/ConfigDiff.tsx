import React from 'react';
import { ConfigDiffPeer } from '../types';

interface ConfigDiffProps {
    currentConfig: { peers: ConfigDiffPeer[] };
    folderConfig: { peers: ConfigDiffPeer[] };
}

type PeerDiff = {
    name: string;
    publicKey: string;
    allowedIPs: string;
    status: 'added' | 'removed' | 'modified';
    changes: {
        property: string;
        currentValue: any;
        folderValue: any;
    }[];
};

const normalizeAllowedIPs = (ips: string | null): string => {
    if (!ips) return '';
    return ips.split(/[\s,]+/)
        .filter(Boolean)
        .map(ip => {
            // Normalize single IPs to include /32 or /128
            if (!ip.includes('/')) {
                return ip.includes(':') ? `${ip}/128` : `${ip}/32`;
            }
            return ip;
        })
        .sort()
        .join(',');
};

const normalizeValue = (value: any): string => {
    if (value === null || value === undefined || value === '') return '';
    return String(value).trim();
};

const calculateDiff = (currentConfig: { peers: ConfigDiffPeer[] }, folderConfig: { peers: ConfigDiffPeer[] }): PeerDiff[] => {
    const diffs: PeerDiff[] = [];
    const processedCurrent = new Set<number>();
    const processedFolder = new Set<number>();

    // Helper to match peers intelligently (by public key, name, or allowed IPs)
    const findMatchingPeer = (peer: ConfigDiffPeer, peerList: ConfigDiffPeer[]): ConfigDiffPeer | null => {
        // First try exact public key match
        let match = peerList.find(p => p.publicKey === peer.publicKey);
        if (match) return match;
        
        // Then try name match (excluding auto-generated names)
        if (peer.name && !/^peer\d+$/.test(peer.name)) {
            match = peerList.find(p => p.name === peer.name && !/^peer\d+$/.test(p.name));
            if (match) return match;
        }
        
        // Finally try allowed IPs match
        const normalizedIPs = normalizeAllowedIPs(peer.allowedIPs);
        if (normalizedIPs) {
            match = peerList.find(p => normalizeAllowedIPs(p.allowedIPs) === normalizedIPs);
            if (match) return match;
        }
        
        return null;
    };

    // Check peers in folder config (new or modified)
    folderConfig.peers.forEach((folderPeer, folderIdx) => {
        const currentPeer = findMatchingPeer(folderPeer, currentConfig.peers);
        const peerChanges: PeerDiff['changes'] = [];

        if (!currentPeer) {
            // Peer is being added - show all fields
            diffs.push({
                name: folderPeer.name,
                publicKey: folderPeer.publicKey,
                allowedIPs: folderPeer.allowedIPs,
                status: 'added',
                changes: [
                    { property: 'Allowed IPs', currentValue: null, folderValue: folderPeer.allowedIPs },
                    { property: 'Endpoint', currentValue: null, folderValue: folderPeer.endpoint },
                    { property: 'Persistent Keepalive', currentValue: null, folderValue: folderPeer.persistentKeepalive }
                ]
            });
            processedFolder.add(folderIdx);
        } else {
            // Mark as processed
            const currentIdx = currentConfig.peers.indexOf(currentPeer);
            processedCurrent.add(currentIdx);
            processedFolder.add(folderIdx);

            // Compare fields
            const currentAllowedIPs = normalizeAllowedIPs(currentPeer.allowedIPs);
            const folderAllowedIPs = normalizeAllowedIPs(folderPeer.allowedIPs);
            if (currentAllowedIPs !== folderAllowedIPs) {
                peerChanges.push({ property: 'Allowed IPs', currentValue: currentPeer.allowedIPs, folderValue: folderPeer.allowedIPs });
            }

            // Compare Public Key if different (peer was re-keyed)
            if (currentPeer.publicKey !== folderPeer.publicKey) {
                peerChanges.push({ property: 'Public Key', currentValue: currentPeer.publicKey, folderValue: folderPeer.publicKey });
            }

            const currentKeepalive = normalizeValue(currentPeer.persistentKeepalive);
            const folderKeepalive = normalizeValue(folderPeer.persistentKeepalive);
            if (currentKeepalive !== folderKeepalive) {
                peerChanges.push({ property: 'Persistent Keepalive', currentValue: currentPeer.persistentKeepalive, folderValue: folderPeer.persistentKeepalive });
            }

            const currentEndpoint = normalizeValue(currentPeer.endpoint);
            const folderEndpoint = normalizeValue(folderPeer.endpoint);
            if (currentEndpoint !== folderEndpoint) {
                peerChanges.push({ property: 'Endpoint', currentValue: currentPeer.endpoint, folderValue: folderPeer.endpoint });
            }

            if (peerChanges.length > 0) {
                diffs.push({
                    name: folderPeer.name,
                    publicKey: folderPeer.publicKey,
                    allowedIPs: folderPeer.allowedIPs,
                    status: 'modified',
                    changes: peerChanges
                });
            }
        }
    });

    // Check for peers only in current config (being removed)
    currentConfig.peers.forEach((currentPeer, currentIdx) => {
        if (!processedCurrent.has(currentIdx)) {
            diffs.push({
                name: currentPeer.name,
                publicKey: currentPeer.publicKey,
                allowedIPs: currentPeer.allowedIPs,
                status: 'removed',
                changes: [
                    { property: 'Allowed IPs', currentValue: currentPeer.allowedIPs, folderValue: null },
                    { property: 'Endpoint', currentValue: currentPeer.endpoint, folderValue: null },
                    { property: 'Persistent Keepalive', currentValue: currentPeer.persistentKeepalive, folderValue: null }
                ]
            });
        }
    });

    return diffs;
};

const ConfigDiff: React.FC<ConfigDiffProps> = ({ currentConfig, folderConfig }) => {
    const peerDiffs = calculateDiff(currentConfig, folderConfig);

    if (peerDiffs.length === 0) {
        return null;
    }

    return (
        <div className="space-y-3 mt-4">
            <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200">Differences</h4>
            <div className="flex items-center text-xs text-gray-600 dark:text-gray-400 mb-2">
                <span className="text-red-600 dark:text-red-400">- current.conf</span>
                <span className="ml-3 text-green-600 dark:text-green-400">+ managed folder</span>
            </div>
            <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm overflow-x-auto border border-gray-300 dark:border-gray-700">
                {peerDiffs.map((diff, idx) => {
                    // Don't show generated peer names like "peer1", "peer2" etc
                    const isGeneratedName = /^peer\d+$/.test(diff.name);
                    const displayName = isGeneratedName ? diff.allowedIPs : diff.name;
                    
                    return (
                        <div key={diff.publicKey} className={idx > 0 ? 'mt-3 pt-3 border-t border-gray-300 dark:border-gray-700' : ''}>
                            <div className="text-blue-600 dark:text-cyan-400 mb-2 text-xs">
                                <div className="flex items-center gap-2">
                                    <span className="font-semibold">{displayName}</span>
                                    {diff.status === 'added' && (
                                        <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2 py-0.5 rounded text-xs font-semibold">Added</span>
                                    )}
                                    {diff.status === 'removed' && (
                                        <span className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 px-2 py-0.5 rounded text-xs font-semibold">Removed</span>
                                    )}
                                </div>
                                <div className="text-gray-600 dark:text-gray-500">{diff.publicKey}</div>
                            </div>
                            {diff.changes.map(change => (
                                <div key={change.property} className="mb-1">
                                    {change.currentValue !== null && (
                                        <div className="text-red-600 dark:text-red-400">- {change.property}: {change.currentValue || '(not set)'}</div>
                                    )}
                                    {change.folderValue !== null && (
                                        <div className="text-green-600 dark:text-green-400">+ {change.property}: {change.folderValue || '(not set)'}</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default ConfigDiff;
