
import React, { useState, useEffect } from 'react';
import { Peer } from '../../types';
import { ClipboardCopyIcon, CheckIcon } from '../icons/Icons';

interface ProModeViewProps {
    peers: Peer[];
}

const ProModeView: React.FC<ProModeViewProps> = ({ peers }) => {
    const [proConfigText, setProConfigText] = useState('');
    const [proCopySuccess, setProCopySuccess] = useState(false);

    useEffect(() => {
        const text = peers.map((peer, index) => {
            const peerIndex = index + 1;
            const formattedIndex = String(peerIndex).padStart(2, '0');
            
            let peerBlock = `[Peer]  #  ${formattedIndex}. ${peer.name}\n`;
            peerBlock += `PublicKey = ${peer.publicKey}\n`;
            if (peer.allowedIPs) {
                peerBlock += `AllowedIPs = ${peer.allowedIPs}\n`;
            }
            if (peer.endpoint) {
                peerBlock += `Endpoint = ${peer.endpoint}\n`;
            }
            return peerBlock;
        }).join('\n');
        setProConfigText(text);
    }, [peers]);

    const copyProConfigToClipboard = () => {
        navigator.clipboard.writeText(proConfigText).then(() => {
            setProCopySuccess(true);
            setTimeout(() => setProCopySuccess(false), 2000);
        });
    };

    return (
        <div className="relative bg-gray-100 dark:bg-gray-900 rounded-md p-4 font-mono text-sm border border-gray-300 dark:border-gray-600">
             <button
                onClick={copyProConfigToClipboard}
                className="absolute top-2 right-2 p-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                aria-label="Copy to clipboard"
            >
                {proCopySuccess ? <CheckIcon className="w-5 h-5 text-green-500" /> : <ClipboardCopyIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />}
            </button>
            <pre className="whitespace-pre-wrap break-all">
                <code>
                    {proConfigText}
                </code>
            </pre>
        </div>
    );
};

export default ProModeView;
