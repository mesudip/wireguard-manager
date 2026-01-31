
import React, { useState, useEffect } from 'react';
import { Peer } from '../../types';
import Modal from '../Modal';
import AllowedIPsInput from './AllowedIPsInput';
import { ExclamationIcon } from '../icons/Icons';

interface EditPeerModalProps {
    isOpen: boolean;
    onClose: () => void;
    peer: Peer;
    onUpdatePeer: (peerName: string, peerData: { name?: string, allowed_ips?: string, endpoint?: string, public_key?: string, persistent_keepalive?: string }) => Promise<void>;
}

const EditPeerModal: React.FC<EditPeerModalProps> = ({ isOpen, onClose, peer, onUpdatePeer }) => {
    const [allowedIPs, setAllowedIPs] = useState<string[]>([]);
    const [allowedIPsInput, setAllowedIPsInput] = useState('');
    const [name, setName] = useState('');
    const [endpoint, setEndpoint] = useState('');
    const [persistentKeepalive, setPersistentKeepalive] = useState('');
    const [publicKey, setPublicKey] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (peer) {
            setName(peer.name);
            setAllowedIPs(peer.allowedIPs ? peer.allowedIPs.split(/[\s,]+/).filter(Boolean) : []);
            setEndpoint(peer.endpoint);
            setPersistentKeepalive(peer.persistentKeepalive || '');
            setPublicKey(peer.publicKey);
            setAllowedIPsInput('');
            setError(null);
        }
    }, [peer, isOpen]);

    const handleClose = () => {
        setError(null);
        onClose();
    };

    const handleSubmit = async () => {
        if (!peer) return;
        setError(null);

        // Combine allowedIPs and new input, preserving order while deduplicating
        const newIPsFromInput = allowedIPsInput.split(/[\s,]+/).map(ip => ip.trim()).filter(Boolean);
        const seenIPs = new Set<string>();
        const finalIPs: string[] = [];
        
        for (const ip of [...allowedIPs, ...newIPsFromInput]) {
            if (!seenIPs.has(ip)) {
                finalIPs.push(ip);
                seenIPs.add(ip);
            }
        }

        if (finalIPs.length === 0) {
            setError('At least one Allowed IP is required.');
            return;
        }

        if (!publicKey.trim()) {
            setError('Public Key is required.');
            return;
        }

        setIsSubmitting(true);
        try {
            await onUpdatePeer(peer.name, {
                name: name.trim(),
                allowed_ips: finalIPs.join(', '),
                endpoint: endpoint.trim() || undefined,
                public_key: publicKey.trim(),
                persistent_keepalive: persistentKeepalive.trim() || undefined
            });
            handleClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title={`Edit Peer: ${peer?.name}`}>
            <div className="space-y-4">
                <AllowedIPsInput
                    list={allowedIPs}
                    setList={setAllowedIPs}
                    input={allowedIPsInput}
                    setInput={setAllowedIPsInput}
                />
                <div>
                    <label htmlFor="editName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Peer Name</label>
                    <input
                        type="text"
                        id="editName"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Peer name"
                        className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2"
                    />
                </div>
                <div>
                    <label htmlFor="editPublicKey" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Public Key</label>
                    <input
                        type="text"
                        id="editPublicKey"
                        value={publicKey}
                        onChange={(e) => setPublicKey(e.target.value)}
                        placeholder="Base64 encoded public key"
                        className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 font-mono"
                    />
                </div>
                <div>
                    <label htmlFor="editEndpoint" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Endpoint (Optional)</label>
                    <input type="text" id="editEndpoint" value={endpoint} onChange={(e) => setEndpoint(e.target.value)} placeholder="e.g., 123.123.123.123:51820" className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2" />
                </div>
                <div>
                    <label htmlFor="editPersistentKeepalive" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Persistent Keepalive (Optional)</label>
                    <input type="number" id="editPersistentKeepalive" value={persistentKeepalive} onChange={(e) => setPersistentKeepalive(e.target.value)} placeholder="e.g., 25" className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2" />
                </div>

                {error && (
                    <div className="p-3 bg-red-100 dark:bg-red-900/20 border border-red-400/30 dark:border-red-500/30 text-red-700 dark:text-red-300 rounded-md text-sm flex items-start">
                        <ExclamationIcon className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
                        <div>{error}</div>
                    </div>
                )}

                <div className="flex justify-end space-x-2 pt-2">
                    <button onClick={handleClose} className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition">Cancel</button>
                    <button onClick={handleSubmit} disabled={isSubmitting} className="px-4 py-2 rounded-md bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold transition disabled:opacity-50">
                        {isSubmitting ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </div>
        </Modal>
    );
};

export default EditPeerModal;