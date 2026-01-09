
import React, { useState } from 'react';
import { Interface, DiffResult } from '../types';
import DiffViewer from './DiffViewer';
import * as api from '../services/api';
import { CheckIcon, ExclamationIcon, UploadIcon, DownloadIcon } from './icons/Icons';

interface ConfigManagerProps {
    interface: Interface;
    configDiff: DiffResult | null;
    refreshData: () => void;
}

const ConfigManager: React.FC<ConfigManagerProps> = ({ interface: iface, configDiff, refreshData }) => {
    const [isApplying, setIsApplying] = useState(false);
    const [isResetting, setIsResetting] = useState(false);

    const handleApply = async () => {
        setIsApplying(true);
        try {
            await api.applyConfig(iface.name);
            alert('Configuration applied successfully!');
            refreshData();
        } catch (error) {
            alert('Failed to apply configuration.');
        } finally {
            setIsApplying(false);
        }
    };

    const handleReset = async () => {
        if (window.confirm('Are you sure you want to reset the folder structure from the config file? This will overwrite existing peer files in the folder.')) {
            setIsResetting(true);
            try {
                await api.resetConfig(iface.name);
                alert('Configuration reset successfully!');
                refreshData();
            } catch (error) {
                alert('Failed to reset configuration.');
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
                    <p><strong className="text-gray-500 dark:text-gray-400 w-24 inline-block">Address:</strong> <span className="font-mono">{iface.address}</span></p>
                    <p><strong className="text-gray-500 dark:text-gray-400 w-24 inline-block">Listen Port:</strong> <span className="font-mono">{iface.listenPort}</span></p>
                    <p><strong className="text-gray-500 dark:text-gray-400 w-24 inline-block">Public Key:</strong> <span className="font-mono break-all">{iface.publicKey}</span></p>
                </div>
            </div>

            <div>
                 <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Management Actions</h3>
                 <div className="flex space-x-4">
                     <button onClick={handleApply} disabled={isApplying} className="flex items-center bg-gray-800 hover:bg-gray-700 dark:bg-green-600 dark:hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200 disabled:bg-gray-600 dark:disabled:bg-green-800 disabled:cursor-not-allowed">
                        <UploadIcon className="w-5 h-5 mr-2"/>
                        {isApplying ? 'Applying...' : 'Apply Folder to Config'}
                    </button>
                    <button onClick={handleReset} disabled={isResetting} className="flex items-center bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200 disabled:bg-yellow-800 disabled:cursor-not-allowed">
                        <DownloadIcon className="w-5 h-5 mr-2"/>
                        {isResetting ? 'Resetting...' : 'Reset Folder from Config'}
                    </button>
                 </div>
            </div>

            <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Folder vs. Config File Diff</h3>
                 {configDiff ? (
                    configDiff.hasChanges ? (
                        <div className="bg-yellow-100/50 dark:bg-yellow-900/20 border border-yellow-400/30 dark:border-yellow-500/30 text-yellow-800 dark:text-yellow-300 p-4 rounded-lg">
                             <div className="flex items-start">
                                <ExclamationIcon className="w-5 h-5 mr-3 mt-1 flex-shrink-0" />
                                <div>
                                    <h4 className="font-bold">Pending Changes</h4>
                                    <p className="text-sm text-yellow-700 dark:text-yellow-400 mb-2">The folder structure has changes that are not present in the main configuration file. Click "Apply" to update the config file.</p>
                                </div>
                             </div>
                            <DiffViewer diff={configDiff.diff} />
                        </div>
                    ) : (
                        <div className="bg-gray-100/50 dark:bg-green-900/20 border border-gray-300/50 dark:border-green-500/30 text-gray-700 dark:text-green-300 p-4 rounded-lg flex items-center">
                            <CheckIcon className="w-5 h-5 mr-2" />
                            <p>The folder structure and configuration file are in sync.</p>
                        </div>
                    )
                ) : (
                     <div className="bg-gray-100/50 dark:bg-gray-900/50 p-4 rounded-lg border border-gray-200/50 dark:border-gray-700/50">
                        <p>Could not load diff.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ConfigManager;
