import subprocess
from typing import Tuple


def generate_keys() -> Tuple[str, str]:
    """
    Generate WireGuard private and public keys.
    
    Returns:
        Tuple of (private_key, public_key)
    """
    private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    public_key = subprocess.check_output(
        ["wg", "pubkey"], input=private_key.encode()
    ).decode().strip()
    return private_key, public_key


def get_public_key(private_key: str) -> str:
    """
    Get public key from private key.
    
    Args:
        private_key: WireGuard private key
        
    Returns:
        Public key string
    """
    try:
        return subprocess.check_output(
            ["wg", "pubkey"], input=private_key.encode()
        ).decode().strip()
    except subprocess.CalledProcessError:
        return ""
