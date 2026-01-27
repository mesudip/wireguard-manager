import logging
import ipaddress
from typing import List, Tuple
from flask import Request

logger = logging.getLogger(__name__)


class AccessControl:
    def __init__(self, allowed_proxies: List[str], allowed_ips: List[str]):
        # Normalize and validate
        self.allowed_proxies = self._compile_nets(allowed_proxies)
        self.allowed_ips = self._compile_nets(allowed_ips)

    def _compile_nets(self, entries: List[str]) -> List[ipaddress._BaseNetwork]:
        nets = []
        for e in entries:
            e = e.strip()
            if not e:
                continue
            try:
                # Accept single IP or network
                if '/' in e:
                    n = ipaddress.ip_network(e, strict=False)
                else:
                    # Single IP -> treat as /32 or /128
                    ip = ipaddress.ip_address(e)
                    if ip.version == 4:
                        n = ipaddress.IPv4Network(f"{e}/32")
                    else:
                        n = ipaddress.IPv6Network(f"{e}/128")
                nets.append(n)
            except ValueError:
                # Ignore invalid entries; validation occurs at startup
                continue
        return nets

    def _ip_in_nets(self, ip_str: str, nets: List[ipaddress._BaseNetwork]) -> bool:
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            return False
        for n in nets:
            if ip in n:
                return True
        return False

    def is_allowed(self, request: Request) -> Tuple[bool, str]:
        """Decide whether the incoming request is allowed.

        Returns (allowed: bool, reason: str)
        """
        remote = request.remote_addr or ''

        # No configured proxies -> use remote_addr
        if not self.allowed_proxies:
            # If allowed_ips empty -> allow all
            if not self.allowed_ips:
                return True, 'no proxies configured and no allowed_ips -> allow all'
            # Otherwise check remote against allowed_ips
            if self._ip_in_nets(remote, self.allowed_ips):
                return True, 'remote addr in allowed_ips'
            logger.warning(f"ACL deny: remote address {remote} not in allowed_ips")
            return False, 'remote addr not in allowed_ips'

        # Proxies configured: requests should come from a trusted proxy
        # If remote is not a configured proxy, deny
        if not self._ip_in_nets(remote, self.allowed_proxies):
            logger.warning(f"ACL deny: request from {remote} is not a trusted proxy")
            return False, 'request did not come from trusted proxy'

        # remote is a trusted proxy. Extract client IP from headers
        xff = request.headers.get('X-Forwarded-For', '')
        client_ip = ''
        if xff:
            # first value is the original client
            client_ip = xff.split(',')[0].strip()

        # If no allowed_ips configured and proxies present -> deny by default
        if not self.allowed_ips:
            return True, 'Trusted proxy -> No allowed_ips configured -> allow all'
        elif client_ip and self._ip_in_nets(client_ip, self.allowed_ips): 
              return True, 'client ip from header in allowed_ips'

        logger.warning(f"ACL deny: client ip {client_ip or '<none>'} not allowed (remote proxy={remote})")
        return False, 'client ip not allowed'
