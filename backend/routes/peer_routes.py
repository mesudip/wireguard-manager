from flask import Blueprint, jsonify, request
from services.peer_service import PeerService

peer_bp = Blueprint('peers', __name__)


def create_peer_routes(peer_service: PeerService):
    """Create peer routes with dependency injection."""
    
    @peer_bp.route('/interfaces/<interface>/peers', methods=['GET'])
    def list_peers(interface):
        """List all peers for an interface."""
        try:
            peers = peer_service.list_peers(interface)
            return jsonify(peers)
        except FileNotFoundError:
            return jsonify({"error": "Interface not found"}), 404
    
    @peer_bp.route('/interfaces/<interface>/peers', methods=['POST'])
    def add_peer(interface):
        """Add a new peer to an interface."""
        data = request.json
        peer_name = data.get('name')
        
        if not peer_name:
            return jsonify({"error": "Peer name is required"}), 400
        
        try:
            result = peer_service.add_peer(
                interface=interface,
                name=peer_name,
                allowed_ips=data.get('allowed_ips', '10.0.0.2/32'),
                endpoint=data.get('endpoint', '')
            )
            return jsonify(result), 201
        except FileNotFoundError:
            return jsonify({"error": "Interface not found"}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    @peer_bp.route('/interfaces/<interface>/peers/<peer_name>', methods=['GET'])
    def get_peer(interface, peer_name):
        """Get details of a specific peer."""
        try:
            result = peer_service.get_peer(interface, peer_name)
            return jsonify(result)
        except FileNotFoundError:
            return jsonify({"error": "Peer not found"}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    @peer_bp.route('/interfaces/<interface>/peers/<peer_name>', methods=['PUT'])
    def update_peer(interface, peer_name):
        """Update a specific peer."""
        data = request.json
        
        try:
            peer_service.update_peer(
                interface=interface,
                peer_name=peer_name,
                allowed_ips=data.get('allowed_ips'),
                endpoint=data.get('endpoint')
            )
            return jsonify({"message": "Peer updated successfully"})
        except FileNotFoundError:
            return jsonify({"error": "Peer not found"}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    @peer_bp.route('/interfaces/<interface>/peers/<peer_name>', methods=['DELETE'])
    def delete_peer(interface, peer_name):
        """Delete a specific peer."""
        try:
            peer_service.delete_peer(interface, peer_name)
            return jsonify({"message": "Peer deleted successfully"})
        except FileNotFoundError:
            return jsonify({"error": "Peer not found"}), 404
    
    return peer_bp
