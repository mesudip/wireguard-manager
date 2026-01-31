
import React, { useState, useEffect, useRef } from 'react';
import { Interface, Peer, InterfaceState, ConfigDiffResult, HostInfo } from '../types';
import PeerList from './PeerList';
import StateView from './StateView';
import ConfigManager from './ConfigManager';
import { UserGroupIcon, CogIcon, StatusOnlineIcon, DotsVerticalIcon, TrashIcon } from './icons/Icons';

interface InterfaceDetailProps {
    interface: Interface;
    peers: Peer[];
    hostInfo: HostInfo | null;
    interfaceState: InterfaceState | null;
    configDiff: ConfigDiffResult | null;
    isLoading: boolean;
    error: string | null;
    refreshData: () => void;
    onDeleteInterface: (name: string) => void;
}

type Tab = 'state' | 'peers' | 'config';

const InterfaceDetail: React.FC<InterfaceDetailProps> = ({
    interface: iface,
    peers,
    hostInfo,
    interfaceState,
    configDiff,
    isLoading,
    error,
    refreshData,
    onDeleteInterface
}) => {
    const [activeTab, setActiveTab] = useState<Tab>('state');
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

    const handleDelete = () => {
        setActionsMenuOpen(false);
        onDeleteInterface(iface.name);
    };

    const renderContent = () => {
        if (isLoading) {
            return <div className="text-center p-10">Loading interface data...</div>;
        }
        if (error) {
            return <div className="text-center p-10 text-red-500 dark:text-red-400">{error}</div>;
        }

        switch (activeTab) {
            case 'state':
                return <StateView
                    interfaceState={interfaceState}
                    peers={peers}
                    configDiff={configDiff}
                    refreshData={refreshData}
                    interfaceName={iface.name}
                    interfaceAddress={iface.address}
                    hostInfo={hostInfo}
                />;
            case 'peers':
                return <PeerList
                    peers={peers}
                    refreshData={refreshData}
                    iface={iface}
                    hostInfo={hostInfo}
                />;
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
            <header className="p-4 border-b border-gray-200/50 dark:border-gray-700/50 flex justify-between items-start">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{iface.name}</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 font-mono break-all">{iface.publicKey}</p>
                </div>
                <div className="relative" ref={menuRef}>
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
                                <button
                                    onClick={handleDelete}
                                    className="w-full text-left flex items-center px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                                    role="menuitem"
                                >
                                    <TrashIcon className="w-4 h-4 mr-3"/>
                                    Delete Interface
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </header>
            <div className="border-b border-gray-200/50 dark:border-gray-700/50 px-4">
                <div className="flex -mb-px">
                    <TabButton 
                        tabName="state" 
                        label="State" 
                        icon={<StatusOnlineIcon className="w-5 h-5" />} 
                    />
                    <TabButton 
                        tabName="peers" 
                        label={`Peers (${peers.length})`} 
                        icon={<UserGroupIcon className="w-5 h-5" />} 
                    />
                    <TabButton 
                        tabName="config" 
                        label="Configuration" 
                        icon={<CogIcon className={`w-5 h-5 ${configDiff && (configDiff.currentConfig.peers.length > 0 || configDiff.folderConfig.peers.length > 0) ? 'text-yellow-500 dark:text-yellow-400' : ''}`} />} 
                    />
                </div>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
                {renderContent()}
            </div>
        </div>
    );
};

export default InterfaceDetail;