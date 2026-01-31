
import React, { useState } from 'react';
import { Interface, ConfigDiffResult } from '../types';
import ConfigDiff from './ConfigDiff';
import * as api from '../services/api';
import { ExclamationIcon, UploadIcon, DownloadIcon } from './icons/Icons';
import { ConfirmDialog, NotificationDialog } from './Dialogs';

interface ConfigManagerProps {
    interface: Interface;
    configDiff: ConfigDiffResult | null;
    refreshData: () => void;
}

const ConfigManager: React.FC<ConfigManagerProps> = ({ interface: iface, configDiff, refreshData }) => {
    const [isApplying, setIsApplying] = useState(false);
    const [isReverting, setIsReverting] = useState(false);
    const [notification, setNotification] = useState<{ isOpen: boolean; title: string; message: string; variant: 'success' | 'error' }>({ isOpen: false, title: '', message: '', variant: 'success' });

    // Helper to check if there are actual differences
    const hasChanges = (diff: ConfigDiffResult | null): boolean => {
        if (!diff) return false;
        
        const { currentConfig, folderConfig } = diff;
        
        // Check if peer counts differ
        if (currentConfig.peers.length !== folderConfig.peers.length) return true;
        
        // Check if any peer properties differ
        const currentMap = new Map(currentConfig.peers.map(p => [p.publicKey, p]));
        for (const folderPeer of folderConfig.peers) {
            const currentPeer = currentMap.get(folderPeer.publicKey);
            if (!currentPeer) return true; // Peer added or public key changed
            
            // Compare properties
            if (currentPeer.allowedIPs !== folderPeer.allowedIPs) return true;
            if (currentPeer.endpoint !== folderPeer.endpoint) return true;
            if (currentPeer.persistentKeepalive !== folderPeer.persistentKeepalive) return true;
        }
        
        return false;
    };

    const handleApply = async () => {
        setIsApplying(true);
        try {
            await api.applyConfig(iface.name);
            setNotification({
                isOpen: true,
                title: 'Success',
                message: 'Configuration applied and WireGuard updated successfully!',
                variant: 'success'
            });
            refreshData();
        } catch (error) {
            setNotification({
                isOpen: true,
                title: 'Apply Failed',
                message: `Failed to apply configuration: ${error instanceof Error ? error.message : 'Unknown error'}`,
                variant: 'error'
            });
        } finally {
            setIsApplying(false);
        }
    };

    const handleRevert = async () => {
        setIsReverting(true);
        try {
            await api.resetConfig(iface.name);
            setNotification({
                isOpen: true,
                title: 'Success',
                message: 'Changes reverted to current configuration file!',
                variant: 'success'
            });
            refreshData();
        } catch (error) {
            setNotification({
                isOpen: true,
                title: 'Revert Failed',
                message: `Failed to revert changes: ${error instanceof Error ? error.message : 'Unknown error'}`,
                variant: 'error'
            });
        } finally {
            setIsReverting(false);
        }
    };

    return (
        <div className="space-y-8">
            <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Interface Configuration</h3>
                <div className="bg-gray-50/50 dark:bg-gray-900/50 p-4 rounded-lg border border-gray-200/50 dark:border-gray-700/50 space-y-2">
                    <p><strong className="text-gray-500 dark:text-gray-400 w-36 inline-block">Interface Address:</strong> <span className="font-mono">{iface.address}</span></p>
                    <p><strong className="text-gray-500 dark:text-gray-400 w-36 inline-block">Listen Port:</strong> <span className="font-mono">{iface.listenPort}</span></p>
                    <p><strong className="text-gray-500 dark:text-gray-400 w-36 inline-block">Public Key:</strong> <span className="font-mono break-all">{iface.publicKey}</span></p>
                </div>
            </div>

            {hasChanges(configDiff) && (
                <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 text-yellow-600 dark:text-yellow-400">Unsaved Changes</h3>
                    <div className="bg-yellow-100/50 dark:bg-yellow-900/20 border border-yellow-400/30 dark:border-yellow-500/30 text-yellow-800 dark:text-yellow-300 p-4 rounded-lg">
                        <div className="flex items-start">
                            <ExclamationIcon className="w-5 h-5 mr-3 mt-1 flex-shrink-0" />
                            <div className="flex-1">
                                <h4 className="font-bold">Pending Changes Detected</h4>
                                <p className="text-sm text-yellow-700 dark:text-yellow-400 mb-4">
                                    The peer configuration or interface settings have been modified. These changes won't take effect until applied.
                                </p>
                                <div className="flex space-x-4">
                                    <button onClick={handleApply} disabled={isApplying || isReverting} className="flex items-center bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
                                        <UploadIcon className="w-5 h-5 mr-2" />
                                        {isApplying ? 'Applying...' : 'Apply Configuration'}
                                    </button>
                                    <button onClick={handleRevert} disabled={isReverting || isApplying} className="flex items-center bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
                                        <DownloadIcon className="w-5 h-5 mr-2" />
                                        {isReverting ? 'Reverting...' : 'Revert Changes'}
                                    </button>
                                </div>
                            </div>
                        </div>
                        <ConfigDiff currentConfig={configDiff.currentConfig} folderConfig={configDiff.folderConfig} />
                    </div>
                </div>
            )}


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

export default ConfigManager;