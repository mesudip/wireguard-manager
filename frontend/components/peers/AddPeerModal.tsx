
import React, { useState } from 'react';
import Modal from '../Modal';
import AllowedIPsInput from './AllowedIPsInput';
import { ExclamationIcon } from '../icons/Icons';

interface AddPeerModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAddPeer: (peerData: { name: string, allowed_ips: string, endpoint?: string, public_key?: string }) => Promise<void>;
    ifaceName: string;
}

const AddPeerModal: React.FC<AddPeerModalProps> = ({ isOpen, onClose, onAddPeer, ifaceName }) => {
    const [name, setName] = useState('');
    const [allowedIPs, setAllowedIPs] = useState<string[]>([]);
    const [allowedIPsInput, setAllowedIPsInput] = useState('');
    const [endpoint, setEndpoint] = useState('');
    const [publicKey, setPublicKey] = useState('');
    const [isAdding, setIsAdding] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const resetForm = () => {
        setName('');
        setAllowedIPs([]);
        setAllowedIPsInput('');
        setEndpoint('');
        setPublicKey('');
        setError(null);
        setIsAdding(false);
    };

    const handleClose = () => {
        resetForm();
        onClose();
    };

    const handleSubmit = async () => {
        setError(null);
        const finalIPs = [...new Set([...allowedIPs, ...allowedIPsInput.split(/[\s,]+/).map(ip => ip.trim()).filter(Boolean)])];

        if (!name.trim() || finalIPs.length === 0) {
            alert('Peer Name and at least one Allowed IP are required.');
            return;
        }

        setIsAdding(true);
        try {
            await onAddPeer({
                name: name.trim(),
                allowed_ips: finalIPs.join(', '),
                endpoint: endpoint.trim() || undefined,
                public_key: publicKey.trim() || undefined
            });
            // The parent will close the modal upon success
            resetForm();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setIsAdding(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title={`Add Peer to ${ifaceName}`}>
            <div className="space-y-4">
                <div>
                    <label htmlFor="peerName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Peer Name</label>
                    <input type="text" id="peerName" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., my-laptop" className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2" />
                </div>
                
                <AllowedIPsInput
                    list={allowedIPs}
                    setList={setAllowedIPs}
                    input={allowedIPsInput}
                    setInput={setAllowedIPsInput}
                />

                <div>
                    <label htmlFor="peerPublicKey" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Public Key (Optional)</label>
                    <input type="text" id="peerPublicKey" value={publicKey} onChange={(e) => setPublicKey(e.target.value)} placeholder="Leave blank to auto-generate" className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2" />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">If you provide a public key, no private key will be generated or stored.</p>
                </div>

                <div>
                    <label htmlFor="endpoint" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Endpoint (Optional)</label>
                    <input type="text" id="endpoint" value={endpoint} onChange={(e) => setEndpoint(e.target.value)} placeholder="e.g., 123.123.123.123:51820" className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2" />
                </div>

                {error && (
                    <div className="p-3 bg-red-100 dark:bg-red-900/20 border border-red-400/30 dark:border-red-500/30 text-red-700 dark:text-red-300 rounded-md text-sm flex items-start">
                        <ExclamationIcon className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
                        <div>{error}</div>
                    </div>
                )}

                <div className="flex justify-end space-x-2 pt-2">
                    <button onClick={handleClose} className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition">Cancel</button>
                    <button onClick={handleSubmit} disabled={isAdding} className="px-4 py-2 rounded-md bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold transition disabled:opacity-50">
                        {isAdding ? 'Adding...' : 'Add Peer'}
                    </button>
                </div>
            </div>
        </Modal>
    );
};

export default AddPeerModal;
