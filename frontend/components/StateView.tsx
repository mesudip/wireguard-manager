
import React, { useState } from 'react';
import { InterfaceState, DiffResult, HostInfo, Peer } from '../types';
import StateDiff from './StateDiff';
import * as api from '../services/api';
import { RefreshIcon, DocumentTextIcon, ExclamationIcon, WifiIcon, BeakerIcon, UploadIcon, AtSymbolIcon } from './icons/Icons';
import { NotificationDialog } from './Dialogs';

interface StateViewProps {
    interfaceState: InterfaceState | null;
    peers: Peer[];
    configDiff: DiffResult | null;
    interfaceName: string;
    interfaceAddress: string;
    refreshData: () => void;
    hostInfo: HostInfo | null;
}

const StateView: React.FC<StateViewProps> = ({ interfaceState, peers, configDiff, interfaceName, interfaceAddress, refreshData, hostInfo }) => {
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

            <StateDiff 
                peers={peers}
                interfaceState={interfaceState}
                hostInfo={hostInfo}
                interfaceAddress={interfaceAddress}
                onApplyConfig={handleApplyConfig}
                isApplying={isApplying}
            />

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