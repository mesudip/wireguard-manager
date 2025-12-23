import pytest
import uuid

def test_interface_lifecycle(api_client):
    """Test full lifecycle of an interface: Create -> Get -> Update -> Delete"""
    interface_name = f"wg{uuid.uuid4().hex[:4]}"
    
    # 1. Create
    response = api_client.create_interface(name=interface_name, address="10.10.10.1/24", listen_port="51821")
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == interface_name
    assert data['address'] == "10.10.10.1/24"
    assert data['listen_port'] == "51821"

    # 2. Get
    response = api_client.get_interface(interface_name)
    assert response.status_code == 200
    assert response.json()['name'] == interface_name
    
    # 3. List
    assert interface_name in api_client.list_interfaces()

    # 4. Update
    api_client.update_interface(interface_name, address="10.10.10.2/24")
    data = api_client.get_interface(interface_name).json()
    assert data['address'] == "10.10.10.2/24"

    # 5. Delete
    assert api_client.delete_interface(interface_name).status_code == 200
    assert api_client.get_interface(interface_name).status_code == 404

def test_create_duplicate_interface(api_client, test_interface):
    # test_interface fixture already created an interface with a random name
    response = api_client.create_interface(name=test_interface)
    assert response.status_code == 400

@pytest.mark.parametrize("invalid_name", [
    "",              # Empty
    " ",             # Space
    "wg test",       # Space in middle
    "verylonginterfacename", # > 15 chars
    "!@#$%^&*()",    # Special chars
    "1startingdigit",# Starting with digit (some systems allow, but often discouraged/restricted)
    "-startwithdash",
    ".hidden",
])
def test_create_invalid_name(api_client, invalid_name):
    response = api_client.create_interface(name=invalid_name)
    assert response.status_code == 400

def test_delete_non_existent_interface(api_client):
    assert api_client.delete_interface("nonexistent").status_code == 404

def test_update_non_existent_interface(api_client):
    response = api_client.update_interface("nonexistent", address="10.0.0.1/24")
    assert response.status_code == 404

@pytest.mark.parametrize("field, invalid_value", [
    ("address", "not-an-ip"),
    ("address", "256.256.256.256/24"),
    ("address", "10.0.0.1/33"),
    ("listen_port", "not-a-port"),
    ("listen_port", "0"),
    ("listen_port", "65536"),
    ("listen_port", "-1"),
])
def test_update_invalid_fields(api_client, test_interface, field, invalid_value):
    kwargs = {field: invalid_value}
    response = api_client.update_interface(test_interface, **kwargs)
    assert response.status_code == 400

def test_create_invalid_fields(api_client):
    # Invalid address
    response = api_client.create_interface(name="wgvalid", address="invalid")
    assert response.status_code == 400
    
    # Invalid port
    response = api_client.create_interface(name="wgvalid2", listen_port="99999")
    assert response.status_code == 400
