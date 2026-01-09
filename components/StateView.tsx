
import React from 'react';
import { InterfaceState, DiffResult } from '../types';
import DiffViewer from './DiffViewer';
import { RefreshIcon, DocumentTextIcon, ExclamationIcon, WifiIcon, BeakerIcon } from './icons/Icons';

interface StateViewProps {
    interfaceState: InterfaceState | null;
    stateDiff: DiffResult | null;
    refreshData: () => void;
}

const StateView: React.FC<StateViewProps> = ({ interfaceState, stateDiff, refreshData }) => {

    const Card: React.FC<{title: string, value: string | number, icon: React.ReactNode}> = ({title, value, icon}) => (
        <div className="bg-white/50 dark:bg-gray-900/50 p-4 rounded-lg flex items-center border border-gray-200/50 dark:border-gray-700/50">
            <div className="p-3 rounded-full bg-gray-500/10 mr-4">
                {icon}
            </div>
            <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">{title}</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{value}</p>
            </div>
        </div>
    );

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Live State</h3>
                <button onClick={refreshData} className="flex items-center text-sm bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold py-2 px-3 rounded-lg transition-colors duration-200">
                    <RefreshIcon className="w-4 h-4 mr-2" />
                    Refresh
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card title="Listen Port" value={interfaceState?.listenPort || 'N/A'} icon={<DocumentTextIcon className="w-6 h-6 text-gray-600 dark:text-cyan-400"/>} />
                <Card title="Live Peers" value={interfaceState?.peers.length || 0} icon={<WifiIcon className="w-6 h-6 text-gray-600 dark:text-cyan-400"/>} />
            </div>

            <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <BeakerIcon className="w-6 h-6 mr-2 text-gray-500 dark:text-gray-400" />
                    Live vs. Config File Diff
                </h3>
                {stateDiff ? (
                    stateDiff.hasChanges ? (
                         <div className="bg-yellow-100/50 dark:bg-yellow-900/20 border border-yellow-400/30 dark:border-yellow-500/30 text-yellow-800 dark:text-yellow-300 p-4 rounded-lg">
                            <div className="flex items-start">
                                <ExclamationIcon className="w-5 h-5 mr-3 mt-1 flex-shrink-0" />
                                <div>
                                    <h4 className="font-bold">Configuration Mismatch</h4>
                                    <p className="text-sm text-yellow-700 dark:text-yellow-400">The live state differs from the saved configuration file. You may need to restart the interface for changes to take effect.</p>
                                </div>
                            </div>
                            <DiffViewer diff={stateDiff.diff} />
                        </div>
                    ) : (
                        <div className="bg-gray-100/50 dark:bg-green-900/20 border border-gray-300/50 dark:border-green-500/30 text-gray-700 dark:text-green-300 p-4 rounded-lg">
                            <p>✓ No differences between live state and configuration file.</p>
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

export default StateView;
