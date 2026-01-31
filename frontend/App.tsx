
import React, { useState, useEffect, useCallback } from 'react';
import { Interface, Peer, InterfaceState, DiffResult, StatePeer, HostInfo } from './types';
import * as api from './services/api';
import { formatBytes, formatHandshake } from './utils';
import InterfaceList from './components/InterfaceList';
import InterfaceDetail from './components/InterfaceDetail';
import { PlusIcon, ServerIcon, SunIcon, MoonIcon, PencilIcon, ExclamationIcon, RefreshIcon } from './components/icons/Icons';
import Modal from './components/Modal';
import { ConfirmDialog } from './components/Dialogs';

const App: React.FC = () => {
    const [interfaces, setInterfaces] = useState<Interface[]>([]);
    const [selectedInterface, setSelectedInterface] = useState<Interface | null>(null);
    const [peers, setPeers] = useState<Peer[]>([]);
    const [interfaceState, setInterfaceState] = useState<InterfaceState | null>(null);
    const [configDiff, setConfigDiff] = useState<DiffResult | null>(null);
    const [stateDiff, setStateDiff] = useState<DiffResult | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isCreateModalOpen, setCreateModalOpen] = useState(false);
    const [newInterfaceName, setNewInterfaceName] = useState('');
    const [newInterfaceAddress, setNewInterfaceAddress] = useState('10.0.1.1/24');
    const [newInterfacePort, setNewInterfacePort] = useState('51820');
    const [hostInfo, setHostInfo] = useState<HostInfo | null>(null);

    const [isHostEditModalOpen, setHostEditModalOpen] = useState(false);
    const [editedHostIPs, setEditedHostIPs] = useState('');
    const [isSavingHostIPs, setIsSavingHostIPs] = useState(false);
    const [isRescanningHostIPs, setIsRescanningHostIPs] = useState(false);
    const [hostEditError, setHostEditError] = useState<string | null>(null);
    const [createInterfaceError, setCreateInterfaceError] = useState<string | null>(null);
    const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; name: string }>({ isOpen: false, name: '' });

    const [theme, setTheme] = useState(() =>
        document.documentElement.classList.contains('dark') ? 'dark' : 'light'
    );

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        if (newTheme === 'dark') {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    };

    const fetchInterfaces = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await api.getInterfaces();
            setInterfaces(data.interfaces);
            setHostInfo(data.hostInfo);
            if (data.interfaces.length > 0 && !selectedInterface) {
                // Automatically select the first interface if none is selected
                handleSelectInterface(data.interfaces[0]);
            } else if (data.interfaces.length === 0) {
                setSelectedInterface(null);
                setPeers([]);
                setInterfaceState(null);
                setIsLoading(false);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch interfaces.');
            console.error(err);
            setIsLoading(false);
        }
        // setIsLoading is handled inside handleSelectInterface for the combined loading state
    }, []); // Removed dependencies to prevent re-fetching loops

    useEffect(() => {
        fetchInterfaces();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleSelectInterface = useCallback(async (iface: Interface) => {
        if (!iface || !iface.name) return; // Guard against invalid selections
        setSelectedInterface(iface);
        setIsLoading(true);
        setError(null);
        try {
            const [configPeers, stateData, configDiffData] = await Promise.all([
                api.getPeers(iface.name),
                api.getInterfaceState(iface.name),
                api.getConfigDiff(iface.name),
            ]);

            const statePeersMap = new Map<string, StatePeer>(stateData.peers.map(p => [p.publicKey, p]));

            const mergedPeers: Peer[] = configPeers.map(cp => {
                const sp = statePeersMap.get(cp.publicKey);
                
                // Handle handshake formatting
                let handshakeStr = 'Never';
                let handshakeVal = 0;
                if (sp && sp.latestHandshake) {
                    // latestHandshake is now a Unix timestamp (seconds since epoch)
                    // Calculate seconds elapsed
                    const now = Math.floor(Date.now() / 1000);
                    const secondsElapsed = now - (sp.latestHandshake as number);
                    
                    if (secondsElapsed > 0) {
                        handshakeStr = formatHandshake(secondsElapsed);
                        handshakeVal = secondsElapsed; // Store the calculated seconds elapsed for sorting
                    }
                }

                // Handle transfer formatting
                let received = '';
                let sent = '';
                let rxBytes = 0;
                let txBytes = 0;
                if (sp) {
                    rxBytes = sp.transferRx || 0;
                    txBytes = sp.transferTx || 0;
                    
                    received = rxBytes > 0 ? formatBytes(rxBytes) : '';
                    sent = txBytes > 0 ? formatBytes(txBytes) : '';
                }

                return {
                    name: cp.name,
                    publicKey: cp.publicKey,
                    privateKey: cp.privateKey,
                    allowedIPs: cp.allowedIPs,
                    endpoint: cp.endpoint || '',
                    liveEndpoint: sp?.endpoint,
                    persistentKeepalive: sp?.persistentKeepalive || cp.persistentKeepalive || '',
                    latestHandshake: handshakeStr,
                    latestHandshakeValue: handshakeVal,
                    transfer: { received, sent },
                    transferValue: { received: rxBytes, sent: txBytes }
                };
            });

            setPeers(mergedPeers);
            setInterfaceState(stateData);
            setConfigDiff(configDiffData);
            setStateDiff(null); // No longer fetched
        } catch (err) {
            setError(err instanceof Error ? err.message : `Failed to load data for ${iface.name}.`);
            console.error(err);
            setPeers([]);
            setInterfaceState(null);
            setConfigDiff(null);
            setStateDiff(null);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const handleCreateInterface = async () => {
        setCreateInterfaceError(null);

        if (!newInterfaceName.trim() || !newInterfaceAddress.trim() || !newInterfacePort.trim()) {
            setCreateInterfaceError('All fields must be filled.');
            return;
        }
        const port = parseInt(newInterfacePort, 10);
        if (isNaN(port) || port <= 0 || port > 65535) {
            setCreateInterfaceError('Please enter a valid port number (1-65535).');
            return;
        }

        try {
            await api.createInterface({ name: newInterfaceName, address: newInterfaceAddress, listen_port: newInterfacePort });
            setNewInterfaceName('');
            setNewInterfaceAddress('10.0.1.1/24');
            setNewInterfacePort('51820');
            setCreateModalOpen(false);
            setCreateInterfaceError(null);
            await fetchInterfaces();
        } catch (err) {
            setError(err instanceof Error ? err.message : `Failed to create interface ${newInterfaceName}.`);
            console.error(err);
        }
    };

    const handleDeleteInterface = async (name: string) => {
        setDeleteConfirm({ isOpen: true, name });
    };

    const confirmDeleteInterface = async () => {
        const name = deleteConfirm.name;
        try {
            await api.deleteInterface(name);
            setSelectedInterface(null);
            await fetchInterfaces();
        } catch (err) {
            setError(err instanceof Error ? err.message : `Failed to delete interface ${name}.`);
            console.error(err);
        }
    };

    const handleOpenHostEditModal = () => {
        if (hostInfo) {
            setEditedHostIPs(hostInfo.ips.join('\n'));
            setHostEditError(null);
            setHostEditModalOpen(true);
        }
    };

    const handleSaveHostIPs = async () => {
        setHostEditError(null);
        setIsSavingHostIPs(true);
        const newIPs = editedHostIPs.split(/[\s,\n]+/).map(ip => ip.trim()).filter(Boolean);

        try {
            const updatedHostInfo = await api.updateHostIPs(newIPs);
            setHostInfo(updatedHostInfo);
            setHostEditModalOpen(false);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
            setHostEditError(errorMessage);
            console.error(err);
        } finally {
            setIsSavingHostIPs(false);
        }
    };

    const handleRescanHostIPs = async () => {
        setHostEditError(null);
        setIsRescanningHostIPs(true);
        try {
            const updatedHostInfo = await api.rescanHostIPs();
            setHostInfo(updatedHostInfo);
            setEditedHostIPs(updatedHostInfo.ips.join('\n'));
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
            setHostEditError(errorMessage);
            console.error(err);
        } finally {
            setIsRescanningHostIPs(false);
        }
    };

    const refreshData = () => {
        if (selectedInterface) {
            handleSelectInterface(selectedInterface);
        }
    }


    return (
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200 font-sans">
            <aside className="w-64 bg-white/70 dark:bg-gray-900/70 backdrop-blur-sm border-r border-gray-200/50 dark:border-gray-700/50 flex flex-col p-4">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center">
                        <ServerIcon className="w-8 h-8 mr-3 text-gray-700 dark:text-cyan-400" />
                        <h1 className="text-xl font-bold tracking-wider text-gray-900 dark:text-gray-100">WG Manager</h1>
                    </div>
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-full hover:bg-gray-200/50 dark:hover:bg-gray-700/50 text-gray-600 dark:text-gray-400 transition-colors"
                        aria-label="Toggle theme"
                    >
                        {theme === 'light' ? <MoonIcon className="w-5 h-5" /> : <SunIcon className="w-5 h-5" />}
                    </button>
                </div>
                <button
                    onClick={() => setCreateModalOpen(true)}
                    className="w-full flex items-center justify-center bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded-lg transition-all duration-200 mb-4 shadow-md hover:shadow-lg"
                >
                    <PlusIcon className="w-5 h-5 mr-2" />
                    New Interface
                </button>
                <InterfaceList
                    interfaces={interfaces}
                    selectedInterface={selectedInterface}
                    onSelect={handleSelectInterface}
                />
                <div className="mt-auto pt-4 border-t border-gray-200/50 dark:border-gray-700/50 text-xs text-gray-500 dark:text-gray-400">
                    <div className="flex justify-between items-center mb-1">
                        <p className="font-semibold">
                            Host Information
                            {hostInfo && typeof hostInfo.manual !== 'undefined' && (
                                <span className="ml-2 text-xs font-normal text-gray-400 dark:text-gray-500">
                                    ({hostInfo.manual ? 'manual' : 'auto'})
                                </span>
                            )}
                        </p>
                        {hostInfo && (
                            <button onClick={handleOpenHostEditModal} className="p-1 rounded text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200/60 dark:hover:bg-gray-700/60 transition-colors">
                                <PencilIcon className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                    {hostInfo ? (
                        <div className="space-y-1 max-h-24 overflow-y-auto pr-1">
                            {hostInfo.ips && hostInfo.ips.length > 0 ? hostInfo.ips.map(ip => (
                                <p key={ip} className="font-mono truncate" title={ip}>{ip}</p>
                            )) : <p>No public IPs found</p>}
                            {hostInfo.message && <p className="text-gray-400 dark:text-gray-500 text-xs mt-1">{hostInfo.message}</p>}
                        </div>
                    ) : (
                        <p>Loading host info...</p>
                    )}
                </div>
            </aside>
            <main className="flex-1 p-6 overflow-y-auto">
                {selectedInterface ? (
                    <InterfaceDetail
                        interface={selectedInterface}
                        hostInfo={hostInfo}
                        peers={peers}
                        interfaceState={interfaceState}
                        configDiff={configDiff}
                        isLoading={isLoading}
                        error={error}
                        refreshData={refreshData}
                        onDeleteInterface={handleDeleteInterface}
                    />
                ) : (
                    <div className="flex flex-col items-center justify-center h-full">
                        <ServerIcon className="w-24 h-24 text-gray-400 dark:text-gray-600 mb-6" />
                        <div className="text-center max-w-md">
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                                {isLoading ? 'Loading Interfaces...' : 'No Interface Selected'}
                            </h2>

                            {error ? (
                                <div className="mt-6 p-4 bg-red-100 dark:bg-red-900/20 border border-red-400/30 dark:border-red-500/30 text-red-700 dark:text-red-300 rounded-lg text-sm flex items-start text-left shadow-sm">
                                    <ExclamationIcon className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
                                    <div>
                                        <p className="font-semibold mb-1">An error occurred</p>
                                        <p className="opacity-90">{error}</p>
                                    </div>
                                </div>
                            ) : (
                                <p className="text-gray-600 dark:text-gray-500">
                                    {isLoading ? 'Please wait.' : 'Select an interface from the sidebar or create a new one to get started.'}
                                </p>
                            )}
                        </div>
                    </div>
                )}
            </main>

            <Modal isOpen={isCreateModalOpen} onClose={() => { setCreateModalOpen(false); setCreateInterfaceError(null); }} title="Create New Interface">
                <div className="space-y-4">
                    <div>
                        <label htmlFor="interfaceName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Interface Name
                        </label>
                        <input
                            type="text" id="interfaceName" value={newInterfaceName}
                            onChange={(e) => setNewInterfaceName(e.target.value)}
                            placeholder="e.g., wg0"
                            className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 text-gray-900 dark:text-white focus:ring-gray-500 focus:border-gray-500 dark:focus:ring-cyan-500 dark:focus:border-cyan-500"
                        />
                    </div>
                    <div>
                        <label htmlFor="address" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Interface Address
                        </label>
                        <input
                            type="text" id="address" value={newInterfaceAddress}
                            onChange={(e) => setNewInterfaceAddress(e.target.value)}
                            placeholder="e.g., 10.0.1.1/24"
                            className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 text-gray-900 dark:text-white focus:ring-gray-500 focus:border-gray-500 dark:focus:ring-cyan-500 dark:focus:border-cyan-500"
                        />
                    </div>
                    <div>
                        <label htmlFor="port" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Listen Port
                        </label>
                        <input
                            type="text" id="port" value={newInterfacePort}
                            onChange={(e) => setNewInterfacePort(e.target.value)}
                            placeholder="e.g., 51820"
                            className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 text-gray-900 dark:text-white focus:ring-gray-500 focus:border-gray-500 dark:focus:ring-cyan-500 dark:focus:border-cyan-500"
                        />
                    </div>

                    {createInterfaceError && (
                        <div className="p-3 bg-red-100 dark:bg-red-900/20 border border-red-400/30 dark:border-red-500/30 text-red-700 dark:text-red-300 rounded-md text-sm flex items-start">
                            <ExclamationIcon className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
                            <div>{createInterfaceError}</div>
                        </div>
                    )}

                    <div className="flex justify-end space-x-2 pt-2">
                        <button onClick={() => setCreateModalOpen(false)} className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition">Cancel</button>
                        <button onClick={handleCreateInterface} className="px-4 py-2 rounded-md bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold transition">Create</button>
                    </div>
                </div>
            </Modal>

            <Modal isOpen={isHostEditModalOpen} onClose={() => setHostEditModalOpen(false)} title="Edit Host IPs">
                <div className="space-y-4">
                    <div>
                        <label htmlFor="hostIPs" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            IP Addresses
                        </label>
                        <textarea
                            id="hostIPs"
                            rows={4}
                            value={editedHostIPs}
                            onChange={(e) => setEditedHostIPs(e.target.value)}
                            placeholder="One IP per line"
                            className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 text-gray-900 dark:text-white font-mono focus:ring-gray-500 focus:border-gray-500 dark:focus:ring-cyan-500 dark:focus:border-cyan-500"
                        />
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Enter one IP address per line. These will be used as the endpoint for client configs.</p>
                    </div>

                    {hostEditError && (
                        <div className="p-3 bg-red-100 dark:bg-red-900/20 border border-red-400/30 dark:border-red-500/30 text-red-700 dark:text-red-300 rounded-md text-sm flex items-start">
                            <ExclamationIcon className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
                            <div>{hostEditError}</div>
                        </div>
                    )}

                    <div className="flex justify-between items-center pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
                        <button
                            onClick={handleRescanHostIPs}
                            disabled={isSavingHostIPs || isRescanningHostIPs}
                            className="flex items-center px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 text-sm font-semibold transition disabled:opacity-50"
                        >
                            <RefreshIcon className={`w-4 h-4 mr-2 ${isRescanningHostIPs ? 'animate-spin' : ''}`} />
                            {isRescanningHostIPs ? 'Rescanning...' : 'Rescan'}
                        </button>
                        <div className="space-x-2">
                            <button onClick={() => setHostEditModalOpen(false)} className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition">Cancel</button>
                            <button
                                onClick={handleSaveHostIPs}
                                disabled={isSavingHostIPs || isRescanningHostIPs}
                                className="px-4 py-2 rounded-md bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold transition disabled:opacity-50"
                            >
                                {isSavingHostIPs ? 'Saving...' : 'Save'}
                            </button>
                        </div>
                    </div>
                </div>
            </Modal>

            <ConfirmDialog
                isOpen={deleteConfirm.isOpen}
                onClose={() => setDeleteConfirm({ isOpen: false, name: '' })}
                onConfirm={confirmDeleteInterface}
                title="Delete Interface"
                message={`Are you sure you want to delete the interface "${deleteConfirm.name}"? This action cannot be undone.`}
                variant="danger"
                confirmText="Delete"
            />
        </div>
    );
};

export default App;
