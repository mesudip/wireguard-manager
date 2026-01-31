
import React, { useState, useEffect } from 'react';
import { Interface, Peer, HostInfo, ConfigPeer } from '../types';
import * as api from '../services/api';

import AddPeerModal from './peers/AddPeerModal';
import EditPeerModal from './peers/EditPeerModal';
import SharePeerModal from './peers/SharePeerModal';
import PeerTable from './peers/PeerTable';
import ProModeView from './peers/ProModeView';

import { PlusIcon } from './icons/Icons';
import QRCode from 'qrcode';
import { ConfirmDialog, NotificationDialog } from './Dialogs';


interface PeerListProps {
    peers: Peer[];
    refreshData: () => void;
    iface: Interface;
    hostInfo: HostInfo | null;
}

const PeerList: React.FC<PeerListProps> = ({ peers, refreshData, iface, hostInfo }) => {
    // Modal States
    const [isAddModalOpen, setAddModalOpen] = useState(false);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [isShareModalOpen, setIsShareModalOpen] = useState(false);

    // Data states
    const [editingPeer, setEditingPeer] = useState<Peer | null>(null);
    const [sharingPeer, setSharingPeer] = useState<Peer | null>(null);
    const [configText, setConfigText] = useState('');
    const [qrCodeUrl, setQrCodeUrl] = useState('');

    const [isProMode, setIsProMode] = useState(false);
    const [needsRefreshOnModalClose, setNeedsRefreshOnModalClose] = useState(false);
    const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; peer: Peer | null }>({ isOpen: false, peer: null });
    const [notification, setNotification] = useState<{ isOpen: boolean; title: string; message: string; variant: 'success' | 'error' }>({ isOpen: false, title: '', message: '', variant: 'success' });

    // --- Event Handlers ---

    const handleAddPeer = async (peerData: { name: string, allowed_ips: string, endpoint?: string, public_key?: string }) => {
        const newPeer = await api.addPeer(iface.name, peerData);
        setAddModalOpen(false);
        setNeedsRefreshOnModalClose(true);
        await openShareModalForPeer(newPeer);
    };

    const handleUpdatePeer = async (peerName: string, peerData: { allowed_ips?: string, endpoint?: string, public_key?: string }) => {
        await api.updatePeer(iface.name, peerName, peerData as any);
        setIsEditModalOpen(false);
        setEditingPeer(null);
        refreshData();
    };

    const handleDeletePeer = async (peer: Peer) => {
        setDeleteConfirm({ isOpen: true, peer });
    };

    const confirmDeletePeer = async () => {
        const peer = deleteConfirm.peer;
        if (!peer) return;

        try {
            await api.deletePeer(iface.name, peer.name);
            refreshData();
        } catch (error) {
            console.error("Failed to delete peer", error);
            setNotification({
                isOpen: true,
                title: 'Delete Failed',
                message: `Failed to delete peer: ${error instanceof Error ? error.message : 'Unknown error'}`,
                variant: 'error'
            });
        }
    };

    // --- Modal Triggers ---

    const handleEditClick = (peer: Peer) => {
        setEditingPeer(peer);
        setIsEditModalOpen(true);
    };

    const handleShareClick = (peer: Peer) => {
        openShareModalForPeer(peer);
    };

    const openShareModalForPeer = async (peer: Peer | ConfigPeer) => {
        const firstIp = hostInfo?.ips?.[0];
        let endpoint = `YOUR_SERVER_IP:${iface.listenPort}`;

        if (firstIp) {
            const isIPv6 = firstIp.includes(':');
            endpoint = isIPv6 ? `[${firstIp}]:${iface.listenPort}` : `${firstIp}:${iface.listenPort}`;
        }

        const peerConfig = `[Interface]
# Name = ${peer.name}
PrivateKey = ${peer.privateKey || 'PASTE_CLIENT_PRIVATE_KEY_HERE'}
Address = ${peer.allowedIPs.split(',')[0]}
DNS = 8.8.8.8

[Peer]
# ${iface.name}
PublicKey = ${iface.publicKey}
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = ${endpoint}
${peer.persistentKeepalive ? `PersistentKeepalive = ${peer.persistentKeepalive}\n` : ''}
`;
        setConfigText(peerConfig);

        try {
            const url = await QRCode.toDataURL(peerConfig, { width: 256, margin: 1 });
            setQrCodeUrl(url);
        } catch (err) {
            console.error('Failed to generate QR code', err);
            setQrCodeUrl('');
        }

        // Ensure the object passed to the modal is a full Peer object
        const peerForModal: Peer = 'transfer' in peer ? peer : {
            ...peer,
            endpoint: peer.endpoint || '',
            persistentKeepalive: peer.persistentKeepalive || '',
            latestHandshake: 'Never',
            latestHandshakeValue: 0,
            transfer: { received: '', sent: '' },
            transferValue: { received: 0, sent: 0 }
        };

        setSharingPeer(peerForModal);
        setIsShareModalOpen(true);
    };

    const handleShareModalClose = () => {
        setIsShareModalOpen(false);
        if (needsRefreshOnModalClose) {
            refreshData();
            setNeedsRefreshOnModalClose(false);
        }
    };


    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Peers ({peers.length})</h3>
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Pro Mode</span>
                        <label htmlFor="pro-mode-toggle" className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" checked={isProMode} onChange={() => setIsProMode(!isProMode)} id="pro-mode-toggle" className="sr-only peer" />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-cyan-600"></div>
                        </label>
                    </div>
                    <button
                        onClick={() => setAddModalOpen(true)}
                        className="flex items-center text-sm bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold py-2 px-3 rounded-lg transition-colors duration-200">
                        <PlusIcon className="w-4 h-4 mr-2" />
                        Add Peer
                    </button>
                </div>
            </div>

            {isProMode ? (
                <ProModeView peers={peers} />
            ) : (
                <PeerTable
                    peers={peers}
                    interfaceAddress={iface.address}
                    onShare={handleShareClick}
                    onEdit={handleEditClick}
                    onDelete={handleDeletePeer}
                />
            )}

            <AddPeerModal
                isOpen={isAddModalOpen}
                onClose={() => setAddModalOpen(false)}
                onAddPeer={handleAddPeer}
                ifaceName={iface.name}
            />

            {editingPeer && (
                <EditPeerModal
                    isOpen={isEditModalOpen}
                    onClose={() => setIsEditModalOpen(false)}
                    peer={editingPeer}
                    onUpdatePeer={handleUpdatePeer}
                />
            )}

            {sharingPeer && (
                <SharePeerModal
                    isOpen={isShareModalOpen}
                    onClose={handleShareModalClose}
                    peer={sharingPeer}
                    configText={configText}
                    qrCodeUrl={qrCodeUrl}
                />
            )}

            <ConfirmDialog
                isOpen={deleteConfirm.isOpen}
                onClose={() => setDeleteConfirm({ isOpen: false, peer: null })}
                onConfirm={confirmDeletePeer}
                title="Delete Peer"
                message={`Are you sure you want to delete the peer "${deleteConfirm.peer?.name}"?`}
                variant="danger"
                confirmText="Delete"
            />

            <NotificationDialog
                isOpen={notification.isOpen}
                onClose={() => setNotification({ ...notification, isOpen: false })}
                title={notification.title}
                message={notification.message}
                variant={notification.variant}
            />
        </div>
    );
};

export default PeerList;