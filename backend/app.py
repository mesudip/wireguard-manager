from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import subprocess
import configparser
from pathlib import Path
import json
from datetime import datetime
import difflib

from services.interface_service import InterfaceService
from services.peer_service import PeerService
from services.config_service import ConfigService
from services.state_service import StateService
from routes.interface_routes import create_interface_routes
from routes.peer_routes import create_peer_routes
from routes.config_routes import create_config_routes
from routes.state_routes import create_state_routes

app = Flask(__name__)
CORS(app)

BASE_DIR = "/etc/wireguard"
Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

interface_service = InterfaceService(BASE_DIR)
peer_service = PeerService(BASE_DIR)
config_service = ConfigService(BASE_DIR)
state_service = StateService(BASE_DIR)

interface_bp = create_interface_routes(interface_service)
peer_bp = create_peer_routes(peer_service)
config_bp = create_config_routes(config_service)
state_bp = create_state_routes(state_service)

app.register_blueprint(interface_bp)
app.register_blueprint(peer_bp)
app.register_blueprint(config_bp)
app.register_blueprint(state_bp)


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "WireGuard API is running"})


def main():
    """Main entry point for console script."""
    # This allows the server to accept connections on both IPv4 and IPv6
    import socket
    
    # Try to bind to IPv6 first (which typically handles IPv4 too on dual-stack)
    try:
        app.run(host='::', port=5000, debug=False)
    except (OSError, socket.error):
        # Fallback to IPv4 if IPv6 not available
        print("Warning: IPv6 not available, falling back to IPv4 only")
        app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    import socket
    try:
        app.run(host='::', port=5000, debug=True)
    except (OSError, socket.error):
        print("Warning: IPv6 not available, falling back to IPv4 only")
        app.run(host='0.0.0.0', port=5000, debug=True)
