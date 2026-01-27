import React from 'react';
import { ExclamationIcon, CheckIcon } from './icons/Icons';

interface ConfirmDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    variant?: 'danger' | 'warning' | 'info';
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    variant = 'warning'
}) => {
    if (!isOpen) return null;

    const handleConfirm = () => {
        onConfirm();
        onClose();
    };

    const variantStyles = {
        danger: {
            bg: 'bg-red-100 dark:bg-red-900/20',
            border: 'border-red-400/30 dark:border-red-500/30',
            text: 'text-red-700 dark:text-red-300',
            button: 'bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600'
        },
        warning: {
            bg: 'bg-yellow-100 dark:bg-yellow-900/20',
            border: 'border-yellow-400/30 dark:border-yellow-500/30',
            text: 'text-yellow-700 dark:text-yellow-300',
            button: 'bg-yellow-600 hover:bg-yellow-700 dark:bg-yellow-500 dark:hover:bg-yellow-600'
        },
        info: {
            bg: 'bg-blue-100 dark:bg-blue-900/20',
            border: 'border-blue-400/30 dark:border-blue-500/30',
            text: 'text-blue-700 dark:text-blue-300',
            button: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600'
        }
    };

    const styles = variantStyles[variant];

    return (
        <div className="fixed inset-0 bg-black bg-opacity-70 z-50 flex justify-center items-center backdrop-blur-sm" onClick={onClose}>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md m-4 border border-gray-200 dark:border-gray-700" onClick={e => e.stopPropagation()}>
                <div className="p-6">
                    <div className={`p-4 ${styles.bg} border ${styles.border} rounded-lg mb-4`}>
                        <div className="flex items-start">
                            <ExclamationIcon className={`w-6 h-6 mr-3 mt-0.5 flex-shrink-0 ${styles.text}`} />
                            <div>
                                <h3 className={`text-lg font-bold ${styles.text} mb-2`}>{title}</h3>
                                <p className={`text-sm ${styles.text}`}>{message}</p>
                            </div>
                        </div>
                    </div>
                    <div className="flex justify-end space-x-3">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition"
                        >
                            {cancelText}
                        </button>
                        <button
                            onClick={handleConfirm}
                            className={`px-4 py-2 rounded-md text-white font-semibold transition ${styles.button}`}
                        >
                            {confirmText}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

interface NotificationDialogProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    message: string;
    variant?: 'success' | 'error' | 'info';
}

export const NotificationDialog: React.FC<NotificationDialogProps> = ({
    isOpen,
    onClose,
    title,
    message,
    variant = 'info'
}) => {
    if (!isOpen) return null;

    const variantStyles = {
        success: {
            bg: 'bg-green-100 dark:bg-green-900/20',
            border: 'border-green-400/30 dark:border-green-500/30',
            text: 'text-green-700 dark:text-green-300',
            icon: CheckIcon
        },
        error: {
            bg: 'bg-red-100 dark:bg-red-900/20',
            border: 'border-red-400/30 dark:border-red-500/30',
            text: 'text-red-700 dark:text-red-300',
            icon: ExclamationIcon
        },
        info: {
            bg: 'bg-blue-100 dark:bg-blue-900/20',
            border: 'border-blue-400/30 dark:border-blue-500/30',
            text: 'text-blue-700 dark:text-blue-300',
            icon: ExclamationIcon
        }
    };

    const styles = variantStyles[variant];
    const Icon = styles.icon;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-70 z-50 flex justify-center items-center backdrop-blur-sm" onClick={onClose}>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md m-4 border border-gray-200 dark:border-gray-700" onClick={e => e.stopPropagation()}>
                <div className="p-6">
                    <div className={`p-4 ${styles.bg} border ${styles.border} rounded-lg mb-4`}>
                        <div className="flex items-start">
                            <Icon className={`w-6 h-6 mr-3 mt-0.5 flex-shrink-0 ${styles.text}`} />
                            <div>
                                <h3 className={`text-lg font-bold ${styles.text} mb-2`}>{title}</h3>
                                <p className={`text-sm ${styles.text}`}>{message}</p>
                            </div>
                        </div>
                    </div>
                    <div className="flex justify-end">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 rounded-md bg-gray-800 hover:bg-gray-700 dark:bg-cyan-500 dark:hover:bg-cyan-600 text-white font-semibold transition"
                        >
                            OK
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
