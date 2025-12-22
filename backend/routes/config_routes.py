from flask import Blueprint, jsonify, request
from services.config_service import ConfigService

config_bp = Blueprint('config', __name__)


def create_config_routes(config_service: ConfigService):
    """Create config routes with dependency injection."""
    
    @config_bp.route('/interfaces/<interface>/config/apply', methods=['POST'])
    def apply_config(interface):
        """Generate the final config file from the interface folder."""
        try:
            path = config_service.apply_config(interface)
            return jsonify({"message": "Config applied successfully", "path": path})
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    @config_bp.route('/interfaces/<interface>/config/reset', methods=['POST'])
    def reset_config(interface):
        """Generate the interface folder from the final config file."""
        try:
            config_service.reset_config(interface)
            return jsonify({"message": "Config reset successfully"})
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    @config_bp.route('/interfaces/<interface>/config/diff', methods=['GET'])
    def get_config_diff(interface):
        """Get diff between folder structure and current conf file."""
        try:
            diff = config_service.get_config_diff(interface)
            return jsonify({"diff": diff})
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    return config_bp
