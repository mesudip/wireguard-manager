
import React, { useEffect, useMemo, useState } from 'react';
import { HostInfo, Interface, Peer, Template } from '../../types';
import Modal from '../Modal';
import { ClipboardCopyIcon, CheckIcon } from '../icons/Icons';
import QRCode from 'qrcode';

interface SharePeerModalProps {
    isOpen: boolean;
    onClose: () => void;
    peer: Peer;
    iface: Interface;
    hostInfo: HostInfo | null;
}

const DEFAULT_TEMPLATE_NAME = '__standard__';

const SharePeerModal: React.FC<SharePeerModalProps> = ({ isOpen, onClose, peer, iface, hostInfo }) => {
    const [copySuccess, setCopySuccess] = useState(false);
    const [selectedTemplate, setSelectedTemplate] = useState<string>(DEFAULT_TEMPLATE_NAME);
    const [configText, setConfigText] = useState('');
    const [qrCodeUrl, setQrCodeUrl] = useState('');

    const templates = hostInfo?.templates || [];
    const defaultTemplateName = hostInfo?.defaultTemplate || DEFAULT_TEMPLATE_NAME;

    useEffect(() => {
        if (isOpen) {
            setSelectedTemplate(defaultTemplateName || DEFAULT_TEMPLATE_NAME);
        }
    }, [isOpen, defaultTemplateName]);

    useEffect(() => {
        if (selectedTemplate === DEFAULT_TEMPLATE_NAME) return;
        const exists = templates.some(t => t.name === selectedTemplate);
        if (!exists) {
            setSelectedTemplate(DEFAULT_TEMPLATE_NAME);
        }
    }, [selectedTemplate, templates]);

    const endpoint = useMemo(() => {
        const firstIp = hostInfo?.ips?.[0];
        if (!firstIp) return `YOUR_SERVER_IP:${iface.listenPort}`;
        const isIPv6 = firstIp.includes(':');
        return isIPv6 ? `[${firstIp}]:${iface.listenPort}` : `${firstIp}:${iface.listenPort}`;
    }, [hostInfo?.ips, iface.listenPort]);

    const defaultConfig = useMemo(() => {
        const dnsValue = iface.dns || '8.8.8.8';
        return `[Interface]
# Name = ${peer.name}
PrivateKey = ${peer.privateKey || '<--Paste-Your-Private-Key-Here-->'}
Address = ${peer.allowedIPs.split(',')[0]}
DNS = ${dnsValue}

[Peer]
# ${iface.name}
PublicKey = ${iface.publicKey}
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = ${endpoint}
${peer.persistentKeepalive ? `PersistentKeepalive = ${peer.persistentKeepalive}\n` : ''}`;
    }, [peer, iface, endpoint]);

    const selectedTemplateContent = useMemo(() => {
        if (selectedTemplate === DEFAULT_TEMPLATE_NAME) return null;
        return templates.find(t => t.name === selectedTemplate)?.content || null;
    }, [selectedTemplate, templates]);

    const parseAllowedIPs = (allowedIPs: string) => {
        const firstIP = allowedIPs.split(',')[0]?.trim() || '';
        const lastSlashIndex = firstIP.lastIndexOf('/');
        const ipOnly = lastSlashIndex !== -1 ? firstIP.substring(0, lastSlashIndex) : firstIP;
        const subnetOnly = lastSlashIndex !== -1 ? firstIP.substring(lastSlashIndex) : '';
        const extraIPs = allowedIPs.split(',').slice(1).map(ip => ip.trim()).join(', ');
        return { ipOnly, subnetOnly, extraIPs };
    };

    useEffect(() => {
        const { ipOnly, subnetOnly, extraIPs } = parseAllowedIPs(peer.allowedIPs);
        const replacements: Record<string, string> = {
            DefaultConfig: defaultConfig,
            PeerName: peer.name,
            PeerPrivateKey: peer.privateKey || '<--Paste-Your-Private-Key-Here-->',
            PeerPublicKey: peer.publicKey || '',
            PeerAllowedIPs: peer.allowedIPs,
            PeerAllowedIP: ipOnly,
            PeerAllowedSubnet: subnetOnly,
            PeerExtraIPs: extraIPs,
            PeerEndpoint: peer.endpoint || '',
            PeerPersistentKeepalive: peer.persistentKeepalive || '',
            InterfaceName: iface.name,
            InterfacePublicKey: iface.publicKey,
            InterfaceAddress: iface.address,
            InterfaceListenPort: String(iface.listenPort),
            InterfaceDNS: iface.dns || '',
            InterfacePostUp: iface.postUp || '',
            InterfacePostDown: iface.postDown || '',
            HostIPs: (hostInfo?.ips || []).join(', '),
            HostPrimaryIP: hostInfo?.ips?.[0] || '',
            HostEndpoint: endpoint
        };

        let nextConfig = defaultConfig;
        if (selectedTemplateContent) {
            nextConfig = selectedTemplateContent.includes('{{DefaultConfig}}')
                ? selectedTemplateContent.replaceAll('{{DefaultConfig}}', defaultConfig)
                : selectedTemplateContent;
        }

        nextConfig = nextConfig.replace(/\{\{\s*([A-Za-z0-9_]+)\s*\}\}/g, (match, key) => {
            return Object.prototype.hasOwnProperty.call(replacements, key) ? replacements[key] : match;
        });

        setConfigText(nextConfig);
    }, [defaultConfig, selectedTemplateContent, peer, iface, hostInfo, endpoint]);

    useEffect(() => {
        let isActive = true;
        if (!configText) {
            setQrCodeUrl('');
            return;
        }
        QRCode.toDataURL(configText, { width: 256, margin: 1 })
            .then(url => {
                if (isActive) setQrCodeUrl(url);
            })
            .catch(err => {
                console.error('Failed to generate QR code', err);
                if (isActive) setQrCodeUrl('');
            });
        return () => { isActive = false; };
    }, [configText]);

    const copyToClipboard = () => {
        navigator.clipboard.writeText(configText).then(() => {
            setCopySuccess(true);
            setTimeout(() => setCopySuccess(false), 2000);
        });
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={`Client Config for ${peer?.name}`} maxWidth="max-w-6xl">
            <div>
                <div className="mb-4">
                    <label htmlFor="templateSelect" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Template
                    </label>
                    <select
                        id="templateSelect"
                        value={selectedTemplate}
                        onChange={(e) => setSelectedTemplate(e.target.value)}
                        className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 text-gray-900 dark:text-white focus:ring-gray-500 focus:border-gray-500 dark:focus:ring-cyan-500 dark:focus:border-cyan-500"
                    >
                        {defaultTemplateName === DEFAULT_TEMPLATE_NAME && (
                            <option value={DEFAULT_TEMPLATE_NAME}>Standard (built-in)</option>
                        )}
                        {templates.map((template: Template) => (
                            <option key={template.name} value={template.name}>{template.name}</option>
                        ))}
                    </select>
                </div>
                <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">
                    <div className="flex-1 w-full relative bg-gray-100 dark:bg-gray-900 rounded-md p-4 font-mono text-xs border border-gray-300 dark:border-gray-600">
                        <button
                            onClick={copyToClipboard}
                            className="absolute top-2 right-2 p-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                            aria-label="Copy to clipboard"
                        >
                            {copySuccess ? <CheckIcon className="w-5 h-5 text-green-500" /> : <ClipboardCopyIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />}
                        </button>
                        <pre className="whitespace-pre-wrap break-all">
                            <code>
                                {configText}
                            </code>
                        </pre>
                    </div>
                    <div className="flex-shrink-0 flex flex-col items-center justify-center p-4 bg-white rounded-md">
                         {qrCodeUrl ? (
                            <img src={qrCodeUrl} alt="WireGuard Config QR Code" className="w-48 h-48 md:w-56 md:h-56"/>
                        ) : (
                            <div className="w-48 h-48 md:w-56 md:h-56 flex items-center justify-center">
                                <p className="text-gray-500">Generating QR code...</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="mt-6 flex justify-end">
                    <button onClick={onClose} className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700 transition">Close</button>
                </div>
            </div>
        </Modal>
    );
};

export default SharePeerModal;
