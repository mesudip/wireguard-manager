
import React from 'react';

interface DiffViewerProps {
    diff: string;
}

const DiffViewer: React.FC<DiffViewerProps> = ({ diff }) => {
    const lines = diff.trim().split('\n');

    const getLineClass = (line: string) => {
        if (line.startsWith('+')) return 'bg-green-500/10 text-green-700 dark:text-green-300';
        if (line.startsWith('-')) return 'bg-red-500/10 text-red-700 dark:text-red-300';
        if (line.startsWith('@')) return 'bg-cyan-500/10 text-cyan-700 dark:text-cyan-300';
        return 'text-gray-500 dark:text-gray-400';
    };

    return (
        <div className="font-mono text-sm bg-gray-50/70 dark:bg-gray-900/70 p-4 rounded-md overflow-x-auto border border-gray-200/50 dark:border-gray-700/50 mt-4">
            <pre>
                {lines.map((line, index) => (
                    <div key={index} className={`whitespace-pre-wrap ${getLineClass(line)}`}>
                        {line}
                    </div>
                ))}
            </pre>
        </div>
    );
};

export default DiffViewer;
