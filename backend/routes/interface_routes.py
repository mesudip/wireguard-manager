from flask import Blueprint, jsonify, request
from services.interface_service import InterfaceService

interface_bp = Blueprint('interfaces', __name__)


def create_interface_routes(interface_service: InterfaceService):
    """Create interface routes with dependency injection."""
    
    @interface_bp.route('/interfaces', methods=['GET'])
    def list_interfaces():
        """List all interfaces."""
        interfaces = interface_service.list_interfaces()
        return jsonify(interfaces)
    
    @interface_bp.route('/interfaces', methods=['POST'])
    def create_interface():
        """Create a new interface."""
        data = request.json
        interface_name = data.get('name')
        
        if not interface_name:
            return jsonify({"error": "Interface name is required"}), 400
        
        try:
            result = interface_service.create_interface(
                name=interface_name,
                address=data.get('address', '10.0.0.1/24'),
                listen_port=data.get('listen_port', '51820')
            )
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    @interface_bp.route('/interfaces/<interface>', methods=['GET'])
    def get_interface(interface):
        """Get details of a specific interface."""
        try:
            result = interface_service.get_interface(interface)
            return jsonify(result)
        except FileNotFoundError:
            return jsonify({"error": "Interface not found"}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    @interface_bp.route('/interfaces/<interface>', methods=['PUT'])
    def update_interface(interface):
        """Update a specific interface."""
        data = request.json
        
        try:
            interface_service.update_interface(
                name=interface,
                address=data.get('address'),
                listen_port=data.get('listen_port')
            )
            return jsonify({"message": "Interface updated successfully"})
        except FileNotFoundError:
            return jsonify({"error": "Interface not found"}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    @interface_bp.route('/interfaces/<interface>', methods=['DELETE'])
    def delete_interface(interface):
        """Delete a specific interface."""
        try:
            interface_service.delete_interface(interface)
            return jsonify({"message": "Interface deleted successfully"})
        except FileNotFoundError:
            return jsonify({"error": "Interface not found"}), 404
    
    return interface_bp
