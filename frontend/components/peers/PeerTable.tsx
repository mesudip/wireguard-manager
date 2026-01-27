
import React from 'react';
import { Peer } from '../../types';
import PeerRow from './PeerRow';

interface PeerTableProps {
    peers: Peer[];
    onShare: (peer: Peer) => void;
    onEdit: (peer: Peer) => void;
    onDelete: (peer: Peer) => void;
}

const PeerTable: React.FC<PeerTableProps> = ({ peers, onShare, onEdit, onDelete }) => {
    return (
        <div className="overflow-x-auto bg-gray-50/50 dark:bg-gray-900/50 rounded-lg border border-gray-200/50 dark:border-gray-700/50">
            <table className="min-w-full divide-y divide-gray-200/50 dark:divide-gray-700">
                <thead className="bg-gray-100/60 dark:bg-gray-800/60">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name / Endpoint</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Allowed IPs</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Latest Handshake</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Transfer</th>
                        <th scope="col" className="relative px-6 py-3">
                            <span className="sr-only">Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-200/50 dark:divide-gray-700/50">
                    {peers.map((peer) => (
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
