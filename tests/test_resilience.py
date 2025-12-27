
import pytest
from tenacity import RetryError
from backend.core.resilience import with_resilience, global_circuit_breaker
from backend.core.exceptions import AppError, ServiceUnavailableError

# Mock LLM
class MockLLM:
    def invoke(self, messages):
        raise ValueError("LLM Failure")

class GoodLLM:
    def invoke(self, messages):
        return "Success"

def test_retry_logic():
    # Test that it retries 3 times then fails
    # We can't easily count retries without a spy, but we can verify it eventually raises RetryError (from tenacity) or the exception
    # tenacity with reraise=True raises the underlying exception
    
    mock = MockLLM()
    
    @with_resilience(max_retries=2)
    def call_llm():
        return mock.invoke([])
        
    global_circuit_breaker.failures = 0
    global_circuit_breaker.state = "CLOSED"
        
    with pytest.raises(ValueError):
        call_llm()
        
    assert global_circuit_breaker.failures > 0

def test_circuit_breaker_open():
    global_circuit_breaker.failures = 3 # Threshold
    global_circuit_breaker.state = "OPEN"
    global_circuit_breaker.last_failure_time = 9999999999 # Future
    
    @with_resilience(max_retries=1)
    def call_llm():
        pass
        
    with pytest.raises(ServiceUnavailableError):
        call_llm()

def test_circuit_breaker_recovery():
    global_circuit_breaker.failures = 3
    global_circuit_breaker.state = "OPEN"
    global_circuit_breaker.last_failure_time = 0 # Past
    global_circuit_breaker.recovery_timeout = 0
    
    result = "Initial"
    
    @with_resilience(max_retries=1)
    def call_llm():
        return "Recovered"
        
    result = call_llm()
    assert result == "Recovered"
    assert global_circuit_breaker.state == "CLOSED"
