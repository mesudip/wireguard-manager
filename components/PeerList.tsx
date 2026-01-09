
import React, { useState } from 'react';
import { Peer } from '../types';
import * as api from '../services/api';
import Modal from './Modal';
import { WifiIcon, ArrowSmDownIcon, ArrowSmUpIcon, PlusIcon } from './icons/Icons';

interface PeerListProps {
    peers: Peer[];
    refreshData: () => void;
    interfaceName: string;
}

const PeerList: React.FC<PeerListProps> = ({ peers, refreshData, interfaceName }) => {
    const [isAddModalOpen, setAddModalOpen] = useState(false);
    const [newPeerName, setNewPeerName] = useState('');
    const [newPeerAllowedIPs, setNewPeerAllowedIPs] = useState('');
    const [newPeerEndpoint, setNewPeerEndpoint] = useState('');
    const [isAdding, setIsAdding] = useState(false);

    const handleAddPeer = async () => {
        if (!newPeerName.trim() || !newPeerAllowedIPs.trim()) {
            alert('Peer Name and Allowed IPs are required.');
            return;
        }
        setIsAdding(true);
        try {
            await api.addPeer(interfaceName, {
                name: newPeerName,
                allowed_ips: newPeerAllowedIPs,
                endpoint: newPeerEndpoint || undefined
            });
            setAddModalOpen(false);
            setNewPeerName('');
            setNewPeerAllowedIPs('');
            setNewPeerEndpoint('');
            refreshData();
        } catch (error) {
            console.error("Failed to add peer", error);
            alert(`Failed to add peer: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsAdding(false);
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Peers ({peers.length})</h3>
                <button
                    onClick={() => setAddModalOpen(true)}
                    className="flex items-center text-sm bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold py-2 px-3 rounded-lg transition-colors duration-200">
                    <PlusIcon className="w-4 h-4 mr-2" />
                    Add Peer
                </button>
            </div>
            <div className="overflow-x-auto bg-gray-50/50 dark:bg-gray-900/50 rounded-lg border border-gray-200/50 dark:border-gray-700/50">
                <table className="min-w-full divide-y divide-gray-200/50 dark:divide-gray-700">
                    <thead className="bg-gray-100/60 dark:bg-gray-800/60">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name / Endpoint</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Allowed IPs</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Latest Handshake</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Transfer</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200/50 dark:divide-gray-700/50">
                        {peers.map((peer) => (
                            <tr key={peer.publicKey} className="hover:bg-gray-100/40 dark:hover:bg-gray-800/40 transition-colors duration-150">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-gray-200 dark:bg-gray-700 rounded-full">
                                            <WifiIcon className="h-6 w-6 text-gray-600 dark:text-cyan-400" />
                                        </div>
                                        <div className="ml-4">
                                            <div className="text-sm font-medium text-gray-900 dark:text-gray-200">{peer.name}</div>
                                            <div className="text-sm text-gray-500 dark:text-gray-400 font-mono">{peer.endpoint}</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300 font-mono">{peer.allowedIPs}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{peer.latestHandshake}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                                    <div className="flex items-center text-gray-600 dark:text-green-400">
                                        <ArrowSmDownIcon className="w-4 h-4 mr-1" />
                                        {peer.transfer.received}
                                    </div>
                                    <div className="flex items-center text-gray-600 dark:text-blue-400">
                                        <ArrowSmUpIcon className="w-4 h-4 mr-1" />
                                        {peer.transfer.sent}
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {peers.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                        No peers configured for this interface.
                    </div>
                )}
            </div>

            <Modal isOpen={isAddModalOpen} onClose={() => setAddModalOpen(false)} title={`Add Peer to ${interfaceName}`}>
                <div className="space-y-4">
                    <div>
                        <label htmlFor="peerName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Peer Name</label>
                        <input type="text" id="peerName" value={newPeerName} onChange={(e) => setNewPeerName(e.target.value)} placeholder="e.g., my-laptop" className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2" />
                    </div>
                    <div>
                        <label htmlFor="allowedIPs" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Allowed IPs</label>
                        <input type="text" id="allowedIPs" value={newPeerAllowedIPs} onChange={(e) => setNewPeerAllowedIPs(e.target.value)} placeholder="e.g., 10.0.1.2/32" className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2" />
                    </div>
                    <div>
                        <label htmlFor="endpoint" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Endpoint (Optional)</label>
                        <input type="text" id="endpoint" value={newPeerEndpoint} onChange={(e) => setNewPeerEndpoint(e.target.value)} placeholder="e.g., 123.123.123.123:51820" className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2" />
                    </div>
                    <div className="flex justify-end space-x-2 pt-2">
                        <button onClick={() => setAddModalOpen(false)} className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition">Cancel</button>
                        <button onClick={handleAddPeer} disabled={isAdding} className="px-4 py-2 rounded-md bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold transition disabled:opacity-50">
                            {isAdding ? 'Adding...' : 'Add Peer'}
                        </button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default PeerList;
