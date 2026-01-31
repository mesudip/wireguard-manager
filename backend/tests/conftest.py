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

# Pytest hook to show response body on assertion failures
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to add response body to assertion error messages."""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # Check if there are any local variables that are Response objects
        if hasattr(call, 'excinfo') and call.excinfo:
            try:
                # Get the local variables from the traceback
                tb = call.excinfo.traceback[-1]
                for var_name, var_value in tb.locals.items():
                    if isinstance(var_value, requests.Response):
                        # Add response details to the report
                        extra_info = f"\n\n{var_name} details:\n"
                        extra_info += f"  Status: {var_value.status_code}\n"
                        extra_info += f"  URL: {var_value.url}\n"
                        try:
                            extra_info += f"  Body: {var_value.text}\n"
                        except:
                            extra_info += f"  Body: <could not decode>\n"
                        
                        if not hasattr(report.longrepr, 'reprcrash'):
                            continue
                        # Append to the failure message
                        if hasattr(report.longrepr, 'reprtraceback'):
                            report.longrepr.reprtraceback.reprentries[-1].lines.append(extra_info)
            except Exception:
                pass  # Don't fail the test if we can't add extra info

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
        "cap_add": ["NET_ADMIN", "SYS_MODULE", "SYS_ADMIN"],
        "environment": env
    }
    
    if mode == "systemd":
        # Add systemd debugging environment variables
        env["SYSTEMD_LOG_LEVEL"] = "debug"
        env["SYSTEMD_SHOW_STATUS"] = "true"
        env["SYSTEMD_IGNORE_CHROOT"] = "1"
        
        kwargs["privileged"] = True
        kwargs["volumes"] = {
            '/sys/fs/cgroup': {'bind': '/sys/fs/cgroup', 'mode': 'rw'},
            '/lib/modules': {'bind': '/lib/modules', 'mode': 'ro'},
            '/sys/kernel/config': {'bind': '/sys/kernel/config', 'mode': 'ro'},
            '/sys/fs/fuse': {'bind': '/sys/fs/fuse', 'mode': 'rw'}
        }
        # Refined tmpfs for systemd 248+ (required for Ubuntu 24.04 base)
        kwargs["tmpfs"] = {
            '/run': 'rw,nosuid,nodev,mode=755',
            '/run/lock': 'rw,nosuid,nodev,noexec,relatime,size=5m',
            '/tmp': 'rw,nosuid,nodev'
        }
        kwargs["cgroupns_mode"] = "host"
        # Disable security restrictors which often block systemd PID 1 in GHA
        kwargs["security_opt"] = ["seccomp=unconfined", "apparmor=unconfined"]
    
    # Move cgroupns_mode to host_config if present
    if "cgroupns_mode" in kwargs:
        # cgroupns_mode should be in host_config, not main kwargs
        host_config_kwargs = {}
        # We'll need to manually handle this since the library doesn't recognize it
        cgroupns_mode = kwargs.pop("cgroupns_mode")
        # For now, let's try without it since it's not critical
        pass
    
    try:
        container = docker_client.containers.run(image_tag, **kwargs)
    except Exception as e:
        print(f"\nCRITICAL: Failed to start {mode} container. Error: {e}")
        print(f"Kwargs used: {kwargs}")
        raise

    # Give systemd a bit more time to reach the socket-binding stage
    time.sleep(5)
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
            container.reload()
            current_status = container.attrs.get('State', {}).get('Status', 'unknown')
            print(f"Readiness failed. Container status: {current_status}")
            
            try:
                # 1. Try standard logs
                logs_raw = container.logs(stdout=True, stderr=True, tail=300)
                logs = logs_raw.decode('utf-8', errors='replace')
                print(f"\n--- API READINESS FAILURE LOGS ({mode}) ---\n{logs}\n--- END LOGS ---")
                
                # 2. If systemd, try journalctl (often has the real info)
                if "systemd" in mode and current_status == "running":
                    print(f"Attempting to fetch journalctl output from {mode} container...")
                    result = container.exec_run("journalctl -n 100 --no-pager")
                    journal = result.output.decode('utf-8', errors='replace')
                    print(f"\n--- INTERNAL SYSTEMD JOURNAL ---\n{journal}\n--- END JOURNAL ---")
            except Exception as e:
                print(f"Failed to fetch detailed logs for {mode} container: {e}")
                
        pytest.fail(f"API ({mode}) did not become ready in time at {base_url}.")

def pytest_generate_tests(metafunc):
    if "docker_stack" in metafunc.fixturenames:
        # Some test runners or environments may not register the --host option.
        # Be defensive: if the option is missing, default to container modes.
        use_host = False
        try:
            use_host = bool(metafunc.config.getoption("host"))
        except Exception:
            use_host = False

        if use_host:
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

@pytest.fixture
def base_dir():
    """Fixture to provide the WireGuard base directory for file-based tests."""
    return "/etc/wireguard"
