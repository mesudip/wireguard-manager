
import React, { useState, useRef, useEffect } from 'react';
import { Peer } from '../../types';
import { WifiIcon, ArrowSmDownIcon, ArrowSmUpIcon, DotsVerticalIcon, PencilIcon, TrashIcon, ShareIcon } from '../icons/Icons';

interface PeerRowProps {
    peer: Peer;
    onShare: (peer: Peer) => void;
    onEdit: (peer: Peer) => void;
    onDelete: (peer: Peer) => void;
}

const PeerRow: React.FC<PeerRowProps> = ({ peer, onShare, onEdit, onDelete }) => {
    const [isActionsMenuOpen, setActionsMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setActionsMenuOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleEditClick = () => {
        onEdit(peer);
        setActionsMenuOpen(false);
    };

    const handleDeleteClick = () => {
        onDelete(peer);
        setActionsMenuOpen(false);
    };

    return (
        <tr className="hover:bg-gray-100/40 dark:hover:bg-gray-800/40 transition-colors duration-150">
            <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-gray-200 dark:bg-gray-700 rounded-full">
                        <WifiIcon className="h-6 w-6 text-gray-600 dark:text-cyan-400" />
                    </div>
                    <div className="ml-4">
                        <div
                            className="text-sm font-medium text-gray-900 dark:text-gray-200 max-w-[22ch] truncate"
                            title={peer.name}
                        >
                            {peer.name}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 font-mono">{peer.endpoint}</div>
                    </div>
                </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex flex-wrap gap-1">
                {peer.allowedIPs.split(/[\s,]+/).filter(Boolean).map(ip => (
                    <span key={ip} className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 text-xs font-mono px-2 py-1 rounded-full">
                        {ip}
                    </span>
                ))}
                </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{peer.latestHandshake}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                {peer.transfer.received && (
                    <div className="flex items-center text-gray-600 dark:text-green-400">
                        <ArrowSmDownIcon className="w-4 h-4 mr-1" />
                        {peer.transfer.received}
                    </div>
                )}
                {peer.transfer.sent && (
                    <div className="flex items-center text-gray-600 dark:text-blue-400">
                        <ArrowSmUpIcon className="w-4 h-4 mr-1" />
                        {peer.transfer.sent}
                    </div>
                )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end space-x-1">
                    <button
                        onClick={() => onShare(peer)}
                        className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
                        aria-label="Share Config"
                        title="Share Config"
                    >
                        <ShareIcon className="w-5 h-5" />
                    </button>
                    <div className="relative inline-block text-left" ref={menuRef}>
                        <button
                            onClick={() => setActionsMenuOpen(!isActionsMenuOpen)}
                            className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
                            aria-haspopup="true"
                            aria-expanded={isActionsMenuOpen}
                        >
                            <DotsVerticalIcon className="w-5 h-5" />
                        </button>
                        {isActionsMenuOpen && (
                            <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 dark:ring-gray-700 z-10">
                                <div className="py-1" role="menu" aria-orientation="vertical">
                                    <button onClick={handleEditClick} className="w-full text-left flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700" role="menuitem">
                                        <PencilIcon className="w-4 h-4 mr-3"/>
                                        Edit
                                    </button>
                                    <button onClick={handleDeleteClick} className="w-full text-left flex items-center px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20" role="menuitem">
                                        <TrashIcon className="w-4 h-4 mr-3"/>
                                        Delete
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </td>
        </tr>
    );
};

export default PeerRow;
