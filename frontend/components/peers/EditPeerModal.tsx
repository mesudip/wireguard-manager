
import React, { useState, useEffect } from 'react';
import { Peer } from '../../types';
import Modal from '../Modal';
import AllowedIPsInput from './AllowedIPsInput';
import { ExclamationIcon } from '../icons/Icons';

interface EditPeerModalProps {
    isOpen: boolean;
    onClose: () => void;
    peer: Peer;
    onUpdatePeer: (peerName: string, peerData: { allowed_ips?: string, endpoint?: string, public_key?: string }) => Promise<void>;
}

const EditPeerModal: React.FC<EditPeerModalProps> = ({ isOpen, onClose, peer, onUpdatePeer }) => {
    const [allowedIPs, setAllowedIPs] = useState<string[]>([]);
    const [allowedIPsInput, setAllowedIPsInput] = useState('');
    const [endpoint, setEndpoint] = useState('');
    const [publicKey, setPublicKey] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (peer) {
            setAllowedIPs(peer.allowedIPs ? peer.allowedIPs.split(/[\s,]+/).filter(Boolean) : []);
            setEndpoint(peer.endpoint);
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
        
        const finalIPs = [...new Set([...allowedIPs, ...allowedIPsInput.split(/[\s,]+/).map(ip => ip.trim()).filter(Boolean)])];
        if (finalIPs.length === 0) {
            alert('At least one Allowed IP is required.');
            return;
        }

        if (!publicKey.trim()) {
            alert('Public Key is required.');
            return;
        }

        setIsSubmitting(true);
        try {
            await onUpdatePeer(peer.name, {
                allowed_ips: finalIPs.join(', '),
                endpoint: endpoint.trim() || undefined,
                public_key: publicKey.trim(),
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