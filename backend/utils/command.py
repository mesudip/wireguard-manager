"""Utility functions for executing system commands."""

import subprocess
import shutil
from typing import List, Optional
from exceptions.wireguard_exceptions import CommandNotFoundException, PermissionDeniedException


def find_command(command: str) -> str:
    """
    Find the full path to a command.
    
    Args:
        command: Command name to find
        
    Returns:
        Full path to the command
        
    Raises:
        CommandNotFoundException: If command is not found
    """
    # Try common paths first
    common_paths = ['/usr/bin', '/usr/sbin', '/bin', '/sbin']
    for path in common_paths:
        full_path = f"{path}/{command}"
        if shutil.which(full_path):
            return full_path
    
    # Fallback to shutil.which
    path = shutil.which(command)
    if path:
        return path
    
    raise CommandNotFoundException(command)


def run_command(
    command: List[str],
    input_data: Optional[bytes] = None,
    check: bool = True
) -> subprocess.CompletedProcess:
    """
    Run a system command with proper error handling.
    
    Args:
        command: Command and arguments as a list
        input_data: Optional input data to pass to command
        check: Whether to raise exception on non-zero exit
        
    Returns:
        CompletedProcess instance
        
    Raises:
        CommandNotFoundException: If command is not found
        PermissionDeniedException: If permission is denied
        subprocess.CalledProcessError: If command fails and check=True
    """
    try:
        # Resolve command to full path
        if command:
            command[0] = find_command(command[0])
        
        result = subprocess.run(
            command,
            input=input_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check
        )
        return result
        
    except FileNotFoundError:
        raise CommandNotFoundException(command[0] if command else "unknown")
    except PermissionError:
        raise PermissionDeniedException(f"executing {' '.join(command)}")
    except subprocess.CalledProcessError as e:
        # Check if it's a permission error in stderr
        if b'permission denied' in e.stderr.lower() or b'operation not permitted' in e.stderr.lower():
            raise PermissionDeniedException(f"executing {' '.join(command)}")
        raise
