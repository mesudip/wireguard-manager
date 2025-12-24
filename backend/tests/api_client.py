import requests
from typing import Dict, Any, Optional

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def get_health(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()

    def list_interfaces(self) -> list:
        response = requests.get(f"{self.base_url}/api/interfaces")
        response.raise_for_status()
        return response.json()

    def create_interface(self, name: str, address: str = '10.0.0.1/24', listen_port: str = '51820') -> Dict[str, Any]:
        data = {
            "name": name,
            "address": address,
            "listen_port": listen_port
        }
        response = requests.post(f"{self.base_url}/api/interfaces", json=data)
        if response.status_code != 201:
             # Allow tests to handle error status codes if needed, or raise for unexpected ones
             # But for helper usage, we usually want to know if it failed. 
             # Let's return the response object or raise_for_status. 
             # To make it easier for positive tests, we raise. For negative tests, we might need a different method or catch exception.
             # Actually, for flexibility, let's return the response object in a lower level method, or just raise_for_status here
             # and catch in tests. But to test error cases, we need the response content.
             # Lets change the pattern: return response object for all checks.
             pass
        return response

    def get_interface(self, name: str) -> requests.Response:
        return requests.get(f"{self.base_url}/api/interfaces/{name}")

    def update_interface(self, name: str, address: Optional[str] = None, listen_port: Optional[str] = None) -> requests.Response:
        data = {}
        if address:
            data['address'] = address
        if listen_port:
            data['listen_port'] = listen_port
        return requests.put(f"{self.base_url}/api/interfaces/{name}", json=data)

    def delete_interface(self, name: str) -> requests.Response:
        return requests.delete(f"{self.base_url}/api/interfaces/{name}")

    # Peer Management
    def list_peers(self, interface: str) -> requests.Response:
        return requests.get(f"{self.base_url}/api/interfaces/{interface}/peers")

    def add_peer(self, interface: str, name: str, allowed_ips: str = '10.0.0.2/32', endpoint: str = '') -> requests.Response:
        data = {
            "name": name,
            "allowed_ips": allowed_ips,
            "endpoint": endpoint
        }
        return requests.post(f"{self.base_url}/api/interfaces/{interface}/peers", json=data)

    def get_peer(self, interface: str, peer_name: str) -> requests.Response:
        return requests.get(f"{self.base_url}/api/interfaces/{interface}/peers/{peer_name}")

    def update_peer(self, interface: str, peer_name: str, allowed_ips: Optional[str] = None, endpoint: Optional[str] = None) -> requests.Response:
        data = {}
        if allowed_ips:
            data['allowed_ips'] = allowed_ips
        if endpoint:
            data['endpoint'] = endpoint
        return requests.put(f"{self.base_url}/api/interfaces/{interface}/peers/{peer_name}", json=data)

    def delete_peer(self, interface: str, peer_name: str) -> requests.Response:
        return requests.delete(f"{self.base_url}/api/interfaces/{interface}/peers/{peer_name}")

    # Config Management
    def sync_config(self, interface: str) -> requests.Response:
        return requests.post(f"{self.base_url}/api/interfaces/{interface}/config/sync")

    def apply_config(self, interface: str) -> requests.Response:
        return requests.post(f"{self.base_url}/api/interfaces/{interface}/config/apply")

    def reset_config(self, interface: str) -> requests.Response:
        return requests.post(f"{self.base_url}/api/interfaces/{interface}/config/reset")

    def get_config_diff(self, interface: str) -> requests.Response:
        return requests.get(f"{self.base_url}/api/interfaces/{interface}/config/diff")

    # State Management
    def get_state(self, interface: str) -> requests.Response:
        return requests.get(f"{self.base_url}/api/interfaces/{interface}/state")

    def get_state_diff(self, interface: str) -> requests.Response:
        return requests.get(f"{self.base_url}/api/interfaces/{interface}/state/diff")
