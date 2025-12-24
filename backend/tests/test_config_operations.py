import pytest
import uuid
import time

def test_config_apply_diff_reset(api_client, test_interface):
    """Test the flow of apply, diff, and reset for configuration."""
    
    # 1. Initially, diff might show some default stuff or be empty if just created
    # Let's add a peer to ensure there's a difference between folder and .conf file
    peer_name = f"peer_{uuid.uuid4().hex[:4]}"
    add_resp = api_client.add_peer(test_interface, name=peer_name)
    public_key = add_resp.json()['public_key']
    
    response = api_client.get_config_diff(test_interface)
    assert response.status_code == 200
    diff = response.json()['diff']
    assert len(diff) > 0
    assert public_key in diff

    # 2. Sync config (generate file)
    response = api_client.sync_config(test_interface)
    assert response.status_code == 200
    assert "Config synchronized successfully" in response.json()['message']
    
    # 3. Check diff again (should be empty now)
    response = api_client.get_config_diff(test_interface)
    assert response.status_code == 200
    assert response.json()['diff'] == ''

    # 4. Reset config
    # To test reset, we should simulate a dirty state in the folder that needs to be reverted.
    # Since we can't easily touch the container filesystem directly from here without exec,
    # let's try to add another peer, then reset. 
    # WAIT: the reset_config implementation (as per docstring) generates the FOLDER from the CONF file.
    # So if we add a peer (which adds a file to the folder), and then reset, that peer file should be deleted.
    
    new_peer = "peer_to_be_reset"
    add_resp = api_client.add_peer(test_interface, name=new_peer)
    new_public_key = add_resp.json()['public_key']
    
    # Verify it exists in folder (diff shows it)
    diff = api_client.get_config_diff(test_interface).json()['diff']
    assert new_public_key in diff
    
    # Reset
    response = api_client.reset_config(test_interface)
    assert response.status_code == 200
    
    # Verify it's gone from folder and folder matches config exactly
    diff = api_client.get_config_diff(test_interface).json()['diff']
    assert diff == ''

def test_config_operations_non_existent_interface(api_client):
    interface = "nonexistent"
    assert api_client.sync_config(interface).status_code == 404
    assert api_client.apply_config(interface).status_code == 404
    assert api_client.reset_config(interface).status_code == 404
    assert api_client.get_config_diff(interface).status_code == 404
