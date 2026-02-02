import pytest
import sys
import os
from unittest.mock import Mock

# Add backend to path to allow imports of services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.access_control import AccessControl

class TestAccessControl:
    
    def test_compile_nets(self):
        """Test that networks are correctly compiled from strings."""
        acl = AccessControl([], ['10.0.0.1', '192.168.1.0/24', '2001:db8::1'])
        
        str_nets = [str(n) for n in acl.allowed_ips]
        assert '10.0.0.1/32' in str_nets
        assert '192.168.1.0/24' in str_nets
        assert '2001:db8::1/128' in str_nets

    def test_ip_in_nets_ipv4_direct(self):
        """Test standard IPv4 matching."""
        acl = AccessControl([], ['10.0.0.0/24'])
        assert acl._ip_in_nets('10.0.0.50', acl.allowed_ips) is True
        assert acl._ip_in_nets('10.0.1.50', acl.allowed_ips) is False

    def test_ip_in_nets_ipv6_direct(self):
        """Test standard IPv6 matching."""
        acl = AccessControl([], ['2001:db8::/64'])
        assert acl._ip_in_nets('2001:db8::1', acl.allowed_ips) is True
        assert acl._ip_in_nets('2001:db8:1::1', acl.allowed_ips) is False

    def test_ip_in_nets_ipv4_mapped_ipv6(self):
        """Test that IPv4-mapped IPv6 addresses match against IPv4 allowed list.
        
        This tests the fix for supporting tunnels/proxies passing IPv6 mapped addresses.
        """
        acl = AccessControl([], ['10.0.0.0/24'])
        
        # ::ffff:10.0.0.1 maps to 10.0.0.1 which is in 10.0.0.0/24
        assert acl._ip_in_nets('::ffff:10.0.0.1', acl.allowed_ips) is True
        
        # ::ffff:10.0.1.1 maps to 10.0.1.1 which is NOT in 10.0.0.0/24
        assert acl._ip_in_nets('::ffff:10.0.1.1', acl.allowed_ips) is False

    def test_is_allowed_no_proxies(self):
        """Test is_allowed logic when no proxies are configured."""
        acl = AccessControl([], ['10.0.0.0/24'])
        
        # Allowed IP
        req = Mock()
        req.remote_addr = '10.0.0.1'
        req.headers = {}
        allowed, reason = acl.is_allowed(req)
        assert allowed is True
        assert 'remote addr in allowed_ips' in reason

        # Disallowed IP
        req.remote_addr = '192.168.1.1'
        allowed, reason = acl.is_allowed(req)
        assert allowed is False
        assert 'remote addr not in allowed_ips' in reason
        
        # IPv4-mapped allowed IP
        req.remote_addr = '::ffff:10.0.0.1'
        allowed, reason = acl.is_allowed(req)
        assert allowed is True

    def test_is_allowed_with_proxies(self):
        """Test is_allowed logic when proxies are configured."""
        # Proxy at 10.0.0.1, Allowed Clients in 192.168.1.0/24
        acl = AccessControl(['10.0.0.1'], ['192.168.1.0/24'])

        # Request from untrusted source
        req = Mock()
        req.remote_addr = '1.2.3.4' # Not the proxy
        allowed, reason = acl.is_allowed(req)
        assert allowed is False
        assert 'did not come from trusted proxy' in reason

        # Request from trusted proxy, valid client
        req.remote_addr = '10.0.0.1'
        req.headers = {'X-Forwarded-For': '192.168.1.50'}
        allowed, reason = acl.is_allowed(req)
        assert allowed is True
        assert 'client ip from header' in reason

        # Request from trusted proxy, invalid client
        req.remote_addr = '10.0.0.1'
        req.headers = {'X-Forwarded-For': '172.16.0.1'}
        allowed, reason = acl.is_allowed(req)
        assert allowed is False
        assert 'client ip not allowed' in reason

    def test_is_allowed_empty_config(self):
        """Test default allow all behavior."""
        # No allowed_ips -> allow all
        acl = AccessControl([], [])
        req = Mock()
        req.remote_addr = '1.2.3.4'
        allowed, reason = acl.is_allowed(req)
        assert allowed is True
