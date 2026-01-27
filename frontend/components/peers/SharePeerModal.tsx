
import React, { useState } from 'react';
import { Peer } from '../../types';
import Modal from '../Modal';
import { ClipboardCopyIcon, CheckIcon } from '../icons/Icons';

interface SharePeerModalProps {
    isOpen: boolean;
    onClose: () => void;
    peer: Peer;
    configText: string;
    qrCodeUrl: string;
}

const SharePeerModal: React.FC<SharePeerModalProps> = ({ isOpen, onClose, peer, configText, qrCodeUrl }) => {
    const [copySuccess, setCopySuccess] = useState(false);

    const copyToClipboard = () => {
        navigator.clipboard.writeText(configText).then(() => {
            setCopySuccess(true);
            setTimeout(() => setCopySuccess(false), 2000);
        });
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={`Client Config for ${peer?.name}`} maxWidth="max-w-3xl">
            <div>
                <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">
                    <div className="flex-1 w-full relative bg-gray-100 dark:bg-gray-900 rounded-md p-4 font-mono text-xs border border-gray-300 dark:border-gray-600">
                        <button
                            onClick={copyToClipboard}
                            className="absolute top-2 right-2 p-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                            aria-label="Copy to clipboard"
                        >
                            {copySuccess ? <CheckIcon className="w-5 h-5 text-green-500" /> : <ClipboardCopyIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />}
                        </button>
                        <pre className="whitespace-pre-wrap break-all">
                            <code>
                                {configText}
                            </code>
                        </pre>
                    </div>
                    <div className="flex-shrink-0 flex flex-col items-center justify-center p-4 bg-white rounded-md">
                         {qrCodeUrl ? (
                            <img src={qrCodeUrl} alt="WireGuard Config QR Code" className="w-48 h-48 md:w-56 md:h-56"/>
                        ) : (
                            <div className="w-48 h-48 md:w-56 md:h-56 flex items-center justify-center">
                                <p className="text-gray-500">Generating QR code...</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="mt-6 flex justify-end">
                    <button onClick={onClose} className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition">Close</button>
                </div>
            </div>
        </Modal>
    );
};

export default SharePeerModal;
