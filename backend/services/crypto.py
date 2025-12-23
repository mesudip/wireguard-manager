import subprocess
from typing import Tuple
from utils.command import run_command
from exceptions.wireguard_exceptions import CommandNotFoundException


def generate_keys() -> Tuple[str, str]:
    """
    Generate WireGuard private and public keys.
    
    Returns:
        Tuple of (private_key, public_key)
        
    Raises:
        CommandNotFoundException: If wg command is not found
    """
    try:
        result = run_command(["wg", "genkey"])
        private_key = result.stdout.decode().strip()
        
        result = run_command(["wg", "pubkey"], input_data=private_key.encode())
        public_key = result.stdout.decode().strip()
        
        return private_key, public_key
    except Exception as e:
        if isinstance(e, CommandNotFoundException):
            raise
        raise RuntimeError(f"Failed to generate keys: {str(e)}")


def get_public_key(private_key: str) -> str:
    """
    Get public key from private key.
    
    Args:
        private_key: WireGuard private key
        
    Returns:
        Public key string
    """
    try:
        result = run_command(["wg", "pubkey"], input_data=private_key.encode())
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError:
        return ""
    except Exception:
        return ""
