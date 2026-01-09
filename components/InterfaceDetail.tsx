
import React, { useState } from 'react';
import { Interface, Peer, InterfaceState, DiffResult } from '../types';
import PeerList from './PeerList';
import StateView from './StateView';
import ConfigManager from './ConfigManager';
import { UserGroupIcon, CogIcon, StatusOnlineIcon } from './icons/Icons';

interface InterfaceDetailProps {
    interface: Interface;
    peers: Peer[];
    interfaceState: InterfaceState | null;
    configDiff: DiffResult | null;
    stateDiff: DiffResult | null;
    isLoading: boolean;
    error: string | null;
    refreshData: () => void;
}

type Tab = 'state' | 'peers' | 'config';

const InterfaceDetail: React.FC<InterfaceDetailProps> = ({
    interface: iface,
    peers,
    interfaceState,
    configDiff,
    stateDiff,
    isLoading,
    error,
    refreshData
}) => {
    const [activeTab, setActiveTab] = useState<Tab>('state');

    const renderContent = () => {
        if (isLoading) {
            return <div className="text-center p-10">Loading interface data...</div>;
        }
        if (error) {
            return <div className="text-center p-10 text-red-500 dark:text-red-400">{error}</div>;
        }

        switch (activeTab) {
            case 'state':
                return <StateView interfaceState={interfaceState} stateDiff={stateDiff} refreshData={refreshData} />;
            case 'peers':
                return <PeerList peers={peers} refreshData={refreshData} interfaceName={iface.name} />;
            case 'config':
                return <ConfigManager interface={iface} configDiff={configDiff} refreshData={refreshData} />;
            default:
                return null;
        }
    };

    const TabButton: React.FC<{ tabName: Tab; label: string; icon: React.ReactNode }> = ({ tabName, label, icon }) => (
        <button
            onClick={() => setActiveTab(tabName)}
            className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors duration-200 ${
                activeTab === tabName
                    ? 'border-gray-800 dark:border-cyan-400 text-gray-900 dark:text-cyan-300'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
        >
            {icon}
            <span>{label}</span>
        </button>
    );

    return (
        <div className="bg-white/50 dark:bg-gray-800/50 rounded-xl shadow-2xl h-full flex flex-col">
            <header className="p-4 border-b border-gray-200/50 dark:border-gray-700/50">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{iface.name}</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-mono break-all">{iface.publicKey}</p>
            </header>
            <div className="border-b border-gray-200/50 dark:border-gray-700/50 px-4">
                <div className="flex -mb-px">
                    <TabButton tabName="state" label="State" icon={<StatusOnlineIcon className="w-5 h-5"/>} />
                    <TabButton tabName="peers" label="Peers" icon={<UserGroupIcon className="w-5 h-5"/>} />
                    <TabButton tabName="config" label="Configuration" icon={<CogIcon className="w-5 h-5"/>} />
                </div>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
                {renderContent()}
            </div>
        </div>
    );
};

export default InterfaceDetail;
