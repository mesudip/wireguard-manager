
import React, { useState } from 'react';
import { InterfaceState, DiffResult, HostInfo } from '../types';
import DiffViewer from './DiffViewer';
import * as api from '../services/api';
import { RefreshIcon, DocumentTextIcon, ExclamationIcon, WifiIcon, BeakerIcon, UploadIcon, AtSymbolIcon } from './icons/Icons';
import { NotificationDialog } from './Dialogs';

interface StateViewProps {
    interfaceState: InterfaceState | null;
    stateDiff: DiffResult | null;
    configDiff: DiffResult | null;
    interfaceName: string;
    interfaceAddress: string;
    refreshData: () => void;
    hostInfo: HostInfo | null;
}

const StateView: React.FC<StateViewProps> = ({ interfaceState, stateDiff, configDiff, interfaceName, interfaceAddress, refreshData, hostInfo }) => {
    const [isApplying, setIsApplying] = useState(false);
    const [notification, setNotification] = useState<{ isOpen: boolean; title: string; message: string; variant: 'success' | 'error' }>({ isOpen: false, title: '', message: '', variant: 'success' });

    const handleApplyConfig = async () => {
        setIsApplying(true);
        try {
            await api.applyConfig(interfaceName);
            setNotification({
                isOpen: true,
                title: 'Success',
                message: 'Configuration applied successfully!',
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
            setIsApplying(true); // Wait, line 29 shows it sets to false. Let me fix the logic here.
            setIsApplying(false);
        }
    };

    const Card: React.FC<{ title: string, value: React.ReactNode, icon: React.ReactNode }> = ({ title, value, icon }) => (
        <div className="bg-white/50 dark:bg-gray-900/50 p-4 rounded-lg flex items-center border border-gray-200/50 dark:border-gray-700/50">
            <div className="p-3 rounded-full bg-gray-500/10 mr-4">
                {icon}
            </div>
            <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">{title}</p>
                <div className="text-lg font-semibold text-gray-900 dark:text-white font-mono break-all">{value}</div>
            </div>
        </div>
    );

    const listenPort = interfaceState?.listenPort;
    const hostIps = hostInfo?.ips;

    let listenEndpointsContent: React.ReactNode;

    if (listenPort && hostIps && hostIps.length > 0) {
        listenEndpointsContent = hostIps.map(ip => {
            const isIPv6 = ip.includes(':');
            const endpoint = isIPv6 ? `[${ip}]:${listenPort}` : `${ip}:${listenPort}`;
            return <div key={ip}>{endpoint}</div>;
        });
    } else if (listenPort) {
        listenEndpointsContent = listenPort;
    } else {
        listenEndpointsContent = 'N/A';
    }


    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Live State</h3>
                <div className="flex items-center">
                    <button onClick={refreshData} className="flex items-center text-sm bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold py-2 px-3 rounded-lg transition-colors duration-200">
                        <RefreshIcon className="w-4 h-4 mr-2" />
                        Refresh
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                    <Card title="Interface Address" value={interfaceAddress} icon={<AtSymbolIcon className="w-6 h-6 text-gray-600 dark:text-cyan-400" />} />
                </div>
                <Card title="Listen Endpoints" value={listenEndpointsContent} icon={<DocumentTextIcon className="w-6 h-6 text-gray-600 dark:text-cyan-400" />} />
                <Card title="Live Peers" value={interfaceState?.peers.length || 0} icon={<WifiIcon className="w-6 h-6 text-gray-600 dark:text-cyan-400" />} />
            </div>

            {stateDiff && stateDiff.hasChanges && (
                <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                        <BeakerIcon className="w-6 h-6 mr-2 text-red-500 dark:text-red-400" />
                        Status: Out of Sync
                    </h3>
                    <div className="bg-red-100/30 dark:bg-red-900/10 border border-red-400/30 dark:border-red-500/30 text-red-800 dark:text-red-300 p-4 rounded-lg">
                        <div className="flex items-start">
                            <ExclamationIcon className="w-5 h-5 mr-3 mt-1 flex-shrink-0" />
                            <div>
                                <h4 className="font-bold">Configuration Sync Required</h4>
                                <p className="text-sm text-red-700 dark:text-red-400 mb-4">The running interface state differs from the saved configuration file. Apply the configuration to restore synchronization.</p>
                                <button onClick={handleApplyConfig} disabled={isApplying} className="flex items-center bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
                                    <UploadIcon className="w-5 h-5 mr-2" />
                                    {isApplying ? 'Applying...' : 'Apply Configuration'}
                                </button>
                            </div>
                        </div>
                        <DiffViewer diff={stateDiff.diff} />
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

export default StateView;