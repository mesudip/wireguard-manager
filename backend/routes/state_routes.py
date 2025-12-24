from flask import Blueprint, jsonify, request
from services.state_service import StateService

state_bp = Blueprint('state', __name__)


def create_state_routes(state_service: StateService):
    """Create state routes with dependency injection."""
    
    @state_bp.route('/interfaces/<interface>/state', methods=['GET'])
    def get_state(interface):
        """Get current state (equivalent to wg show).
        ---
        get:
          tags: ["State"]
          summary: Get interface state
          description: Get current state of interface from wg show command
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: Interface state
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/InterfaceState"}
        """
        state = state_service.get_state(interface)
        return jsonify(state)
    
    @state_bp.route('/interfaces/<interface>/state/diff', methods=['GET'])
    def get_state_diff(interface):
        """Get diff between wg command output and current conf file.
        ---
        get:
          tags: ["State"]
          summary: Get state diff
          description: Get diff between wg show output and current conf file
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: State diff
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/DiffResponse"}
        """
        result = state_service.get_state_diff(interface)
        return jsonify(result)
    
    return state_bp
