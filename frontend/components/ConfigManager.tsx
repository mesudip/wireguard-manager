
import React, { useState } from 'react';
import { Interface, DiffResult } from '../types';
import DiffViewer from './DiffViewer';
import * as api from '../services/api';
import { ExclamationIcon, UploadIcon, DownloadIcon } from './icons/Icons';

interface ConfigManagerProps {
    interface: Interface;
    configDiff: DiffResult | null;
    refreshData: () => void;
}

const ConfigManager: React.FC<ConfigManagerProps> = ({ interface: iface, configDiff, refreshData }) => {
    const [isSyncing, setIsSyncing] = useState(false);
    const [isResetting, setIsResetting] = useState(false);

    const handleSync = async () => {
        setIsSyncing(true);
        try {
            await api.syncConfig(iface.name);
            alert('Configuration file replaced successfully!');
            refreshData();
        } catch (error) {
            alert(`Failed to replace configuration file: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsSyncing(false);
        }
    };

    const handleReset = async () => {
        if (window.confirm('Are you sure you want to read from the config file? This will overwrite the current folder structure and any unsaved changes.')) {
            setIsResetting(true);
            try {
                await api.resetConfig(iface.name);
                alert('Folder structure updated from config file successfully!');
                refreshData();
            } catch (error) {
                alert(`Failed to read from config file: ${error instanceof Error ? error.message : 'Unknown error'}`);
            } finally {
                setIsResetting(false);
            }
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

            {configDiff && configDiff.hasChanges && (
                <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Config file inconsistent</h3>
                     <div className="bg-yellow-100/50 dark:bg-yellow-900/20 border border-yellow-400/30 dark:border-yellow-500/30 text-yellow-800 dark:text-yellow-300 p-4 rounded-lg">
                         <div className="flex items-start">
                            <ExclamationIcon className="w-5 h-5 mr-3 mt-1 flex-shrink-0" />
                            <div>
                                <h4 className="font-bold">Pending Changes</h4>
                                <p className="text-sm text-yellow-700 dark:text-yellow-400 mb-4">
                                    The folder structure has changes that are not present in the main configuration file.
                                </p>
                                <div className="flex space-x-4">
                                    <button onClick={handleSync} disabled={isSyncing || isResetting} className="flex items-center bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
                                        <UploadIcon className="w-5 h-5 mr-2"/>
                                        {isSyncing ? 'Replacing...' : 'Replace config file'}
                                    </button>
                                     <button onClick={handleReset} disabled={isResetting || isSyncing} className="flex items-center bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
                                        <DownloadIcon className="w-5 h-5 mr-2"/>
                                        {isResetting ? 'Reading...' : 'Read from config file'}
                                    </button>
                                </div>
                            </div>
                         </div>
                        <DiffViewer diff={configDiff.diff} />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ConfigManager;