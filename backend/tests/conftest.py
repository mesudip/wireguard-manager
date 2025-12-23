import pytest
import docker
import time
import requests
import os
import uuid
from urllib.parse import urlparse
from api_client import APIClient

# Configuration
IMAGE_NAME_STANDARD = "wireguard-backend-standard"
IMAGE_NAME_SYSTEMD = "wireguard-backend-systemd"

def get_docker_host():
    docker_host_env = os.environ.get('DOCKER_HOST')
    if not docker_host_env:
        return 'localhost'
    
    parsed = urlparse(docker_host_env)
    if parsed.scheme == 'unix':
        return 'localhost'
    elif parsed.scheme in ['tcp', 'http', 'https']:
        return parsed.hostname
    return 'localhost'

@pytest.fixture(scope="session")
def docker_client():
    return docker.from_env()

@pytest.fixture(scope="session", params=["standard", "systemd"])
def docker_stack(request, docker_client):
    mode = request.param
    image_tag = IMAGE_NAME_STANDARD if mode == "standard" else IMAGE_NAME_SYSTEMD
    dockerfile = "Dockerfile" if mode == "standard" else "tests/Dockerfile.systemd"
    
    # Build image
    print(f"\nBuilding {mode} Docker image {image_tag}...")
    image, logs = docker_client.images.build(
        path=os.path.join(os.path.dirname(__file__), ".."),
        dockerfile=dockerfile,
        tag=image_tag,
        rm=True
    )
    for log in logs:
        if 'stream' in log:
            print(log['stream'].strip())

    # Run container
    container_name = f"wg-test-{mode}-{uuid.uuid4().hex[:8]}"
    print(f"Starting {mode} container {container_name}...")
    
    kwargs = {
        "detach": True,
        "name": container_name,
        "ports": {'5000/tcp': None},
        "privileged": True
    }
    
    if mode == "systemd":
        # Required for systemd in docker
        # On GHA (Cgroup v2), host cgroupns and specific volumes are often needed
        kwargs["volumes"] = {
            '/sys/fs/cgroup': {'bind': '/sys/fs/cgroup', 'mode': 'rw'} # Revert to rw for now
        }
        kwargs["tmpfs"] = {'/run': '', '/run/lock': ''}
        
        # Only add cgroupns_mode if supported by the library
        # Instead of version checking, we'll try-catch the run call later
        kwargs["cgroupns_mode"] = "host"
    
    try:
        container = docker_client.containers.run(image_tag, **kwargs)
    except TypeError as e:
        if 'cgroupns_mode' in str(e) and mode == "systemd":
            del kwargs['cgroupns_mode']
            container = docker_client.containers.run(image_tag, **kwargs)
        else:
            raise

    # Reload to get port mapping info
    container.reload()
    ports = container.attrs['NetworkSettings']['Ports']
    host_port = ports['5000/tcp'][0]['HostPort']
    
    host = get_docker_host()
    base_url = f"http://{host}:{host_port}"
    print(f"API available at {base_url} ({mode} mode)")

    # Wait for health check
    print("Waiting for API to be ready...")
    start_time = time.time()
    ready = False
    timeout = 90 if mode == "systemd" else 30 # systemd takes longer to boot
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print("API is ready!")
                ready = True
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(2)
    
    if not ready:
        print(f"Timeout waiting for {mode} API.")
        
        if mode == "systemd":
            print("\nSystemd Status Check:")
            try:
                # Check if systemd is even running
                ps = container.exec_run("ps aux")
                print("Process List:")
                print(ps.output.decode('utf-8'))
                
                # Check service status
                status = container.exec_run("systemctl status wireguard-manager")
                print("\nService Status:")
                print(status.output.decode('utf-8'))
                
                # Check journal
                print("\nJournalctl logs (systemd):")
                journals = container.exec_run("journalctl -u wireguard-manager -n 100")
                print(journals.output.decode('utf-8'))
            except Exception as e:
                print(f"Failed to get diagnostics: {e}")
        else:
            print("Container logs:")
            print(container.logs().decode('utf-8'))
                
        container.remove(force=True)
        pytest.fail(f"API ({mode}) did not become ready in time.")

    yield base_url

    # Teardown
    print(f"\nStopping container {container_name}...")
    container.remove(force=True)

@pytest.fixture(scope="session")
def api_client(docker_stack):
    return APIClient(docker_stack)

@pytest.fixture
def test_interface(api_client):
    """Fixture to create and clean up an interface for tests."""
    name = f"wg{uuid.uuid4().hex[:4]}"
    response = api_client.create_interface(name=name)
    assert response.status_code == 201
    
    yield name
    
    # Cleanup
    api_client.delete_interface(name)
