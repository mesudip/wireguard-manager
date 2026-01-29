
import React, { useState, useMemo } from 'react';
import { Peer } from '../../types';
import PeerRow from './PeerRow';

interface PeerTableProps {
    peers: Peer[];
    interfaceAddress?: string;
    onShare: (peer: Peer) => void;
    onEdit: (peer: Peer) => void;
    onDelete: (peer: Peer) => void;
}

type SortField = 'name' | 'allowedIPs' | 'handshake' | 'transfer';
type SortDirection = 'asc' | 'desc';

const PeerTable: React.FC<PeerTableProps> = ({ peers, interfaceAddress, onShare, onEdit, onDelete }) => {
    const [sortField, setSortField] = useState<SortField>('name');
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

    // Helper to get the primary IP for sorting (matching interface subnet if possible)
    const getSortIP = (allowedIPs: string): string => {
        if (!allowedIPs) return '';
        const ips = allowedIPs.split(',').map(s => s.trim());
        if (ips.length <= 1 || !interfaceAddress) return ips[0] || '';

        // Try to find an IP in the same /24 or /16 as the interface
        // This is a simple heuristic since we don't have a full CIDR library here
        const ifaceParts = interfaceAddress.split('/')[0].split('.');
        if (ifaceParts.length === 4) {
            const ifacePrefix24 = ifaceParts.slice(0, 3).join('.');
            const match = ips.find(ip => ip.startsWith(ifacePrefix24));
            if (match) return match;
        }

        return ips[0];
    };

    const sortedPeers = useMemo(() => {
        const sorted = [...peers];
        sorted.sort((a, b) => {
            let comparison = 0;
            switch (sortField) {
                case 'name':
                    comparison = a.name.localeCompare(b.name);
                    break;
                case 'allowedIPs':
                    comparison = getSortIP(a.allowedIPs).localeCompare(getSortIP(b.allowedIPs), undefined, { numeric: true });
                    break;
                case 'handshake':
                    comparison = a.latestHandshakeValue - b.latestHandshakeValue;
                    break;
                case 'transfer':
                    const totalA = a.transferValue.received + a.transferValue.sent;
                    const totalB = b.transferValue.received + b.transferValue.sent;
                    comparison = totalA - totalB;
                    break;
            }
            return sortDirection === 'asc' ? comparison : -comparison;
        });
        return sorted;
    }, [peers, sortField, sortDirection, interfaceAddress]);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection('asc');
        }
    };

    const SortIndicator = ({ field }: { field: SortField }) => {
        return (
            <span className={`ml-1 inline-block transition-opacity duration-200 ${sortField === field ? 'opacity-100' : 'opacity-0'}`}>
                {sortDirection === 'asc' ? '↑' : '↓'}
            </span>
        );
    };

    return (
        <div className="overflow-x-auto bg-gray-50/50 dark:bg-gray-900/50 rounded-lg border border-gray-200/50 dark:border-gray-700/50">
            <table className="min-w-full divide-y divide-gray-200/50 dark:divide-gray-700">
                <thead className="bg-gray-100/60 dark:bg-gray-800/60">
                    <tr>
                        <th 
                            scope="col" 
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-white"
                            onClick={() => handleSort('name')}
                        >
                            Name / Endpoint <SortIndicator field="name" />
                        </th>
                        <th 
                            scope="col" 
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-white"
                            onClick={() => handleSort('allowedIPs')}
                        >
                            Allowed IPs <SortIndicator field="allowedIPs" />
                        </th>
                        <th 
                            scope="col" 
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-white"
                            onClick={() => handleSort('handshake')}
                        >
                            Latest Handshake <SortIndicator field="handshake" />
                        </th>
                        <th 
                            scope="col" 
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-white"
                            onClick={() => handleSort('transfer')}
                        >
                            Transfer <SortIndicator field="transfer" />
                        </th>
                        <th scope="col" className="relative px-6 py-3">
                            <span className="sr-only">Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-200/50 dark:divide-gray-700/50">
                    {sortedPeers.map((peer) => (
                        <PeerRow 
                            key={peer.publicKey} 
                            peer={peer} 
                            onShare={onShare}
                            onEdit={onEdit}
                            onDelete={onDelete}
                        />
                    ))}
                </tbody>
            </table>
            {peers.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                    No peers configured for this interface.
                </div>
            )}
        </div>
    );
};

export default PeerTable;
