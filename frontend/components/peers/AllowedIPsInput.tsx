
import React, { useState, useRef, useEffect } from 'react';

// --- Helper Functions ---
const parseAndAddIPs = (value: string, setList: React.Dispatch<React.SetStateAction<string[]>>) => {
    const newIPs = value
        .split(/[\s,]+/)
        .map(ip => ip.trim())
        .filter(ip => ip.length > 0);
    if (newIPs.length > 0) {
        setList(prevList => {
            const seenIPs = new Set(prevList);
            const result = [...prevList];
            for (const ip of newIPs) {
                if (!seenIPs.has(ip)) {
                    result.push(ip);
                    seenIPs.add(ip);
                }
            }
            return result;
        });
    }
};

const removeAllowedIP = (ipToRemove: string, setList: React.Dispatch<React.SetStateAction<string[]>>) => {
    setList(prevList => prevList.filter(ip => ip !== ipToRemove));
};


interface AllowedIPsInputProps {
    list: string[];
    setList: React.Dispatch<React.SetStateAction<string[]>>;
    input: string;
    setInput: React.Dispatch<React.SetStateAction<string>>;
}

const AllowedIPsInput: React.FC<AllowedIPsInputProps> = ({ list, setList, input, setInput }) => {
    const [editingIndex, setEditingIndex] = useState<number | null>(null);
    const [editingValue, setEditingValue] = useState('');
    const editInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (editingIndex !== null) {
            editInputRef.current?.focus();
            editInputRef.current?.select();
        }
    }, [editingIndex]);

    const handleAddNewKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && input.trim()) {
            e.preventDefault();
            parseAndAddIPs(input, setList);
            setInput('');
        }
    };

    const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
        e.preventDefault();
        const pastedText = e.clipboardData.getData('text');
        parseAndAddIPs(pastedText, setList);
        setInput('');
    };

    const handleAddNewBlur = () => {
        if (input.trim()) {
            parseAndAddIPs(input, setList);
            setInput('');
        }
    };

    const startEditing = (index: number) => {
        setEditingIndex(index);
        setEditingValue(list[index]);
    };

    const saveEdit = () => {
        if (editingIndex === null) return;
        
        const updatedValue = editingValue.trim();
        const newList = [...list];

        if (updatedValue === '') {
            newList.splice(editingIndex, 1);
        } else {
            if (!newList.some((ip, i) => ip === updatedValue && i !== editingIndex)) {
                newList[editingIndex] = updatedValue;
            }
        }
        
        setList(newList);
        setEditingIndex(null);
        setEditingValue('');
    };

    const handleEditKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveEdit();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            setEditingIndex(null);
            setEditingValue('');
        }
    };

    return (
        <div>
            <label htmlFor="allowedIPs" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Allowed IPs</label>
            <div className="flex flex-wrap items-center gap-2 p-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md">
                {list.map((ip, index) => (
                    <div key={`${ip}-${index}`}>
                        {editingIndex === index ? (
                            <input
                                ref={editInputRef}
                                type="text"
                                value={editingValue}
                                onChange={(e) => setEditingValue(e.target.value)}
                                onBlur={saveEdit}
                                onKeyDown={handleEditKeyDown}
                                className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 text-sm font-mono px-2 py-1 rounded-md border border-cyan-500 focus:outline-none"
                                style={{ width: `${Math.max(editingValue.length, 10)}ch` }}
                            />
                        ) : (
                            <span 
                                onClick={() => startEditing(index)}
                                className="flex items-center bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm font-mono px-2 py-1 rounded-md cursor-pointer hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                            >
                                {ip}
                                <button 
                                    onClick={(e) => { 
                                        e.stopPropagation(); 
                                        removeAllowedIP(ip, setList); 
                                    }} 
                                    className="ml-2 text-gray-500 hover:text-gray-800 dark:hover:text-white"
                                    aria-label={`Remove ${ip}`}
                                >
                                    &times;
                                </button>
                            </span>
                        )}
                    </div>
                ))}
                <input
                    id="allowedIPs"
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleAddNewKeyDown}
                    onPaste={handlePaste}
                    onBlur={handleAddNewBlur}
                    placeholder={list.length === 0 ? "e.g., 10.0.1.2/32" : "Add more..."}
                    className="flex-grow bg-transparent focus:outline-none p-1 min-w-[120px] text-sm font-mono"
                />
            </div>
        </div>
    );
};

export default AllowedIPsInput;
