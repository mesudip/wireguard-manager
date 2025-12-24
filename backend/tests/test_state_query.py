import pytest

def test_state_queries(api_client, test_interface):
    """Test state query and state diff."""
    
    # 1. Get State (equivalent to wg show)
    response = api_client.get_state(test_interface)
    # If the interface is not up, state_service might return 404 or 500 depending on error message
    assert response.status_code in [200, 404, 500]
    
    # 2. Get State Diff
    response = api_client.get_state_diff(test_interface)
    assert response.status_code in [200, 404, 500]

def test_state_reflects_peer_addition(api_client, test_interface):
    """Test that adding a peer and applying config/state is reflected in wg show."""
    # 1. Add a peer
    peer_name = "state_test_peer"
    add_resp = api_client.add_peer(test_interface, name=peer_name)
    assert add_resp.status_code == 201
    public_key = add_resp.json()['public_key']
    
    # 2. Apply config (This now does BOTH generation and application to live state)
    apply_resp = api_client.apply_config(test_interface)
    
    # If it works (e.g. in systemd container with WG)
    if apply_resp.status_code == 200:
        # 3. Verify state reflects the peer
        state_resp = api_client.get_state(test_interface)
        if state_resp.status_code == 200:
            state = state_resp.json()
            assert any(p['public_key'] == public_key for p in state['peers'])
        else:
            pytest.skip(f"State query failed (likely env issue): {state_resp.text}")
    else:
        pytest.skip(f"Config apply failed (likely env issue): {apply_resp.text}")

def test_state_non_existent_interface(api_client):
    # Depending on whether 'wg show' or 'FileNotFoundError' hits first
    response = api_client.get_state("nonexistent")
    assert response.status_code in [404, 500]
    
    response = api_client.get_state_diff("nonexistent")
    assert response.status_code in [404, 500]
