"""Utility functions for executing system commands."""

import subprocess
import shutil
import os
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
    check: bool = True,
    use_sudo: bool = False
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
        if command:
            # Auto-sudo for wg and wg-quick if not already present and not explicitly disabled
            # genkey and pubkey don't need sudo
            privileged_cmds = ['wg', 'wg-quick', 'systemctl']
            if command[0] in privileged_cmds and not use_sudo:
                if command[0] != 'wg' or (len(command) > 1 and command[1] not in ['genkey', 'pubkey']):
                    # Check if we are already root. If not, use sudo.
                    if os.geteuid() != 0:
                        use_sudo = True
            
            if use_sudo and command[0] != 'sudo':
                command = ['sudo'] + command
            
            # Resolve all command parts that look like binaries
            # If it's ['sudo', 'wg', ...], we want to resolve 'sudo' and 'wg'
            start_idx = 0
            if command[0] == 'sudo':
                 # Resolve sudo itself
                 command[0] = find_command('sudo')
                 start_idx = 1
            
            if len(command) > start_idx:
                command[start_idx] = find_command(command[start_idx])
        
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
