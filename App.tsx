
import React, { useState, useEffect, useCallback } from 'react';
import { Interface, Peer, InterfaceState, DiffResult, StatePeer } from './types';
import * as api from './services/api';
import { formatBytes, formatHandshake } from './utils';
import InterfaceList from './components/InterfaceList';
import InterfaceDetail from './components/InterfaceDetail';
import { PlusIcon, ServerIcon, SunIcon, MoonIcon } from './components/icons/Icons';
import Modal from './components/Modal';

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
            setInterfaces(data);
            if (data.length > 0 && !selectedInterface) {
                // Automatically select the first interface if none is selected
                handleSelectInterface(data[0]);
            } else if (data.length === 0) {
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
            const [configPeers, stateData, configDiffData, stateDiffData] = await Promise.all([
                api.getPeers(iface.name),
                api.getInterfaceState(iface.name),
                api.getConfigDiff(iface.name),
                api.getStateDiff(iface.name),
            ]);

            const statePeersMap = new Map<string, StatePeer>(stateData.peers.map(p => [p.publicKey, p]));

            const mergedPeers: Peer[] = configPeers.map(cp => {
                const sp = statePeersMap.get(cp.publicKey);
                return {
                    name: cp.name,
                    publicKey: cp.publicKey,
                    allowedIPs: cp.allowedIPs,
                    endpoint: sp?.endpoint || cp.endpoint || 'N/A',
                    latestHandshake: sp ? formatHandshake(sp.latestHandshake) : 'Never',
                    transfer: {
                        received: sp ? formatBytes(sp.transferRx) : '0 B',
                        sent: sp ? formatBytes(sp.transferTx) : '0 B',
                    }
                };
            });

            setPeers(mergedPeers);
            setInterfaceState(stateData);
            setConfigDiff(configDiffData);
            setStateDiff(stateDiffData);
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
        if (!newInterfaceName.trim() || !newInterfaceAddress.trim() || !newInterfacePort.trim()) {
            alert('All fields must be filled.');
            return;
        }
        const port = parseInt(newInterfacePort, 10);
        if (isNaN(port) || port <= 0 || port > 65535) {
            alert('Please enter a valid port number (1-65535).');
            return;
        }

        try {
            await api.createInterface({ name: newInterfaceName, address: newInterfaceAddress, listen_port: newInterfacePort });
            setNewInterfaceName('');
            setNewInterfaceAddress('10.0.1.1/24');
            setNewInterfacePort('51820');
            setCreateModalOpen(false);
            await fetchInterfaces();
        } catch (err) {
            setError(err instanceof Error ? err.message : `Failed to create interface ${newInterfaceName}.`);
            console.error(err);
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
            </aside>
            <main className="flex-1 p-6 overflow-y-auto">
                {selectedInterface ? (
                    <InterfaceDetail
                        interface={selectedInterface}
                        peers={peers}
                        interfaceState={interfaceState}
                        configDiff={configDiff}
                        stateDiff={stateDiff}
                        isLoading={isLoading}
                        error={error}
                        refreshData={refreshData}
                    />
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                            <ServerIcon className="w-24 h-24 mx-auto text-gray-500 dark:text-gray-600" />
                            <h2 className="mt-4 text-2xl font-semibold text-gray-500 dark:text-gray-400">
                                {isLoading ? 'Loading Interfaces...' : 'No Interface Selected'}
                            </h2>
                            <p className="mt-2 text-gray-600 dark:text-gray-500">
                                {isLoading ? 'Please wait.' : error ? error : 'Select an interface or create a new one.'}
                            </p>
                        </div>
                    </div>
                )}
            </main>

            <Modal isOpen={isCreateModalOpen} onClose={() => setCreateModalOpen(false)} title="Create New Interface">
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
                            Address
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
                    <div className="flex justify-end space-x-2 pt-2">
                        <button onClick={() => setCreateModalOpen(false)} className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition">Cancel</button>
                        <button onClick={handleCreateInterface} className="px-4 py-2 rounded-md bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold transition">Create</button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default App;
