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

    const livePeersMap = new Map(interfaceState.peers.map(p => [p.publicKey, p]));
    const diffs: PeerDiff[] = [];

    peers.forEach(configPeer => {
        const livePeer = livePeersMap.get(configPeer.publicKey);
        const peerChanges: PeerDiff['changes'] = [];
        let hasStrictChanges = false;

        if (!livePeer) {
            peerChanges.push({ property: 'Status', configValue: 'Configured', liveValue: 'Not Live' });
            hasStrictChanges = true;
        } else {
            // Compare Allowed IPs with normalization
            const configAllowedIPs = normalizeAllowedIPs(configPeer.allowedIPs);
            const liveAllowedIPs = normalizeAllowedIPs(livePeer.allowedIPs);
            if (configAllowedIPs !== liveAllowedIPs) {
                peerChanges.push({ property: 'Allowed IPs', configValue: configPeer.allowedIPs, liveValue: livePeer.allowedIPs });
                hasStrictChanges = true;
            }

            // Compare Persistent Keepalive with normalization
            const configKeepalive = normalizeValue(configPeer.persistentKeepalive);
            const liveKeepalive = normalizeValue(livePeer.persistentKeepalive);
            if (configKeepalive !== liveKeepalive) {
                peerChanges.push({ property: 'Persistent Keepalive', configValue: configPeer.persistentKeepalive, liveValue: livePeer.persistentKeepalive });
                hasStrictChanges = true;
            }

            // Compare Endpoint with normalization
            const configEndpoint = normalizeValue(configPeer.endpoint);
            const liveEndpoint = normalizeValue(livePeer.endpoint);
            if (configEndpoint !== liveEndpoint) {
                peerChanges.push({ property: 'Endpoint', configValue: configPeer.endpoint, liveValue: livePeer.endpoint });
                // Endpoint change alone is not strict
            }
        }

        if (peerChanges.length > 0) {
            diffs.push({
                name: configPeer.name,
                publicKey: configPeer.publicKey,
                isStrict: hasStrictChanges,
                changes: peerChanges
            });
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
                    <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm overflow-x-auto border border-gray-300 dark:border-gray-700">
                        {peerDiffs.map((diff, idx) => (
                            <div key={diff.publicKey} className={idx > 0 ? 'mt-3 pt-3 border-t border-gray-300 dark:border-gray-700' : ''}>
                                <div className="text-blue-600 dark:text-cyan-400 mb-2 text-xs">
                                    {diff.name && <div>{diff.name}</div>}
                                    <div className="text-gray-600 dark:text-gray-500">{diff.publicKey}</div>
                                </div>
                                {diff.changes.map(change => (
                                    <div key={change.property} className="mb-1">
                                        <div className="text-red-600 dark:text-red-400">- {change.property}: {change.configValue || '(not set)'}</div>
                                        <div className="text-green-600 dark:text-green-400">+ {change.property}: {change.liveValue || '(not set)'}</div>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default StateDiff;
