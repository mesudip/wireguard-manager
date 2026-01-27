
import React from 'react';
import { Interface } from '../types';
import { ChevronRightIcon } from './icons/Icons';

interface InterfaceListProps {
    interfaces: Interface[];
    selectedInterface: Interface | null;
    onSelect: (iface: Interface) => void;
}

const InterfaceList: React.FC<InterfaceListProps> = ({ interfaces, selectedInterface, onSelect }) => {
    return (
        <nav className="flex-1 space-y-2">
            {interfaces.map((iface) => (
                <button
                    key={iface.name}
                    onClick={() => onSelect(iface)}
                    className={`w-full text-left flex items-center p-3 rounded-lg transition-all duration-200 ${
                        selectedInterface?.name === iface.name
                            ? 'bg-gray-200/80 dark:bg-cyan-500/20 text-gray-800 dark:text-cyan-300'
                            : 'hover:bg-gray-200/50 dark:hover:bg-gray-700/50 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                    }`}
                >
                    <span className="flex-1 font-medium">{iface.name}</span>
                    <ChevronRightIcon className="w-5 h-5" />
                </button>
            ))}
        </nav>
    );
};

export default InterfaceList;
