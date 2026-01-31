import os
import json
import socket
import subprocess
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from pathlib import Path

class HostInfoService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.cache_file = os.path.join(base_dir, "host_info.json")
        self.logger = None  # Will be set if needed, but we'll use print/exceptions for now

    def _get_physical_interfaces(self) -> List[str]:
        """Identify physical network interfaces."""
        interfaces = []
        net_dir = "/sys/class/net"
        if not os.path.exists(net_dir):
            return []
            
        for iface in os.listdir(net_dir):
            iface_path = os.path.join(net_dir, iface)
            # Physical interfaces usually have a 'device' symlink
            device_path = os.path.join(iface_path, "device")
            if os.path.islink(device_path):
                # Exclude virtual interfaces like bridge, veth, etc. 
                # even if they have some device mapping in some setups
                # but /sys/class/net/eth0/device existence is a strong indicator
                interfaces.append(iface)
        return interfaces

    def _get_ips_from_interface(self, iface: str) -> List[str]:
        """Extract global IPs from a specific interface using 'ip addr' command."""
        ips = []
        try:
            # We use 'ip -o addr show' for easier parsing
            result = subprocess.run(
                ["ip", "-o", "addr", "show", iface, "scope", "global"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4:
                    # parts[3] is the IP/CIDR
                    ip_with_cidr = parts[3]
                    ip = ip_with_cidr.split('/')[0]
                    ips.append(ip)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return ips

    def _get_external_ip(self, version: int = 4) -> Optional[str]:
        """Get external IP using multiple fallback services."""
        if version == 6:
            urls = [
                "https://ipv6.ifconfig.me",
                "https://api6.ipify.org",
            ]
        else:
            urls = [
                "https://ipv4.ifconfig.me",
                "https://api.ipify.org",
            ]
        
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    return response.read().decode('utf-8').strip()
            except (urllib.error.URLError, socket.timeout):
                continue
        return None

    def update_host_info(self, force: bool = False) -> Dict[str, Any]:
        """
        Update host info:
        1. Load existing cache. If manual and not forced, skip discovery.
        2. Infer from physical interfaces.
        3. If fails, use ifconfig.me.
        4. If fails, return existing cache.
        5. If no cache, return error.
        """
        existing_info = {}
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    existing_info = json.load(f)
            except Exception:
                pass
        
        # If manual discovery is set and we're not forcing, respect it
        if existing_info.get("manual") and not force:
            return existing_info

        ips = []
        physical_ifaces = self._get_physical_interfaces()
        
        for iface in physical_ifaces:
            iface_ips = self._get_ips_from_interface(iface)
            ips.extend(iface_ips)
            
        if not ips:
            # Fallback to ifconfig.me
            ipv4 = self._get_external_ip(4)
            ipv6 = self._get_external_ip(6)
            if ipv4: ips.append(ipv4)
            if ipv6: ips.append(ipv6)
            
        # Final deduplication and cleaning, preserve order
        seen = set()
        cleaned_ips = []
        for ip in ips:
            ip = ip.strip()
            if ip and ip not in seen:
                cleaned_ips.append(ip)
                seen.add(ip)
        ips = cleaned_ips
            
        if ips:
            host_info = {
                "ips": ips,
                "manual": False,
                "updated_at": socket.gethostname() 
            }
            # Save to cache
            try:
                os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
                with open(self.cache_file, 'w') as f:
                    json.dump(host_info, f)
                return host_info
            except Exception:
                pass # Continue to load from cache if save fails

        return existing_info if existing_info else {"error": "Could not determine host IP addresses", "ips": []}

    def save_host_info(self, ips: List[str], manual: bool = True) -> Dict[str, Any]:
        """Manually update and save host info. Preserves the order of IPs provided by user."""
        # Clean and deduplicate while preserving order
        seen = set()
        cleaned_ips = []
        for ip in ips:
            ip = ip.strip()
            if ip and ip not in seen:
                cleaned_ips.append(ip)
                seen.add(ip)
        
        host_info = {
            "ips": cleaned_ips,
            "manual": manual,
            "updated_at": socket.gethostname()
        }
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(host_info, f)
            return host_info
        except Exception as e:
            return {"error": f"Failed to save host info: {str(e)}", "ips": cleaned_ips}

    def get_host_info(self) -> Dict[str, Any]:
        """Retrieve host info from cache or error if not found."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"error": "Host info not available. Service may need to restart.", "ips": []}
