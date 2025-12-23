"""OpenAPI specification for WireGuard Manager API."""

def get_swagger_spec():
    """Return the OpenAPI 3.0 specification."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "WireGuard Manager API",
            "description": "REST API for managing WireGuard VPN interfaces, peers, and configurations",
            "version": "1.0.0",
            "contact": {
                "name": "WireGuard Manager",
            }
        },
        "servers": [
            {
                "url": "/api",
                "description": "API Server"
            }
        ],
        "tags": [
            {
                "name": "Health",
                "description": "Health check endpoints"
            },
            {
                "name": "Interfaces",
                "description": "Manage WireGuard interfaces"
            },
            {
                "name": "Peers",
                "description": "Manage peers for interfaces"
            },
            {
                "name": "Config",
                "description": "Configuration sync operations"
            },
            {
                "name": "State",
                "description": "Live state monitoring"
            }
        ],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Health check",
                    "description": "Check if the API is running",
                    "responses": {
                        "200": {
                            "description": "API is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "ok"},
                                            "message": {"type": "string", "example": "WireGuard API is running"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces": {
                "get": {
                    "tags": ["Interfaces"],
                    "summary": "List all interfaces",
                    "description": "Get a list of all WireGuard interfaces",
                    "responses": {
                        "200": {
                            "description": "List of interfaces",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Interface"}
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Interfaces"],
                    "summary": "Create a new interface",
                    "description": "Create a new WireGuard interface",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/InterfaceCreate"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Interface created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Interface"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces/{interface}": {
                "get": {
                    "tags": ["Interfaces"],
                    "summary": "Get interface details",
                    "description": "Get details of a specific interface",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name (e.g., wg0)",
                            "example": "wg0"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Interface details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Interface"}
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "put": {
                    "tags": ["Interfaces"],
                    "summary": "Update interface",
                    "description": "Update an existing interface",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/InterfaceUpdate"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Interface updated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "tags": ["Interfaces"],
                    "summary": "Delete interface",
                    "description": "Delete an existing interface",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Interface deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces/{interface}/peers": {
                "get": {
                    "tags": ["Peers"],
                    "summary": "List peers",
                    "description": "Get all peers for an interface",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of peers",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Peer"}
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Peers"],
                    "summary": "Add peer",
                    "description": "Add a new peer to an interface",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PeerCreate"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Peer created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Peer"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces/{interface}/peers/{peer_name}": {
                "get": {
                    "tags": ["Peers"],
                    "summary": "Get peer details",
                    "description": "Get details of a specific peer",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        },
                        {
                            "name": "peer_name",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Peer name",
                            "example": "client1"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Peer details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Peer"}
                                }
                            }
                        },
                        "404": {
                            "description": "Peer not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "put": {
                    "tags": ["Peers"],
                    "summary": "Update peer",
                    "description": "Update an existing peer",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        },
                        {
                            "name": "peer_name",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Peer name",
                            "example": "client1"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PeerUpdate"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Peer updated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Peer not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "tags": ["Peers"],
                    "summary": "Delete peer",
                    "description": "Delete an existing peer",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        },
                        {
                            "name": "peer_name",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Peer name",
                            "example": "client1"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Peer deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Peer not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces/{interface}/config/apply": {
                "post": {
                    "tags": ["Config"],
                    "summary": "Apply config",
                    "description": "Generate final config file from interface folder structure",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Config applied successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"},
                                            "path": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces/{interface}/config/reset": {
                "post": {
                    "tags": ["Config"],
                    "summary": "Reset config",
                    "description": "Generate interface folder from final config file",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Config reset successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces/{interface}/config/diff": {
                "get": {
                    "tags": ["Config"],
                    "summary": "Get config diff",
                    "description": "Get diff between folder structure and current conf file",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Config diff",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "diff": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces/{interface}/state": {
                "get": {
                    "tags": ["State"],
                    "summary": "Get interface state",
                    "description": "Get current state of interface from wg show command",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Interface state",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/InterfaceState"}
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found or not running",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/interfaces/{interface}/state/diff": {
                "get": {
                    "tags": ["State"],
                    "summary": "Get state diff",
                    "description": "Get diff between wg show output and current conf file",
                    "parameters": [
                        {
                            "name": "interface",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Interface name",
                            "example": "wg0"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "State diff",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "diff": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Interface not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Interface": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "example": "wg0"},
                        "address": {"type": "string", "example": "10.0.0.1/24"},
                        "listen_port": {"type": "string", "example": "51820"},
                        "private_key": {"type": "string", "example": "cGhpcHBMVGtOU3h..."},
                        "public_key": {"type": "string", "example": "MTVHVGtOU3hwaGl..."}
                    }
                },
                "InterfaceCreate": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string", "example": "wg0"},
                        "address": {"type": "string", "example": "10.0.0.1/24"},
                        "listen_port": {"type": "string", "example": "51820"}
                    }
                },
                "InterfaceUpdate": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string", "example": "10.0.0.1/24"},
                        "listen_port": {"type": "string", "example": "51820"}
                    }
                },
                "InterfaceState": {
                    "type": "object",
                    "properties": {
                        "interface": {"type": "string", "example": "wg0"},
                        "public_key": {"type": "string"},
                        "listening_port": {"type": "integer", "example": 51820},
                        "peers": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PeerState"}
                        }
                    }
                },
                "Peer": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "example": "client1"},
                        "public_key": {"type": "string"},
                        "private_key": {"type": "string"},
                        "allowed_ips": {"type": "string", "example": "10.0.0.2/32"},
                        "endpoint": {"type": "string", "example": "203.0.113.1:51820"}
                    }
                },
                "PeerCreate": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string", "example": "client1"},
                        "allowed_ips": {"type": "string", "example": "10.0.0.2/32"},
                        "endpoint": {"type": "string", "example": "203.0.113.1:51820"}
                    }
                },
                "PeerUpdate": {
                    "type": "object",
                    "properties": {
                        "allowed_ips": {"type": "string", "example": "10.0.0.2/32"},
                        "endpoint": {"type": "string", "example": "203.0.113.1:51820"}
                    }
                },
                "PeerState": {
                    "type": "object",
                    "properties": {
                        "public_key": {"type": "string"},
                        "endpoint": {"type": "string"},
                        "allowed_ips": {"type": "string"},
                        "latest_handshake": {"type": "integer"},
                        "transfer_rx": {"type": "integer"},
                        "transfer_tx": {"type": "integer"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Interface not found"},
                        "type": {"type": "string", "example": "InterfaceNotFoundException"},
                        "details": {"type": "string"}
                    }
                }
            }
        }
    }
