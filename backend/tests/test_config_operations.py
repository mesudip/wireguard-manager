import pytest
import uuid
import time

def test_config_apply_diff_reset(api_client, test_interface):
    """Test the flow of apply, diff, and reset for configuration."""
    
    # 1. Initially, diff might show some default stuff or be empty if just created
    # Since operations are now auto-synced, diff should be empty after adding a peer
    peer_name = f"peer_{uuid.uuid4().hex[:4]}"
    add_resp = api_client.add_peer(test_interface, name=peer_name)
    public_key = add_resp.json()['public_key']
    
    response = api_client.get_config_diff(test_interface)
    assert response.status_code == 200
    diff = response.json()['diff']
    # Diff should be empty because add_peer auto-syncs the folder to the conf file
    assert diff == ''

    # 2. Sync config (generate file) - should still return success but do nothing new
    response = api_client.sync_config(test_interface)
    assert response.status_code == 200
    assert "Config synchronized successfully" in response.json()['message']
    
    # 3. Check diff again (still empty)
    response = api_client.get_config_diff(test_interface)
    assert response.status_code == 200
    assert response.json()['diff'] == ''

    # 4. Reset config
    # Since we are auto-synced, reset won't have much to do through the API,
    # but we can verify it returns success and maintains the sync.
    response = api_client.reset_config(test_interface)
    assert response.status_code == 200
    
    diff = api_client.get_config_diff(test_interface).json()['diff']
    assert diff == ''

def test_config_operations_non_existent_interface(api_client):
    interface = "nonexistent"
    assert api_client.sync_config(interface).status_code == 404
    assert api_client.apply_config(interface).status_code == 404
    assert api_client.reset_config(interface).status_code == 404
    assert api_client.get_config_diff(interface).status_code == 404
