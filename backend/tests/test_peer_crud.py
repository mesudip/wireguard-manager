import pytest
import uuid

def test_peer_lifecycle(api_client, test_interface):
    """Test full lifecycle of a peer: Create -> Get -> Update -> Delete"""
    peer_name = f"peer_{uuid.uuid4().hex[:4]}"
    allowed_ips = "10.0.0.2/32"
    
    # 1. Add Peer
    response = api_client.add_peer(test_interface, name=peer_name, allowed_ips=allowed_ips)
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == peer_name
    assert data['allowed_ips'] == allowed_ips

    # 2. Get Peer
    response = api_client.get_peer(test_interface, peer_name)
    assert response.status_code == 200
    assert response.json()['name'] == peer_name
    assert response.json()['allowed_ips'] == allowed_ips
    
    # 3. List Peers
    response = api_client.list_peers(test_interface)
    assert response.status_code == 200
    peers = response.json()
    assert any(p['name'] == peer_name for p in peers)

    # 4. Update Peer
    new_allowed_ips = "10.0.0.3/32"
    response = api_client.update_peer(test_interface, peer_name, allowed_ips=new_allowed_ips)
    assert response.status_code == 200
    
    response = api_client.get_peer(test_interface, peer_name)
    assert response.json()['allowed_ips'] == new_allowed_ips

    # 5. Delete Peer
    response = api_client.delete_peer(test_interface, peer_name)
    assert response.status_code == 200
    
    response = api_client.get_peer(test_interface, peer_name)
    assert response.status_code == 404

def test_add_peer_invalid_interface(api_client):
    response = api_client.add_peer("nonexistent_if", name="test_peer")
    assert response.status_code == 404

def test_add_peer_missing_name(api_client, test_interface):
    # Testing missing name. The APIClient.add_peer requires name, so we'll use a raw request if needed
    # but based on route definition, it checks for peer_name in json.
    import requests
    response = requests.post(f"{api_client.base_url}/api/interfaces/{test_interface}/peers", json={})
    assert response.status_code == 400
    assert "Peer name is required" in response.json()['error']

def test_get_non_existent_peer(api_client, test_interface):
    response = api_client.get_peer(test_interface, "nonexistent_peer")
    assert response.status_code == 404

def test_delete_non_existent_peer(api_client, test_interface):
    response = api_client.delete_peer(test_interface, "nonexistent_peer")
    assert response.status_code == 404
