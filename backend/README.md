# WireGuard Backend API

Flask-based REST API for managing WireGuard VPN configurations with a modular architecture.

## Architecture

The backend is organized into the following modules:

### Models (`models/`)
Type definitions using Python's `TypedDict` for strong typing:
- `InterfaceConfig` - Interface configuration structure
- `PeerConfig` - Peer configuration structure
- `WireGuardConfig` - Complete WireGuard config structure
- Response types for API endpoints

### Services (`services/`)
Business logic layer with clear separation of concerns:
- `interface_service.py` - Interface CRUD operations
- `peer_service.py` - Peer management operations
- `config_service.py` - Config synchronization and diffing
- `state_service.py` - Live state monitoring via `wg` command
- `crypto.py` - Key generation utilities
- `config.py` - Config file parsing and writing

### Routes (`routes/`)
API endpoint definitions using Flask Blueprints:
- `interface_routes.py` - Interface endpoints
- `peer_routes.py` - Peer endpoints
- `config_routes.py` - Config management endpoints
- `state_routes.py` - State monitoring endpoints

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure WireGuard tools are installed:
```bash
# Ubuntu/Debian
sudo apt-get install wireguard-tools

# macOS
brew install wireguard-tools
```

3. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Docker

1. Build the image:
```bash
docker build -t wireguard-api .
```

2. Run the container:
```bash
docker run -p 5000:5000 \
  -v /etc/wireguard:/etc/wireguard \
  --cap-add=NET_ADMIN \
  wireguard-api
```

## API Endpoints

### Health Check
- `GET /` - Health check endpoint

### Interfaces
- `GET /interfaces` - List all interfaces
- `POST /interfaces` - Create a new interface
  ```json
  {
    "name": "wg0",
    "address": "10.0.0.1/24",
    "listen_port": "51820"
  }
  ```
- `GET /interfaces/{interface}` - Get interface details
- `PUT /interfaces/{interface}` - Update interface
  ```json
  {
    "address": "10.0.0.1/24",
    "listen_port": "51820"
  }
  ```
- `DELETE /interfaces/{interface}` - Delete interface

### Peers
- `GET /interfaces/{interface}/peers` - List all peers
- `POST /interfaces/{interface}/peers` - Add a new peer
  ```json
  {
    "name": "peer1",
    "allowed_ips": "10.0.0.2/32",
    "endpoint": "192.168.1.100:51820"
  }
  ```
- `GET /interfaces/{interface}/peers/{peer_name}` - Get peer details
- `PUT /interfaces/{interface}/peers/{peer_name}` - Update peer
  ```json
  {
    "allowed_ips": "10.0.0.2/32",
    "endpoint": "192.168.1.100:51820"
  }
  ```
- `DELETE /interfaces/{interface}/peers/{peer_name}` - Delete peer

### Config Management
- `POST /interfaces/{interface}/config/apply` - Apply folder config to final config
  - Merges interface config with all peer configs into final `/etc/wireguard/{interface}.conf`
- `POST /interfaces/{interface}/config/reset` - Reset folder from final config
  - Splits final config into interface and individual peer files
- `GET /interfaces/{interface}/config/diff` - Get diff between folder and config
  - Shows differences between folder structure and final config file

### State Monitoring
- `GET /interfaces/{interface}/state` - Get current interface state
  - Returns live state from `wg show` command
- `GET /interfaces/{interface}/state/diff` - Get diff between state and config
  - Compares running state with config file

## Configuration Structure

### Folder Structure
```
/etc/wireguard/
├── wg0/
│   ├── wg0.conf          # Interface config (without peers)
│   ├── peer1.conf        # Individual peer config
│   └── peer2.conf        # Individual peer config
└── wg0.conf              # Final merged config (after apply)
```

### Workflow

1. **Create Interface**: Creates folder `/etc/wireguard/wg0/` with `wg0.conf`
2. **Add Peers**: Creates individual peer files like `peer1.conf`, `peer2.conf`
3. **Apply Config**: Merges all configs into final `/etc/wireguard/wg0.conf`
4. **Use WireGuard**: Use standard `wg-quick up wg0` with the final config
5. **Monitor State**: Check live state vs config with diff endpoints
6. **Reset Config**: Split final config back into folder structure for editing

## Error Handling

All services raise standard Python exceptions:
- `FileNotFoundError` - Resource not found (404)
- `ValueError` - Invalid input or state (400)
- `RuntimeError` - System errors like WireGuard command failures (500)

Routes catch these exceptions and return appropriate HTTP status codes with JSON error responses.

## Type Safety

The codebase uses Python's `TypedDict` for type hints throughout:
- All function parameters and return values are typed
- Config structures have explicit type definitions
- Use a type checker like `mypy` to verify type correctness:
  ```bash
  mypy backend/
  ```

## Development

### Running Tests
```bash
# TODO: Add tests
pytest tests/
```

### Code Style
Follow PEP 8 and use type hints throughout. Use `black` for formatting:
```bash
black backend/
