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
    # Check that keys were generated (default behavior)
    assert 'public_key' in data
    assert 'private_key' in data
    assert data['private_key'] is not None

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


def test_add_peer_with_public_key(api_client, test_interface):
    """Test adding a peer with a provided public key."""
    peer_name = f"peer_{uuid.uuid4().hex[:4]}"
    public_key = "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZU="
    allowed_ips = "10.0.0.2/32"
    
    response = api_client.add_peer(test_interface, name=peer_name, allowed_ips=allowed_ips, public_key=public_key)
    assert response.status_code == 201
    data = response.json()
    assert data['public_key'] == public_key
    assert data.get('private_key') is None

    # Verify Get shows the correct public key
    response = api_client.get_peer(test_interface, peer_name)
    assert response.status_code == 200
    assert response.json()['public_key'] == public_key

def test_add_peer_automatic_ip(api_client):
    """Test adding a peer with automatic IP detection from a partial subnet."""
    import uuid
    if_name = f"wg{uuid.uuid4().hex[:4]}"
    # Create interface with 10.50.0.1/16
    api_client.create_interface(name=if_name, address="10.50.0.1/16")
    
    try:
        # Request 10.50.10 subnet (partial)
        peer_name_1 = "auto-peer-1"
        response = api_client.add_peer(if_name, name=peer_name_1, allowed_ips="10.50.10")
        assert response.status_code == 201
        data = response.json()
        assert data['allowed_ips'] == "10.50.10.1/32"
        
        # Peer with full network address ending in .0
        peer_name_1_ext = "auto-peer-1-ext"
        response = api_client.add_peer(if_name, name=peer_name_1_ext, allowed_ips="10.50.20.0")
        assert response.status_code == 201
        data = response.json()
        assert data['allowed_ips'] == "10.50.20.1/32"
        
        # Second peer in same partial subnet
        peer_name_2 = "auto-peer-2"
        response = api_client.add_peer(if_name, name=peer_name_2, allowed_ips="10.50.10")
        assert response.status_code == 201
        data = response.json()
        assert data['allowed_ips'] == "10.50.10.2/32"
        
        # Peer in different subnetwork of same interface
        peer_name_3 = "auto-peer-3"
        response = api_client.add_peer(if_name, name=peer_name_3, allowed_ips="10.50")
        assert response.status_code == 201
        data = response.json()
        # 10.50.0.1 is taken by interface, so next is 10.50.0.2
        assert data['allowed_ips'] == "10.50.0.2/32"

        # Peer with .0 shorthand for interface network
        peer_name_4 = "auto-peer-4"
        response = api_client.add_peer(if_name, name=peer_name_4, allowed_ips="10.50.0.0")
        assert response.status_code == 201
        data = response.json()
        # 10.50.0.1 is interface, 10.50.0.2 is peer-3, so next is 10.50.0.3
        assert data['allowed_ips'] == "10.50.0.3/32"
    finally:
        api_client.delete_interface(if_name)

def test_add_peer_invalid_subnet(api_client, test_interface):
    """Test adding a peer with a subnet that is not a subset of the interface network."""
    # test_interface usually has 10.0.0.1/24 (default)
    response = api_client.add_peer(test_interface, name="invalid-subnet-peer", allowed_ips="10.10")
    assert response.status_code == 400
    assert "not a subset" in response.json()["error"]

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
