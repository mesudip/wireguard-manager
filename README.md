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

## Quick Start

### Backend Setup

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

### Frontend Setup

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
NEXT_PUBLIC_API_URL=http://localhost:5000
```

4. Run development server:
```bash
npm run dev
```

5. Build static site:
```bash
npm run build
```

The static files will be in the `out` directory.

## Docker Deployment

### Backend

```bash
cd backend
docker build -t wireguard-api .
docker run -p 5000:5000 \
  -v /etc/wireguard:/etc/wireguard \
  --cap-add=NET_ADMIN \
  wireguard-api
```

### Frontend

The frontend builds to a static site that can be served with any web server:

```bash
npm run build
# Serve the 'out' directory with nginx, Apache, or any static file server
```

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
- `GET /interfaces` - List all interfaces
- `POST /interfaces` - Create a new interface
- `GET /interfaces/{interface}` - Get interface details
- `PUT /interfaces/{interface}` - Update interface
- `DELETE /interfaces/{interface}` - Delete interface

### Peers
- `GET /interfaces/{interface}/peers` - List all peers
- `POST /interfaces/{interface}/peers` - Add a new peer
- `GET /interfaces/{interface}/peers/{peer_name}` - Get peer details
- `PUT /interfaces/{interface}/peers/{peer_name}` - Update peer
- `DELETE /interfaces/{interface}/peers/{peer_name}` - Delete peer

### Config Operations
- `POST /interfaces/{interface}/config/apply` - Generate final config from folder
- `POST /interfaces/{interface}/config/reset` - Generate folder from final config
- `GET /interfaces/{interface}/config/diff` - Get diff between folder and config

### State Monitoring
- `GET /interfaces/{interface}/state` - Get current interface state (wg show)
- `GET /interfaces/{interface}/state/diff` - Get diff between state and config

## Security Notes

- Private keys never leave the backend - only public keys are returned to clients
- Ensure the Flask API is behind authentication in production
- Consider using HTTPS/TLS for API communication
- Set appropriate file permissions on `/etc/wireguard` directory

## Technology Stack

**Backend:**
- Python 3.11+
- Flask 3.0
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
```

```json file="" isHidden
