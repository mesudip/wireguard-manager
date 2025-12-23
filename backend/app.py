from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import subprocess
import configparser
from pathlib import Path
import json
from datetime import datetime
import difflib
import socket

from config.app_config import AppConfig
from utils.logger import setup_logger
from exceptions.wireguard_exceptions import WireGuardException

from services.interface_service import InterfaceService
from services.peer_service import PeerService
from services.config_service import ConfigService
from services.state_service import StateService
from routes.interface_routes import create_interface_routes
from routes.peer_routes import create_peer_routes
from routes.config_routes import create_config_routes
from routes.state_routes import create_state_routes

config = AppConfig()

logger = setup_logger(
    name='wireguard-manager',
    level=config.logging_level,
    method=config.logging_method,
    log_dir=config.logging_dir if config.logging_method == 'directory' else None,
    max_bytes=config.logging_max_bytes,
    backup_count=config.logging_backup_count
)

STATIC_FOLDER = '/lib/wireguard/backend'

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')

if config.cors_enabled:
    cors_config = {
        'origins': config.cors_origins,
        'methods': config.cors_methods,
        'allow_headers': config.cors_allow_headers,
        'supports_credentials': config.cors_supports_credentials,
        'max_age': config.cors_max_age,
    }
    
    # Add expose_headers if configured
    if config.cors_expose_headers:
        cors_config['expose_headers'] = config.cors_expose_headers
    
    CORS(app, **cors_config)
    logger.info(f"CORS enabled with origins: {config.cors_origins}")
else:
    logger.info("CORS disabled")

BASE_DIR = config.wireguard_base_dir
Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

interface_service = InterfaceService(BASE_DIR)
peer_service = PeerService(BASE_DIR)
config_service = ConfigService(BASE_DIR)
state_service = StateService(BASE_DIR)

interface_bp = create_interface_routes(interface_service)
peer_bp = create_peer_routes(peer_service)
config_bp = create_config_routes(config_service)
state_bp = create_state_routes(state_service)

app.register_blueprint(interface_bp, url_prefix='/api')
app.register_blueprint(peer_bp, url_prefix='/api')
app.register_blueprint(config_bp, url_prefix='/api')
app.register_blueprint(state_bp, url_prefix='/api')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return jsonify({"status": "ok", "message": "WireGuard API is running"})


@app.errorhandler(WireGuardException)
def handle_wireguard_exception(error):
    """Handle custom WireGuard exceptions."""
    logger.error(f"WireGuard error: {error.message}")
    response = jsonify({
        "error": error.message,
        "type": error.__class__.__name__
    })
    response.status_code = error.status_code
    return response

@app.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors."""
    # Check if it's an API request
    if request.path.startswith('/api/'):
        logger.warning(f"API endpoint not found: {request.path}")
        return jsonify({
            "error": "Endpoint not found",
            "path": request.path
        }), 404
    
    # For non-API routes, serve the static index.html (SPA routing)
    try:
        return send_from_directory(STATIC_FOLDER, 'index.html')
    except Exception as e:
        logger.error(f"Failed to serve index.html: {e}")
        return jsonify({
            "error": "Frontend not found",
            "details": "The static files may not be installed. Please run the installation script."
        }), 404

@app.errorhandler(Exception)
def handle_generic_exception(error):
    """Handle all other exceptions."""
    # Don't log 404 as exceptions
    if isinstance(error, Exception) and '404' in str(error):
        return handle_not_found(error)
    
    logger.exception(f"Unhandled exception: {str(error)}")
    
    # Check if it's an API request
    if request.path.startswith('/api/'):
        response = jsonify({
            "error": "An internal server error occurred",
            "details": str(error) if config.debug else None,
            "path": request.path
        })
        response.status_code = 500
        return response
    
    # For non-API routes, try to serve index.html
    try:
        return send_from_directory(STATIC_FOLDER, 'index.html')
    except:
        return jsonify({
            "error": "An internal server error occurred",
            "details": str(error) if config.debug else None
        }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """Serve static frontend files."""
    # Never serve API routes as static files
    if path.startswith('api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    
    if path != "" and os.path.exists(os.path.join(STATIC_FOLDER, path)):
        return send_from_directory(STATIC_FOLDER, path)
    else:
        # Serve index.html for all non-API routes (SPA routing)
        try:
            return send_from_directory(STATIC_FOLDER, 'index.html')
        except Exception as e:
            logger.error(f"Failed to serve static files: {e}")
            return jsonify({
                "error": "Frontend not found",
                "details": "The static files may not be installed. Run: sudo ./install.sh"
            }), 404

def main():
    """Main entry point for console script."""
    host = config.server_host
    port = config.server_port
    debug = config.debug
    
    logger.info(f"Starting WireGuard Manager on {host}:{port} (debug={debug})")
    logger.info(f"Serving static files from: {STATIC_FOLDER}")
    
    # Try to bind to configured host
    try:
        app.run(host=host, port=port, debug=debug)
    except (OSError, socket.error) as e:
        if host == '::':
            # Fallback to IPv4 if IPv6 not available
            logger.warning(f"Failed to bind to {host}: {e}")
            logger.info("Falling back to IPv4 only (0.0.0.0)")
            app.run(host='0.0.0.0', port=port, debug=debug)
        else:
            raise


if __name__ == '__main__':
    host = config.server_host
    port = config.server_port
    
    try:
        app.run(host=host, port=port, debug=True)
    except (OSError, socket.error) as e:
        if host == '::':
            logger.warning(f"Failed to bind to {host}: {e}")
            logger.info("Falling back to IPv4 only (0.0.0.0)")
            app.run(host='0.0.0.0', port=port, debug=True)
        else:
            raise
