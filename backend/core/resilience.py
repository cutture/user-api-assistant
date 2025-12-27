
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .exceptions import LLMError, ServiceUnavailableError, AppError

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failures = 0
        self.threshold = failure_threshold
        self.last_failure_time = 0
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.threshold:
            self.state = "OPEN"
            print(f"🔥 Circuit Breaker OPENed! Too many failures.")

    def record_success(self):
        if self.failures > 0:
            print("✅ Circuit Breaker Recovered.")
        self.failures = 0
        self.state = "CLOSED"

    def check(self):
        if self.state == "OPEN":
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.recovery_timeout:
                self.state = "HALF-OPEN" # Allow one trial
            else:
                raise ServiceUnavailableError(f"Service unavailable by Circuit Breaker. Retry in {int(self.recovery_timeout - elapsed)}s.")

# Singleton
global_circuit_breaker = CircuitBreaker()

def with_resilience(max_retries=3):
    """
    Decorator that adds:
    1. Circuit Breaker Check
    2. Retries with Exponential Backoff
    """
    def decorator(func):
        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            reraise=True
        )
        def wrapper(*args, **kwargs):
            global_circuit_breaker.check()
            try:
                result = func(*args, **kwargs)
                global_circuit_breaker.record_success()
                return result
            except Exception as e:
                # If we are in HALF-OPEN and fail, go back to OPEN immediately?
                # For now, just record failure
                if not isinstance(e, ServiceUnavailableError):
                    global_circuit_breaker.record_failure()
                raise e
        return wrapper
    return decorator
