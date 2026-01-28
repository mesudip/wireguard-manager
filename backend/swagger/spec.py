from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
import json

def get_swagger_spec(app=None):
    """Generate OpenAPI 3.0 specification."""
    spec = APISpec(
        title="WireGuard Manager API",
        version="1.0.0",
        openapi_version="3.0.0",
        plugins=[FlaskPlugin()],
    )

    # Define components/schemas
    spec.components.schema("CommandLog", {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "return_code": {"type": "integer"},
            "stdout": {"type": "string"},
            "stderr": {"type": "string"}
        }
    })

    spec.components.schema("Interface", {
        "type": "object",
        "properties": {
            "name": {"type": "string", "example": "wg0"},
            "address": {"type": "string", "example": "10.0.0.1/24"},
            "listen_port": {"type": "string", "example": "51820"},
            "private_key": {"type": "string", "example": "cGhpcHBMVGtOU3h..."},
            "public_key": {"type": "string", "example": "MTVHVGtOU3hwaGl..."},
            "warnings": {"type": "string"},
            "commands": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/CommandLog"}
            }
        }
    })

    spec.components.schema("InterfaceCreate", {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string", "example": "wg0"},
            "address": {"type": "string", "example": "10.0.0.1/24"},
            "listen_port": {"type": "string", "example": "51820"}
        }
    })

    spec.components.schema("InterfaceUpdate", {
        "type": "object",
        "properties": {
            "address": {"type": "string", "example": "10.0.0.1/24"},
            "listen_port": {"type": "string", "example": "51820"}
        }
    })

    spec.components.schema("PeerState", {
        "type": "object",
        "properties": {
            "public_key": {"type": "string"},
            "endpoint": {"type": "string"},
            "allowed_ips": {"type": "string"},
            "latest_handshake": {"type": "integer"},
            "transfer_rx": {"type": "integer"},
            "transfer_tx": {"type": "integer"},
            "persistent_keepalive": {"type": "string"}
        }
    })

    spec.components.schema("InterfaceState", {
        "type": "object",
        "properties": {
            "interface": {"type": "string", "example": "wg0"},
            "public_key": {"type": "string"},
            "listening_port": {"type": "integer", "example": 51820},
            "status": {"type": "string", "enum": ["active", "inactive", "not_found"]},
            "message": {"type": "string"},
            "peers": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/PeerState"}
            },
            "warnings": {"type": "string"},
            "commands": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/CommandLog"}
            }
        }
    })

    spec.components.schema("DiffResponse", {
        "type": "object",
        "properties": {
            "diff": {"type": "string"},
            "status": {"type": "string", "enum": ["success", "inactive", "not_found", "error"]},
            "message": {"type": "string"},
            "warnings": {"type": "string"},
            "commands": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/CommandLog"}
            }
        }
    })

    spec.components.schema("Peer", {
        "type": "object",
        "properties": {
            "name": {"type": "string", "example": "client1"},
            "public_key": {"type": "string"},
            "private_key": {"type": "string"},
            "allowed_ips": {"type": "string", "example": "10.0.0.2/32"},
            "endpoint": {"type": "string", "example": "203.0.113.1:51820"},
            "persistent_keepalive": {"type": "string", "example": "25"},
            "warnings": {"type": "string"},
            "commands": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/CommandLog"}
            }
        }
    })

    spec.components.schema("PeerCreate", {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string", "example": "client1"},
            "allowed_ips": {"type": "string", "example": "10.0.0.2/32"},
            "endpoint": {"type": "string", "example": "203.0.113.1:51820"},
            "persistent_keepalive": {"type": "string", "example": "25"}
        }
    })

    spec.components.schema("PeerUpdate", {
        "type": "object",
        "properties": {
            "allowed_ips": {"type": "string", "example": "10.0.0.2/32"},
            "endpoint": {"type": "string", "example": "203.0.113.1:51820"},
            "persistent_keepalive": {"type": "string", "example": "25"}
        }
    })

    spec.components.schema("Error", {
        "type": "object",
        "properties": {
            "error": {"type": "string", "example": "Interface not found"},
            "type": {"type": "string", "example": "InterfaceNotFoundException"},
            "details": {"type": "string"}
        }
    })

    # Register paths from the app
    if app:
        with app.test_request_context():
            # Extract all endpoints
            for rule in app.url_map.iter_rules():
                if rule.endpoint.startswith('interfaces.') or \
                   rule.endpoint.startswith('peers.') or \
                   rule.endpoint.startswith('config.') or \
                   rule.endpoint.startswith('state.') or \
                   rule.endpoint == 'health_check':
                    spec.path(view=app.view_functions[rule.endpoint])

    return spec.to_dict()
