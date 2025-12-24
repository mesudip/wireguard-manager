import subprocess
from typing import Tuple, Optional
from utils.command import run_command
from exceptions.wireguard_exceptions import CommandNotFoundException


def generate_keys() -> Tuple[str, str, Optional[str]]:
    """
    Generate WireGuard private and public keys.
    
    Returns:
        Tuple of (private_key, public_key, warnings)
        
    Raises:
        CommandNotFoundException: If wg command is not found
    """
    warnings = []
    try:
        result = run_command(["wg", "genkey"])
        private_key = result.stdout.decode().strip()
        if result.stderr:
            warnings.append(result.stderr.decode())
        
        result = run_command(["wg", "pubkey"], input_data=private_key.encode())
        public_key = result.stdout.decode().strip()
        if result.stderr:
            warnings.append(result.stderr.decode())
        
        return private_key, public_key, ("\n".join(warnings) if warnings else None)
    except Exception as e:
        if isinstance(e, CommandNotFoundException):
            raise
        raise RuntimeError(f"Failed to generate keys: {str(e)}")


def get_public_key(private_key: str) -> Tuple[str, Optional[str]]:
    """
    Get public key from private key.
    
    Args:
        private_key: WireGuard private key
        
    Returns:
        Tuple of (public_key, warnings)
    """
    try:
        result = run_command(["wg", "pubkey"], input_data=private_key.encode())
        return result.stdout.decode().strip(), (result.stderr.decode() if result.stderr else None)
    except subprocess.CalledProcessError:
        return "", None
    except Exception:
        return "", None
