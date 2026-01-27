from flask import Blueprint, jsonify, request
from services.peer_service import PeerService

peer_bp = Blueprint('peers', __name__)


def create_peer_routes(peer_service: PeerService):
    """Create peer routes with dependency injection."""
    
    @peer_bp.route('/interfaces/<interface>/peers', methods=['GET'])
    def list_peers(interface):
        """List all peers for an interface.
        ---
        get:
          tags: ["Peers"]
          summary: List peers
          description: Get all peers for an interface
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
              description: Interface name
          responses:
            200:
              description: List of peers
              content:
                application/json:
                  schema:
                    type: array
                    items: {"$ref": "#/components/schemas/Peer"}
            404:
              description: Interface not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        try:
            peers = peer_service.list_peers(interface)
            return jsonify(peers)
        except FileNotFoundError:
            return jsonify({"error": "Interface not found"}), 404
    
    @peer_bp.route('/interfaces/<interface>/peers', methods=['POST'])
    def add_peer(interface):
        """Add a new peer to an interface.
        ---
        post:
          tags: ["Peers"]
          summary: Add peer
          description: Add a new peer to an interface
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
          requestBody:
            required: true
            content:
              application/json:
                schema: {"$ref": "#/components/schemas/PeerCreate"}
          responses:
            201:
              description: Peer created successfully
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Peer"}
            400:
              description: Invalid request
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
            404:
              description: Interface not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        data = request.json
        peer_name = data.get('name')
        
        if not peer_name:
            return jsonify({"error": "Peer name is required"}), 400
        
        try:
          result = peer_service.add_peer(
            interface=interface,
            name=peer_name,
            allowed_ips=data.get('allowed_ips'),
            endpoint=data.get('endpoint', ''),
            public_key=data.get('public_key')
          )
          return jsonify(result), 201
        except FileNotFoundError:
          return jsonify({"error": "Interface not found"}), 404
        except ValueError as e:
          return jsonify({"error": str(e)}), 400
    
    @peer_bp.route('/interfaces/<interface>/peers/<peer_name>', methods=['GET'])
    def get_peer(interface, peer_name):
        """Get details of a specific peer.
        ---
        get:
          tags: ["Peers"]
          summary: Get peer details
          description: Get details of a specific peer
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
            - name: peer_name
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: Peer details
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Peer"}
            404:
              description: Peer not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        try:
            result = peer_service.get_peer(interface, peer_name)
            return jsonify(result)
        except FileNotFoundError:
            return jsonify({"error": "Peer not found"}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    
    @peer_bp.route('/interfaces/<interface>/peers/<peer_name>', methods=['PUT'])
    def update_peer(interface, peer_name):
        """Update a specific peer.
        ---
        put:
          tags: ["Peers"]
          summary: Update peer
          description: Update an existing peer
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
            - name: peer_name
              in: path
              required: true
              schema: {"type": "string"}
          requestBody:
            required: true
            content:
              application/json:
                schema: {"$ref": "#/components/schemas/PeerUpdate"}
          responses:
            200:
              description: Peer updated successfully
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message: {"type": "string"}
            404:
              description: Peer not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        data = request.json
        
        try:
          peer_service.update_peer(
            interface=interface,
            peer_name=peer_name,
            allowed_ips=data.get('allowed_ips'),
            endpoint=data.get('endpoint'),
            new_name=data.get('name'),
            public_key=data.get('public_key')
          )
          return jsonify({"message": "Peer updated successfully"})
        except FileNotFoundError:
          return jsonify({"error": "Peer not found"}), 404
        except ValueError as e:
          return jsonify({"error": str(e)}), 400
    
    @peer_bp.route('/interfaces/<interface>/peers/<peer_name>', methods=['DELETE'])
    def delete_peer(interface, peer_name):
        """Delete a specific peer.
        ---
        delete:
          tags: ["Peers"]
          summary: Delete peer
          description: Delete an existing peer
          parameters:
            - name: interface
              in: path
              required: true
              schema: {"type": "string"}
            - name: peer_name
              in: path
              required: true
              schema: {"type": "string"}
          responses:
            200:
              description: Peer deleted successfully
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message: {"type": "string"}
            404:
              description: Peer not found
              content:
                application/json:
                  schema: {"$ref": "#/components/schemas/Error"}
        """
        try:
          peer_service.delete_peer(interface, peer_name)
          return jsonify({"message": "Peer deleted successfully"})
        except FileNotFoundError:
            return jsonify({"error": "Peer not found"}), 404
    
    return peer_bp
