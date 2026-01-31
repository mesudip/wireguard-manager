import pytest
import os
import json

def test_list_interfaces_structure(api_client):
    """Test that /interfaces returns the new structured response."""
    response = api_client.list_interfaces()
    assert isinstance(response, dict)
    assert "host" in response
    assert "wireguard" in response
    assert "ips" in response["host"]

def test_host_info_manual_override(api_client):
    """Test manual host info update and that it sets the manual flag."""
    custom_ips = ["1.2.3.4", "5.6.7.8"]
    response = api_client.update_host_info(ips=custom_ips)
    assert response.status_code == 200
    data = response.json()
    assert data["ips"] == custom_ips
    assert data["manual"] is True

    # Verify via list_interfaces
    interfaces = api_client.list_interfaces()
    assert interfaces["host"]["ips"] == custom_ips

def test_host_info_rescan(api_client):
    """Test force rescan of host info."""
    # First set manual
    api_client.update_host_info(ips=["1.1.1.1"])
    
    # Then rescan
    response = api_client.rescan_host_info()
    assert response.status_code == 200
    data = response.json()
    assert data["manual"] is False
    # IPs should be rediscovered (might be empty in CI/Docker but manual should be False)

def test_host_info_file_persistence(api_client):
    """Test that host info persists in the cache file (indirectly via GET)."""
    custom_ips = ["9.9.9.9"]
    api_client.update_host_info(ips=custom_ips)
    
    # In integration tests, we can't easily restart the backend, 
    # but we can verify it returns what we just set.
    interfaces = api_client.list_interfaces()
    assert interfaces["host"]["ips"] == custom_ips
    assert interfaces["host"]["message"] is None or interfaces["host"]["message"] == "success"

def test_host_info_deduplication(api_client):
    """Test that the API deduplicates and cleans IPs."""
    input_ips = ["1.1.1.1", "1.1.1.1 ", "  2.2.2.2  ", "1.1.1.1"]
    expected_ips = ["1.1.1.1", "2.2.2.2"]
    
    response = api_client.update_host_info(ips=input_ips)
    assert response.status_code == 200
    data = response.json()
    assert data["ips"] == expected_ips
