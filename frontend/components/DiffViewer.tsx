
import React from 'react';

interface DiffViewerProps {
    diff: string;
}

type DiffLine = { type: 'add' | 'del'; content: string };
type DiffHunk = { header: string; lines: DiffLine[] };

const parseUnifiedDiff = (diff: string): DiffHunk[] => {
    const lines = diff.trim().split('\n').filter(Boolean);
    const hunks: DiffHunk[] = [];
    let current: DiffHunk = { header: '', lines: [] };

    const pushHunk = () => {
        if (current.header || current.lines.length > 0) {
            hunks.push(current);
        }
        current = { header: '', lines: [] };
    };

    lines.forEach(line => {
        if (line.startsWith('---') || line.startsWith('+++')) {
            return;
        }
        if (line.startsWith('@@')) {
            pushHunk();
            current.header = line.replace(/^@@\s*|\s*@@$/g, '').trim();
            return;
        }
        if (line.startsWith('-') && !line.startsWith('---')) {
            current.lines.push({ type: 'del', content: line.slice(1) });
            return;
        }
        if (line.startsWith('+') && !line.startsWith('+++')) {
            current.lines.push({ type: 'add', content: line.slice(1) });
            return;
        }
        // Skip context lines for a compact, change-focused view
    });

    pushHunk();
    return hunks;
};

const DiffViewer: React.FC<DiffViewerProps> = ({ diff }) => {
    if (!diff || !diff.trim()) return null;
    const hunks = parseUnifiedDiff(diff);

    return (
        <div className="space-y-3 mt-4">
            <div className="flex items-center text-xs text-gray-600 dark:text-gray-400">
                <span className="text-red-600 dark:text-red-400">- current.conf</span>
                <span className="ml-3 text-green-600 dark:text-green-400">+ managed folder</span>
            </div>
            <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm overflow-x-auto border border-gray-300 dark:border-gray-700">
                {hunks.map((hunk, idx) => (
                    <div key={`${hunk.header}-${idx}`} className={idx > 0 ? 'mt-3 pt-3 border-t border-gray-300 dark:border-gray-700' : ''}>
                        {hunk.header && (
                            <div className="text-cyan-700 dark:text-cyan-400 text-xs mb-2">{hunk.header}</div>
                        )}
                        {hunk.lines.length > 0 ? (
                            hunk.lines.map((line, lineIdx) => (
                                <div key={`${line.type}-${lineIdx}`} className={line.type === 'del' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}>
                                    {line.type === 'del' ? '- ' : '+ '}{line.content || '(blank)'}
                                </div>
                            ))
                        ) : (
                            <div className="text-gray-500 dark:text-gray-500 text-xs">No changes in this block.</div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DiffViewer;
