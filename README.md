# WireGuard Manager

A full-stack WireGuard VPN management application with a Python Flask backend and Next.js static frontend.

## Architecture

- **Backend**: Python Flask REST API for managing WireGuard configurations
- **Frontend**: Next.js static site with TypeScript and Tailwind CSS
- **Design System**: Mono (monospace fonts, minimal borders, technical aesthetic)

## Features

- **Interface Management**: Create, update, and delete WireGuard interfaces
- **Peer Management**: Add, edit, and remove peers with public key generation
- **Config Operations**: 
  - Apply folder structure to final config file
  - Reset folder structure from config file
  - View diffs between folder and config
- **Live State Monitoring**: View active interface status and peer connections (via `wg show`)
- **Bidirectional Sync**: Support for both folder → config and config → folder workflows
- **IPv6 Support**: Backend supports both IPv4 and IPv6
- **CORS Configuration**: Flexible CORS settings via config file

## Installation

### Quick Install (Recommended)

Run the main installation script as root:

```bash
sudo ./install.sh
```

This will:
1. Build the frontend (if `dist` folder is empty)
2. Install static files to `/lib/wireguard/backend`
3. Install and configure the backend service
4. Start the WireGuard Manager service

After installation, access the application at `http://your-server-ip:5000`

### Manual Setup (Development)

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure WireGuard tools are installed:
```bash
# Ubuntu/Debian
sudo apt-get install wireguard-tools

# macOS
brew install wireguard-tools
```

4. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

#### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update the API URL in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

4. Run development server:
```bash
npm run dev
```

5. Build static site:
```bash
npm run build
```

The static files will be in the `dist` directory.

## Configuration

### Backend Configuration

The backend is configured via `/etc/wireguard/backend.conf`:

```ini
[server]
# Server host - use '::' for IPv4+IPv6, '0.0.0.0' for IPv4 only
host = ::
port = 5000
debug = false

[cors]
# Enable CORS support
enabled = true
# CORS origins - use '*' for all, or comma-separated list of domains
origins = *
methods = GET,POST,PUT,DELETE,OPTIONS
allow_headers = Content-Type,Authorization
expose_headers = 
supports_credentials = false
max_age = 3600

[wireguard]
base_dir = /etc/wireguard

[logging]
# Logging method: 'console' (stdout) or 'directory' (rotating files)
method = console
level = INFO
dir = /var/log/wireguard-manager
max_bytes = 10485760
backup_count = 5
```

After changing configuration, restart the service:
```bash
sudo systemctl restart wireguard-manager
```

### IPv6 Support

The backend supports both IPv4 and IPv6:
- Set `host = ::` to listen on both IPv4 and IPv6
- Set `host = 0.0.0.0` for IPv4 only
- WireGuard interfaces support IPv6 addresses (e.g., `fd00::1/64`)
- Peers can use dual-stack addresses

### Logging

Two logging methods are available:

1. **Console** (default): Logs to stdout, visible via `journalctl`
   ```bash
   journalctl -u wireguard-manager -f
   ```

2. **Directory**: Logs to rotating files in `/var/log/wireguard-manager/`
   - `wireguard-manager.log` - All logs
   - `wireguard-manager.error.log` - Error logs only
   - Automatic rotation at 10MB (configurable)

## Configuration Structure

WireGuard configs are organized as follows:

```
/etc/wireguard/
├── wg0/                    # Interface folder
│   ├── wg0.conf           # Interface config (no peers)
│   ├── peer1.conf         # Individual peer config
│   └── peer2.conf         # Individual peer config
└── wg0.conf               # Final generated config (with all peers)
```

## API Endpoints

### Interfaces
- `GET /api/interfaces` - List all interfaces
- `POST /api/interfaces` - Create a new interface
- `GET /api/interfaces/{interface}` - Get interface details
- `PUT /api/interfaces/{interface}` - Update interface
- `DELETE /api/interfaces/{interface}` - Delete interface

### Peers
- `GET /api/interfaces/{interface}/peers` - List all peers
- `POST /api/interfaces/{interface}/peers` - Add a new peer
- `GET /api/interfaces/{interface}/peers/{peer_name}` - Get peer details
- `PUT /api/interfaces/{interface}/peers/{peer_name}` - Update peer
- `DELETE /api/interfaces/{interface}/peers/{peer_name}` - Delete peer

### Config Operations
- `POST /api/interfaces/{interface}/config/apply` - Generate final config from folder
- `POST /api/interfaces/{interface}/config/reset` - Generate folder from final config
- `GET /api/interfaces/{interface}/config/diff` - Get diff between folder and config

### State Monitoring
- `GET /api/interfaces/{interface}/state` - Get current interface state (wg show)
- `GET /api/interfaces/{interface}/state/diff` - Get diff between state and config

### Health Check
- `GET /api/health` - Service health check

## Service Management

```bash
# Check service status
sudo systemctl status wireguard-manager

# Start service
sudo systemctl start wireguard-manager

# Stop service
sudo systemctl stop wireguard-manager

# Restart service
sudo systemctl restart wireguard-manager

# View logs
sudo journalctl -u wireguard-manager -f

# View error logs (directory logging only)
sudo tail -f /var/log/wireguard-manager/wireguard-manager.error.log
```

## Uninstallation

```bash
cd backend
sudo ./uninstall.sh
```

This will:
- Stop and disable the service
- Remove the systemd service file
- Remove the installation directory
- Remove the service user
- Optionally remove configuration and logs

## Security Notes

- Private keys never leave the backend - only public keys are returned to clients
- Ensure the Flask API is behind authentication in production
- Consider using HTTPS/TLS for API communication
- Set appropriate file permissions on `/etc/wireguard` directory
- The service runs with restricted permissions (NoNewPrivileges, ProtectSystem)
- Only specific WireGuard commands are allowed via sudo

## Technology Stack

**Backend:**
- Python 3.11+
- Flask 3.0
- Flask-CORS
- WireGuard Tools

**Frontend:**
- Next.js 16 (Static Export)
- React 19
- TypeScript
- Tailwind CSS v4
- shadcn/ui components
- Mono Design System

## Development

The project uses the Mono design system with these characteristics:
- Monospace fonts (Geist Mono)
- Sharp corners (no border radius)
- Minimal, technical aesthetic
- High contrast colors
- Clear hierarchy with spacing

## License

MIT
