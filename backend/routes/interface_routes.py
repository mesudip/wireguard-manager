from flask import Blueprint, jsonify, request
from services.interface_service import InterfaceService
from exceptions.wireguard_exceptions import (
    InterfaceNotFoundException,
    ConfigurationException
)

interface_bp = Blueprint('interfaces', __name__)


def create_interface_routes(interface_service: InterfaceService):
    """Create interface routes with dependency injection."""
    
    @interface_bp.route('/interfaces', methods=['GET'])
    def list_interfaces():
        """List all interfaces.
        ---
        get:
          tags: ["Interfaces"]
          summary: List all interfaces
          description: Get a list of all WireGuard interfaces
          responses:
            200:
              description: List of interfaces
              content:
                application/json:
                  schema:
                    type: array
                    items: {"$ref": "#/components/schemas/Interface"}
        """
        interfaces = interface_service.list_interfaces()
        return jsonify(interfaces)
    
    @interface_bp.route('/interfaces', methods=['POST'])
    def create_interface():
        """Create a new interface.
        ---
        post:
          tags: ["Interfaces"]
          summary: Create a new interface
          description: Create a new WireGuard interface
          requestBody:
            required: true
            content:
              application/json:
                schema: {"$ref": "#/components/schemas/InterfaceCreate"}
          responses:
            201:
              description: Interface created successfully
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Interface"}
            400:
              description: Invalid request
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        data = request.json
        interface_name = data.get('name')
        
        if not interface_name:
            raise ConfigurationException("Interface name is required")
        
        result = interface_service.create_interface(
            name=interface_name,
            address=data.get('address', '10.0.0.1/24'),
            listen_port=data.get('listen_port', '51820')
        )
        return jsonify(result), 201
    
    @interface_bp.route('/interfaces/<interface>', methods=['GET'])
    def get_interface(interface):
        """Get interface details.
        ---
        get:
          tags: ["Interfaces"]
          summary: Get interface details
          description: Get details of a specific interface
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
              description: Interface name (e.g., wg0)
          responses:
            200:
              description: Interface details
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Interface"}
            404:
              description: Interface not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        result = interface_service.get_interface(interface)
        return jsonify(result)
    
    @interface_bp.route('/interfaces/<interface>', methods=['PUT'])
    def update_interface(interface):
        """Update interface.
        ---
        put:
          tags: ["Interfaces"]
          summary: Update interface
          description: Update an existing interface
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          requestBody:
            required: true
            content:
              application/json:
                schema: {"$ref": "#/components/schemas/InterfaceUpdate"}
          responses:
            200:
              description: Interface updated successfully
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
        data = request.json
        
        interface_service.update_interface(
            name=interface,
            address=data.get('address'),
            listen_port=data.get('listen_port')
        )
        return jsonify({"message": "Interface updated successfully"})
    
    @interface_bp.route('/interfaces/<interface>', methods=['DELETE'])
    def delete_interface(interface):
        """Delete interface.
        ---
        delete:
          tags: ["Interfaces"]
          summary: Delete interface
          description: Delete an existing interface
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: Interface deleted successfully
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
        interface_service.delete_interface(interface)
        return jsonify({"message": "Interface deleted successfully"})
    
    return interface_bp
