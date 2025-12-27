
import time
import functools
from contextlib import contextmanager

class PerformanceTimer:
    """Context manager to measure execution time."""
    def __init__(self, name="Operation"):
        self.name = name
        self.start = 0
        self.end = 0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        elapsed = self.end - self.start
        if elapsed > 1.0:
            print(f"⚠️ [SLOW] {self.name} took {elapsed:.4f}s")
        else:
            print(f"⏱️ [FAST] {self.name} took {elapsed:.4f}s")

def measure_time(func):
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start
            if elapsed > 1.0:
                print(f"⚠️ [SLOW] {func.__name__} took {elapsed:.4f}s")
            else:
                print(f"⏱️ [FAST] {func.__name__} took {elapsed:.4f}s")
    return wrapper
