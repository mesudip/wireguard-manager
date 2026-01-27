import pytest
import docker
import time
import requests
import os
import uuid
import subprocess
import sys
from urllib.parse import urlparse
from api_client import APIClient

# Configuration
IMAGE_NAME_STANDARD = "wireguard-backend-standard"
IMAGE_NAME_SYSTEMD = "wireguard-backend-systemd"

def pytest_addoption(parser):
    parser.addoption("--host", action="store_true", help="Run tests against host backend")

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

@pytest.fixture(scope="session")
def docker_stack(request, docker_client):
    mode = request.param
    base_url = "http://localhost:5000"
    
    if mode == "host-systemd":
        print(f"\nRunning in HOST SYSTEMD mode.")
        backend_dir = os.path.join(os.path.dirname(__file__), "..")
        install_script = os.path.join(backend_dir, "install.sh")
        
        print(f"Running installation script: {install_script}")
        try:
            subprocess.run(["bash", "-e", install_script], check=True, cwd=backend_dir)
            print("Installation complete. Restarting service...")
            subprocess.run([ "systemctl", "restart", "wireguard-manager"], check=True)
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to setup host systemd: {e}")
        
        try:
            wait_for_ready(base_url, mode)
            yield base_url
        finally:
            print("Stopping host systemd service...")
            subprocess.run([ "systemctl", "stop", "wireguard-manager"], check=True)
        return

    if mode == "host-standard":
        print(f"\nRunning in HOST STANDARD mode.")
        # Ensure systemd service is stopped to avoid port conflict
        subprocess.run([ "systemctl", "stop", "wireguard-manager"], check=False)
        
        backend_dir = os.path.join(os.path.dirname(__file__), "..")
        app_path = os.path.join(backend_dir, "app.py")
        python_exe = sys.executable
        
        print(f"Starting backend: {python_exe} {app_path}")
        process = subprocess.Popen([ python_exe, app_path], cwd=backend_dir)
        
        try:
            wait_for_ready(base_url, mode)
            yield base_url
        finally:
            print(f"Stopping host-standard backend (PID: {process.pid})...")
            subprocess.run([ "kill", str(process.pid)])
            process.wait()
        return

    # Docker modes
    image_tag = f"{IMAGE_NAME_STANDARD}:latest" if mode == "standard" else f"{IMAGE_NAME_SYSTEMD}:latest"
    dockerfile = "Dockerfile" if mode == "standard" else "tests/Dockerfile.systemd"
    
    in_ci = os.environ.get("GITHUB_ACTIONS", "false").lower() == "true"
    force_build = os.environ.get("WG_TEST_FORCE_BUILD", "false").lower() == "true"
    
    image_exists = False
    if in_ci and not force_build:
        try:
            docker_client.images.get(image_tag)
            print(f"\nUsing pre-existing Docker image {image_tag}")
            image_exists = True
        except docker.errors.ImageNotFound:
            pass

    if not image_exists:
        print(f"\nBuilding {mode} Docker image {image_tag}...")
        image, logs = docker_client.images.build(
            path=os.path.join(os.path.dirname(__file__), ".."),
            dockerfile=dockerfile,
            tag=image_tag,
            nocache=False,
            rm=True
        )
        for log in logs:
            if 'stream' in log:
                print(log['stream'].strip())

    container_name = f"wg-test-{mode}-{uuid.uuid4().hex[:8]}"
    print(f"Starting {mode} container {container_name}...")
    
    env = {}
    if mode == "standard":
        env = {
            "WG_WIREGUARD_USE_SYSTEMD": "false",
            "WG_WIREGUARD_USE_SUDO": "false",
            "WG_WIREGUARD_BASE_DIR": "/etc/wireguard"
        }
    
    kwargs = {
        "detach": True,
        "name": container_name,
        "ports": {'5000/tcp': None},
        "cap_add": ["NET_ADMIN", "SYS_MODULE"],
        "environment": env
    }
    
    if mode == "systemd":
        kwargs["privileged"] = True
        # systemd requires SYS_ADMIN and specific mounts
        if "SYS_ADMIN" not in kwargs["cap_add"]:
            kwargs["cap_add"].append("SYS_ADMIN")
        
        kwargs["volumes"] = {
            '/sys/fs/cgroup': {'bind': '/sys/fs/cgroup', 'mode': 'rw'},
            '/lib/modules': {'bind': '/lib/modules', 'mode': 'ro'}
        }
        kwargs["tmpfs"] = {'/run': '', '/run/lock': '', '/tmp': '', '/run/wireguard': ''}
    
    try:
        container = docker_client.containers.run(image_tag, **kwargs)
    except TypeError as e:
        # Fallback for older docker-py that doesn't support some newer flags
        print(f"Docker run TypeError: {e}. Retrying without redundant flags...")
        container = docker_client.containers.run(image_tag, detach=True, name=container_name, ports={'5000/tcp': None}, privileged=True)
    except Exception as e:
        pytest.fail(f"Failed to start {mode} container: {e}")

    # Give it a second to stabilize and get network settings
    time.sleep(3)
    container.reload()
    
    # 5. Get assigned port
    ports = container.attrs['NetworkSettings']['Ports']
    if not ports or '5000/tcp' not in ports or not ports['5000/tcp']:
        # Fallback/Retry reload if ports are missing (sometimes happens in slow CI)
        time.sleep(2)
        container.reload()
        ports = container.attrs['NetworkSettings']['Ports']
        
    if not ports or '5000/tcp' not in ports or not ports['5000/tcp']:
        state = container.attrs.get('State', {})
        status = state.get('Status', 'unknown')
        exit_code = state.get('ExitCode', 'N/A')
        error = state.get('Error', 'N/A')
        
        try:
            # Explicitly fetch both stdout and stderr
            logs_raw = container.logs(stdout=True, stderr=True, tail=300)
            logs = logs_raw.decode('utf-8', errors='replace')
        except Exception as e:
            logs = f"Failed to fetch logs: {e}"
            
        container_info = (
            f"\n--- CONTAINER FAILURE INFO ---\n"
            f"Container: {container_name} ({mode})\n"
            f"Status: {status}\n"
            f"ExitCode: {exit_code}\n"
            f"Error: {error}\n"
            f"--- CONTAINER LOGS (STDOUT+STDERR) ---\n"
            f"{logs}\n"
            f"---------------------------\n"
        )
        print(container_info)
        container.remove(force=True)
        pytest.fail(f"Could not get host port for {mode} container. See logs above.")

    host_port = ports['5000/tcp'][0]['HostPort']
    host = get_docker_host()
    base_url = f"http://{host}:{host_port}"
    
    try:
        wait_for_ready(base_url, mode, container)
        yield base_url
    finally:
        print(f"\nStopping container {container_name}...")
        container.remove(force=True)

def wait_for_ready(base_url, mode, container=None):
    print(f"Waiting for {mode} API to be ready at {base_url}...")
    start_time = time.time()
    ready = False
    timeout = 120 if "systemd" in mode else 45
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print("API is ready!")
                ready = True
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Check if container died while waiting
            if container:
                container.reload()
                if container.attrs.get('State', {}).get('Status') == 'exited':
                    break
            time.sleep(2)
    
    if not ready:
        if container:
            try:
                logs_raw = container.logs(stdout=True, stderr=True, tail=500)
                logs = logs_raw.decode('utf-8', errors='replace')
                print(f"\n--- API READINESS FAILURE LOGS ({mode}) ---\n{logs}\n--- END LOGS ---")
            except:
                print(f"Failed to fetch logs for {mode} container.")
        pytest.fail(f"API ({mode}) did not become ready in time at {base_url}.")

def pytest_generate_tests(metafunc):
    if "docker_stack" in metafunc.fixturenames:
        if metafunc.config.getoption("host"):
            metafunc.parametrize("docker_stack", ["host-standard", "host-systemd"], indirect=True)
        else:
            metafunc.parametrize("docker_stack", ["standard", "systemd"], indirect=True)

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
