from flask import Blueprint, jsonify, request
from services.state_service import StateService

state_bp = Blueprint('state', __name__)


def create_state_routes(state_service: StateService):
    """Create state routes with dependency injection."""
    
    @state_bp.route('/interfaces/<interface>/state', methods=['GET'])
    def get_state(interface):
        """Get current state (equivalent to wg show)."""
        state = state_service.get_state(interface)
        return jsonify(state)
    
    @state_bp.route('/interfaces/<interface>/state/diff', methods=['GET'])
    def get_state_diff(interface):
        """Get diff between wg command output and current conf file."""
        diff = state_service.get_state_diff(interface)
        return jsonify({"diff": diff})
    
    return state_bp
