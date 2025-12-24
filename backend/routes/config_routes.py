from flask import Blueprint, jsonify, request
from services.config_service import ConfigService

config_bp = Blueprint('config', __name__)


def create_config_routes(config_service: ConfigService):
    """Create config routes with dependency injection."""
    
    @config_bp.route('/interfaces/<interface>/config/sync', methods=['POST'])
    def sync_config(interface):
        """Generate the final config file from the interface folder.
        ---
        post:
          tags: ["Config"]
          summary: Sync config
          description: Generate final config file from interface folder structure
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: Config synchronized successfully
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message: {"type": "string"}
                      path: {"type": "string"}
            404:
              description: Interface not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        try:
            path = config_service.sync_config(interface)
            return jsonify({"message": "Config synchronized successfully", "path": path})
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500

    @config_bp.route('/interfaces/<interface>/config/apply', methods=['POST'])
    def apply_config(interface):
        """Generate the config AND apply it to the running interface.
        ---
        post:
          tags: ["Config"]
          summary: Apply config
          description: Generate config AND apply it to running state (syncconf/up)
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: Config applied successfully
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message: {"type": "string"}
            404:
              description: Interface not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        try:
            # 1. Sync folder to .conf file
            config_service.sync_config(interface)
            
            # 2. Apply .conf file to running state
            warnings = config_service.apply_config(interface)
            return jsonify({
                "message": "Config applied and state updated successfully",
                "warnings": warnings
            })
                
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @config_bp.route('/interfaces/<interface>/config/reset', methods=['POST'])
    def reset_config(interface):
        """Generate the interface folder from the final config file.
        ---
        post:
          tags: ["Config"]
          summary: Reset config
          description: Generate interface folder from final config file
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: Config reset successfully
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message: {"type": "string"}
            404:
              description: Interface not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        try:
            config_service.reset_config(interface)
            return jsonify({"message": "Config reset successfully"})
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    @config_bp.route('/interfaces/<interface>/config/diff', methods=['GET'])
    def get_config_diff(interface):
        """Get diff between folder structure and current conf file.
        ---
        get:
          tags: ["Config"]
          summary: Get config diff
          description: Get diff between folder structure and current conf file
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: Config diff
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      diff: {"type": "string"}
            404:
              description: Interface not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        try:
            diff = config_service.get_config_diff(interface)
            return jsonify({"diff": diff})
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    return config_bp
