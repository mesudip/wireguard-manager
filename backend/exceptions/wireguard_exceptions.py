"""Custom exception classes for WireGuard Manager."""


class WireGuardException(Exception):
    """Base exception for all WireGuard Manager errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class CommandNotFoundException(WireGuardException):
    """Exception raised when wg command is not found."""
    def __init__(self, command: str = "wg"):
        message = (
            f"Command '{command}' not found. Please ensure WireGuard tools are installed "
            f"and accessible. Try installing with: apt-get install wireguard-tools"
        )
        super().__init__(message, status_code=500)


class PermissionDeniedException(WireGuardException):
    """Exception raised when permission is denied for an operation."""
    def __init__(self, operation: str = ""):
        message = (
            f"Permission denied{': ' + operation if operation else ''}. "
            f"Please ensure the service has proper sudo privileges."
        )
        super().__init__(message, status_code=403)


class InterfaceNotFoundException(WireGuardException):
    """Exception raised when an interface is not found."""
    def __init__(self, interface: str):
        message = f"Interface '{interface}' not found."
        super().__init__(message, status_code=404)


class PeerNotFoundException(WireGuardException):
    """Exception raised when a peer is not found."""
    def __init__(self, peer: str, interface: str = ""):
        message = f"Peer '{peer}' not found"
        if interface:
            message += f" in interface '{interface}'"
        message += "."
        super().__init__(message, status_code=404)


class ConfigurationException(WireGuardException):
    """Exception raised when there's a configuration error."""
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}", status_code=400)


class StateException(WireGuardException):
    """Exception raised when there's an error getting interface state."""
    def __init__(self, interface: str, details: str = ""):
        message = f"Failed to get state for interface '{interface}'"
        if details:
            message += f": {details}"
        super().__init__(message, status_code=500)
