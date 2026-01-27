from flask import Blueprint, jsonify, request
from services.interface_service import InterfaceService
from exceptions.wireguard_exceptions import (
    InterfaceNotFoundException,
    ConfigurationException
)
from services.host_info_service import HostInfoService

interface_bp = Blueprint('interfaces', __name__)


def create_interface_routes(interface_service: InterfaceService, host_info_service: HostInfoService):
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
        host_info = host_info_service.get_host_info()
        
        response = {
            "host": {
                "ips": host_info.get("ips", []),
                "message": host_info.get("message") or host_info.get("error")
            },
            "wireguard": interfaces
        }
        return jsonify(response)
    
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
            listen_port=data.get('listen_port', '51820'),
            post_up=data.get('post_up'),
            post_down=data.get('post_down'),
            dns=data.get('dns')
        )
        # InterfaceService handles syncing; return result
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
            listen_port=data.get('listen_port'),
            post_up=data.get('post_up'),
            post_down=data.get('post_down'),
            dns=data.get('dns')
        )
        # InterfaceService handles syncing; return result
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
        # No need to sync after delete; folder removed
        return jsonify({"message": "Interface deleted successfully"})

    @interface_bp.route('/host/info', methods=['POST'])
    def update_host_info():
        """Update host info manually.
        ---
        post:
          tags: ["Host Info"]
          summary: Update host info manually
          description: Manually set the host's public IP addresses. This sets the 'manual' flag to true.
          requestBody:
            required: true
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    ips:
                      type: array
                      items:
                        type: string
          responses:
            200:
              description: Host info updated successfully
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/HostInfo"}
        """
        data = request.json
        ips = data.get('ips', [])
        result = host_info_service.save_host_info(ips, manual=True)
        return jsonify(result)

    @interface_bp.route('/host/info/rescan', methods=['POST'])
    def rescan_host_info():
        """Rescan host info.
        ---
        post:
          tags: ["Host Info"]
          summary: Rescan host info
          description: Force a re-discovery of host's public IP addresses. This sets the 'manual' flag to false.
          responses:
            200:
              description: Host info rescanned successfully
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/HostInfo"}
        """
        result = host_info_service.update_host_info(force=True)
        return jsonify(result)
    
    return interface_bp
