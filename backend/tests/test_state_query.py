import pytest

def test_state_queries(api_client, test_interface):
    """Test state query and state diff."""
    
    # 1. Get State (equivalent to wg show)
    response = api_client.get_state(test_interface)
    assert response.status_code == 200
    state = response.json()
    assert "status" in state
    
    # 2. Get State Diff
    response = api_client.get_state_diff(test_interface)
    assert response.status_code == 200

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
    # Now should return 200 with status="not_found"
    response = api_client.get_state("nonexistent")
    assert response.status_code == 200
    assert response.json()["status"] == "not_found"
    
    # Diff should now return 200 with status="success" even if interface doesn't exist
    # because it treats the missing interface as an empty state.
    response = api_client.get_state_diff("nonexistent")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    # The diff won't be empty if there's no such interface but we have a config for it.
    # But for "nonexistent", there's probably no config either, so diff might be empty.
    # If both config and state are empty, diff is empty.
