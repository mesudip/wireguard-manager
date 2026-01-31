import React from 'react';
import { Peer, InterfaceState, HostInfo } from '../types';
import { formatBytes, formatHandshake } from '../utils';
import { CheckIcon, ExclamationIcon, UploadIcon } from './icons/Icons';

interface StateDiffProps {
    peers: Peer[];
    interfaceState: InterfaceState | null;
    hostInfo: HostInfo | null;
    interfaceAddress: string;
    onApplyConfig: () => void;
    isApplying: boolean;
}

type PeerDiff = {
    name: string;
    publicKey: string;
    allowedIPs: string;
    status: 'not-live' | 'synced' | 'modified';
    isStrict: boolean;
    changes: {
        property: string;
        configValue: any;
        liveValue: any;
    }[];
};

const normalizeAllowedIPs = (ips: string): string => {
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

const calculateDiff = (peers: Peer[], interfaceState: InterfaceState | null): PeerDiff[] => {
    if (!interfaceState) return [];

    const diffs: PeerDiff[] = [];
    const processedConfig = new Set<number>();

    // Helper to find matching peer intelligently
    const findMatchingLivePeer = (configPeer: Peer, livePeers: any[]) => {
        // First try exact public key match
        let match = livePeers.find(p => p.publicKey === configPeer.publicKey);
        if (match) return match;
        
        // Then try name match (excluding auto-generated names)
        if (configPeer.name && !/^peer\d+$/.test(configPeer.name)) {
            // Can't match by name in live state, so skip this
        }
        
        // Finally try allowed IPs match
        const normalizedIPs = normalizeAllowedIPs(configPeer.allowedIPs);
        if (normalizedIPs) {
            match = livePeers.find(p => normalizeAllowedIPs(p.allowedIPs) === normalizedIPs);
            if (match) return match;
        }
        
        return null;
    };

    peers.forEach((configPeer, configIdx) => {
        const livePeer = findMatchingLivePeer(configPeer, interfaceState.peers);
        const peerChanges: PeerDiff['changes'] = [];
        let hasStrictChanges = false;

        if (!livePeer) {
            // Peer is configured but not live - collect only set fields
            const notLiveChanges: PeerDiff['changes'] = [];
            
            if (configPeer.allowedIPs) {
                notLiveChanges.push({ property: 'Allowed IPs', configValue: configPeer.allowedIPs, liveValue: null });
            }
            if (configPeer.endpoint) {
                notLiveChanges.push({ property: 'Endpoint', configValue: configPeer.endpoint, liveValue: null });
            }
            if (configPeer.persistentKeepalive) {
                notLiveChanges.push({ property: 'Persistent Keepalive', configValue: configPeer.persistentKeepalive, liveValue: null });
            }
            
            diffs.push({
                name: configPeer.name,
                publicKey: configPeer.publicKey,
                allowedIPs: configPeer.allowedIPs,
                status: 'not-live',
                isStrict: true,
                changes: notLiveChanges
            });
            processedConfig.add(configIdx);
        } else {
            processedConfig.add(configIdx);

            // Compare Allowed IPs with normalization
            const configAllowedIPs = normalizeAllowedIPs(configPeer.allowedIPs);
            const liveAllowedIPs = normalizeAllowedIPs(livePeer.allowedIPs);
            if (configAllowedIPs !== liveAllowedIPs) {
                peerChanges.push({ property: 'Allowed IPs', configValue: configPeer.allowedIPs, liveValue: livePeer.allowedIPs });
                hasStrictChanges = true;
            }

            // Compare Public Key if different (peer was re-keyed)
            if (configPeer.publicKey !== livePeer.publicKey) {
                peerChanges.push({ property: 'Public Key', configValue: configPeer.publicKey, liveValue: livePeer.publicKey });
                hasStrictChanges = true;
            }

            // Compare Persistent Keepalive with normalization
            const configKeepalive = normalizeValue(configPeer.persistentKeepalive);
            const liveKeepalive = normalizeValue(livePeer.persistentKeepalive);
            if (configKeepalive !== liveKeepalive) {
                peerChanges.push({ property: 'Persistent Keepalive', configValue: configPeer.persistentKeepalive, liveValue: livePeer.persistentKeepalive });
                hasStrictChanges = true;
            }

            // Compare Endpoint with normalization (non-critical)
            const configEndpoint = normalizeValue(configPeer.endpoint);
            const liveEndpoint = normalizeValue(livePeer.endpoint);
            if (configEndpoint !== liveEndpoint) {
                peerChanges.push({ property: 'Endpoint', configValue: configPeer.endpoint, liveValue: livePeer.endpoint });
                // Endpoint change alone is not strict
            }

            if (peerChanges.length > 0) {
                diffs.push({
                    name: configPeer.name,
                    publicKey: configPeer.publicKey,
                    allowedIPs: configPeer.allowedIPs,
                    status: 'modified',
                    isStrict: hasStrictChanges,
                    changes: peerChanges
                });
            }
        }
    });

    return diffs;
};


const StateDiff: React.FC<StateDiffProps> = ({ peers, interfaceState, hostInfo, interfaceAddress, onApplyConfig, isApplying }) => {
    const peerDiffs = calculateDiff(peers, interfaceState);
    const hasStrictDiff = peerDiffs.some(d => d.isStrict);

    const renderValue = (value: any) => {
        if (value === null || typeof value === 'undefined' || value === '') return <span className="text-gray-500">Not set</span>;
        return <span>{value}</span>;
    };

    return (
        <div className="space-y-6">
            {peerDiffs.length > 0 && (
                <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">Sync Status</h3>
                    {hasStrictDiff ? (
                        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500/30 rounded-lg p-4">
                            <div className="flex items-start mb-4">
                                <ExclamationIcon className="w-6 h-6 text-red-500 dark:text-red-400 mr-3 flex-shrink-0" />
                                <div className="flex-1">
                                    <p className="font-semibold text-red-800 dark:text-red-300">Out of Sync</p>
                                    <p className="text-sm text-red-700 dark:text-red-400">The live state has critical differences from the saved configuration. Apply the configuration to restore synchronization.</p>
                                </div>
                            </div>
                            <button 
                                onClick={onApplyConfig} 
                                disabled={isApplying} 
                                className="flex items-center bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <UploadIcon className="w-5 h-5 mr-2" />
                                {isApplying ? 'Applying...' : 'Apply Configuration'}
                            </button>
                        </div>
                    ) : (
                        <div className="flex items-center p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-500/30 rounded-lg">
                            <ExclamationIcon className="w-6 h-6 text-yellow-500 dark:text-yellow-400 mr-3" />
                            <div>
                                <p className="font-semibold text-yellow-800 dark:text-yellow-300">Minor Differences</p>
                                <p className="text-sm text-yellow-700 dark:text-yellow-400">The live state has non-critical differences (e.g., endpoint changes).</p>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {peerDiffs.length > 0 && (
                <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">Differences</h3>
                    <div className="flex items-center text-xs text-gray-600 dark:text-gray-400 mb-2">
                        <span className="text-red-600 dark:text-red-400">- config</span>
                        <span className="ml-3 text-green-600 dark:text-green-400">+ live state</span>
                    </div>
                    <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm overflow-x-auto border border-gray-300 dark:border-gray-700">
                        {peerDiffs.map((diff, idx) => {
                            // Don't show generated peer names like "peer1", "peer2" etc
                            const isGeneratedName = /^peer\d+$/.test(diff.name);
                            const displayName = isGeneratedName ? diff.allowedIPs : diff.name;
                            
                            return (
                                <div key={diff.publicKey} className={idx > 0 ? 'mt-3 pt-3 border-t border-gray-300 dark:border-gray-700' : ''}>
                                    <div className="text-blue-600 dark:text-cyan-400 mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className="font-bold text-base">{displayName}</span>
                                            {diff.status === 'not-live' && (
                                                <span className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 px-2 py-0.5 rounded text-xs font-semibold">Not Live</span>
                                            )}
                                            {diff.status === 'modified' && diff.isStrict && (
                                                <span className="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 px-2 py-0.5 rounded text-xs font-semibold">Out of Sync</span>
                                            )}
                                            {diff.status === 'modified' && !diff.isStrict && (
                                                <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-2 py-0.5 rounded text-xs font-semibold">Minor Diff</span>
                                            )}
                                        </div>
                                        <div className="text-gray-600 dark:text-gray-500 text-xs">{diff.publicKey}</div>
                                    </div>
                                    {diff.status === 'not-live' ? (
                                        // For not-live peers, show values normally (not as red/green diff)
                                        diff.changes.map(change => (
                                            <div key={change.property} className="mb-1 text-gray-700 dark:text-gray-300">
                                                {change.property}: {change.configValue}
                                            </div>
                                        ))
                                    ) : (
                                        // For modified peers, show as diff
                                        diff.changes.map(change => (
                                            <div key={change.property} className="mb-1">
                                                {change.configValue !== null && (
                                                    <div className="text-red-600 dark:text-red-400">- {change.property}: {change.configValue || '(not set)'}</div>
                                                )}
                                                {change.liveValue !== null && (
                                                    <div className="text-green-600 dark:text-green-400">+ {change.property}: {change.liveValue || '(not set)'}</div>
                                                )}
                                            </div>
                                        ))
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default StateDiff;
