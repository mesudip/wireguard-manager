import os
import fcntl
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def acquire_read_lock(lock_path: str):
    """
    Context manager for a shared (read) lock using fcntl.
    Multiple read locks can be held concurrently, but will block if a write lock is active.
    """
    lock_file = f"{lock_path}.lock"
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    
    try:
        f = open(lock_file, 'a+')
        try:
            # LOCK_SH: Shared lock - multiple readers can hold this simultaneously
            fcntl.flock(f, fcntl.LOCK_SH)
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
    except Exception as e:
        logger.error(f"Error acquiring read lock on {lock_file}: {e}")
        raise

@contextmanager
def acquire_write_lock(lock_path: str):
    """
    Context manager for an exclusive (write) lock using fcntl.
    Only one write lock can be held at a time, and it blocks all read locks.
    """
    lock_file = f"{lock_path}.lock"
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    
    try:
        f = open(lock_file, 'a+')
        try:
            # LOCK_EX: Exclusive lock - only one holder at a time
            fcntl.flock(f, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
    except Exception as e:
        logger.error(f"Error acquiring write lock on {lock_file}: {e}")
        raise

@contextmanager
def file_lock(lock_path: str, timeout: int = 10):
    """
    Context manager for a simple cross-process file lock using fcntl.
    Deprecated: Use acquire_write_lock() or acquire_read_lock() instead.
    """
    with acquire_write_lock(lock_path):
        yield
