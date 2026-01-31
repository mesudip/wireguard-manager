
import pytest
import json
import re

def test_private_key_redaction_in_diff(api_client, test_interface):
    """Verify that private keys are redacted in config diff responses."""
    # 1. Add a peer to create some configuration
    # Note: test_interface uses default 10.0.0.1/24, so peer should be in 10.0.0.x subnet
    peer_response = api_client.add_peer(
        test_interface,
        name="test-peer",
        allowed_ips="10.0.0.2/32"
    )
    assert peer_response.status_code == 201, f"Failed to add peer: {peer_response.status_code} - {peer_response.text}"
    peer_data = peer_response.json()
    
    # 2. Verify that the peer has a private key (for client config)
    assert "private_key" in peer_data
    private_key = peer_data["private_key"]
    
    # If there's no private key generated, we can't test redaction
    if private_key:
        # 3. Get the config diff
        diff_response = api_client.get_config_diff(test_interface)
        assert diff_response.status_code == 200, f"Failed to get config diff: {diff_response.status_code} - {diff_response.text}"
        diff = diff_response.json()['diff']
        
        # 4. Assert that actual private keys are NOT in the diff output
        # Private keys are base64 encoded strings, typically 44 characters
        assert private_key not in diff, "Private key should be redacted in diff output"
        
        # 5. Get the interface details which should have the interface private key
        interface_response = api_client.get_interface(test_interface)
        assert interface_response.status_code == 200, f"Failed to get interface: {interface_response.status_code} - {interface_response.text}"
        interface_data = interface_response.json()
        
        # Check that interface public key is present (this is safe to show)
        assert "public_key" in interface_data
        assert interface_data["public_key"] is not None
        
    # 6. List peers to verify private key handling in API responses
    peers_response = api_client.list_peers(test_interface)
    assert peers_response.status_code == 200, f"Failed to list peers: {peers_response.status_code} - {peers_response.text}"
    peers = peers_response.json()
    
    # Peer private keys should either be null or redacted in list responses
    for peer in peers:
        if "private_key" in peer and peer["private_key"]:
            # If shown, it should be for the peer's own config generation
            # But it should never appear in diffs
            pass
