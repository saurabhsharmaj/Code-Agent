"""
Test and demonstration of the BaseAgent class and all agent implementations
"""

import sys
import os
from typing import Dict, Any

# Add test API key for imports
os.environ.setdefault("GROQ_API_KEY", "test_key_for_testing")

from src.agents import (
    BaseAgent,
    StatefulAgent,
    ComposableAgent,
    PlannerAgent,
    ImplementerAgent,
    ReviewerAgent,
    DecisionAgent,
    ReporterAgent,
    ExecutionMetrics,
    planner_node,
    implement_node,
    review_node,
    decision_node,
    report_node,
)


def test_base_agent_exists():
    """Test that BaseAgent is abstract and cannot be instantiated"""
    print("\n✅ Test: BaseAgent is abstract")
    try:
        agent = BaseAgent(name="test")
        print("❌ FAILED: BaseAgent should be abstract")
        return False
    except TypeError as e:
        print("✅ PASSED: Cannot instantiate abstract BaseAgent")
        return True


def test_execution_metrics():
    """Test ExecutionMetrics dataclass"""
    print("\n✅ Test: ExecutionMetrics dataclass")
    metrics = ExecutionMetrics(
        execution_time=1.5,
        tokens_used=100,
        api_calls=2,
        agent_name="test",
        status="success"
    )
    
    metrics_dict = metrics.to_dict()
    assert metrics_dict["agent_name"] == "test"
    assert metrics_dict["status"] == "success"
    assert metrics_dict["execution_time"] == 1.5
    print("✅ PASSED: ExecutionMetrics works correctly")
    return True


def test_planner_agent_initialization():
    """Test PlannerAgent initialization"""
    print("\n✅ Test: PlannerAgent initialization")
    agent = PlannerAgent(name="planner", max_retries=3)
    
    assert agent.name == "planner"
    assert agent.max_retries == 3
    assert agent.metrics.agent_name == "planner"
    assert agent.metrics.status == "pending"
    print("✅ PASSED: PlannerAgent initializes correctly")
    return True


def test_implementer_agent_initialization():
    """Test ImplementerAgent initialization"""
    print("\n✅ Test: ImplementerAgent initialization")
    agent = ImplementerAgent(name="implementer", max_retries=2)
    
    assert agent.name == "implementer"
    assert agent.max_retries == 2
    print("✅ PASSED: ImplementerAgent initializes correctly")
    return True


def test_reviewer_agent_initialization():
    """Test ReviewerAgent initialization"""
    print("\n✅ Test: ReviewerAgent initialization")
    agent = ReviewerAgent(name="reviewer")
    
    assert agent.name == "reviewer"
    assert agent.max_retries == 3  # default
    print("✅ PASSED: ReviewerAgent initializes correctly")
    return True


def test_decision_agent_initialization():
    """Test DecisionAgent initialization"""
    print("\n✅ Test: DecisionAgent initialization")
    agent = DecisionAgent(name="decision")
    
    assert agent.name == "decision"
    print("✅ PASSED: DecisionAgent initializes correctly")
    return True


def test_reporter_agent_initialization():
    """Test ReporterAgent initialization"""
    print("\n✅ Test: ReporterAgent initialization")
    agent = ReporterAgent(name="reporter")
    
    assert agent.name == "reporter"
    print("✅ PASSED: ReporterAgent initializes correctly")
    return True


def test_stateful_agent():
    """Test StatefulAgent functionality"""
    print("\n✅ Test: StatefulAgent state tracking")
    
    class TestStatefulAgent(StatefulAgent):
        def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
            return {**state, "result": "test"}
    
    agent = TestStatefulAgent(name="stateful")
    state = {"input": "test"}
    
    # First execution
    result1 = agent.execute(state)
    agent._record_result(result1)
    
    # Second execution
    result2 = agent.execute(state)
    agent._record_result(result2)
    
    # Check history
    history = agent.get_history()
    assert len(history) == 2
    assert agent.get_last_result() == result2
    
    print("✅ PASSED: StatefulAgent tracks state correctly")
    return True


def test_composable_agent():
    """Test ComposableAgent functionality"""
    print("\n✅ Test: ComposableAgent composition")
    
    class SimpleAgent(BaseAgent):
        def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
            return {**state, f"executed_{self.name}": True}
    
    class MainAgent(ComposableAgent):
        def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
            state = self.execute_sub_agent("sub1", state)
            state = self.execute_sub_agent("sub2", state)
            return state
    
    agent = MainAgent(name="main")
    agent.add_sub_agent("sub1", SimpleAgent(name="sub1"))
    agent.add_sub_agent("sub2", SimpleAgent(name="sub2"))
    
    state = {"input": "test"}
    result = agent(state)
    
    assert "executed_sub1" in result
    assert "executed_sub2" in result
    
    sub_agents = agent.get_sub_agents()
    assert len(sub_agents) == 2
    
    print("✅ PASSED: ComposableAgent composes sub-agents correctly")
    return True


def test_backward_compatibility():
    """Test backward compatibility with node functions"""
    print("\n✅ Test: Backward compatibility with node functions")
    
    # All node functions should be callable
    assert callable(planner_node)
    assert callable(implement_node)
    assert callable(review_node)
    assert callable(decision_node)
    assert callable(report_node)
    
    print("✅ PASSED: All node functions are callable")
    return True


def test_agent_callable_interface():
    """Test that agents are callable via __call__"""
    print("\n✅ Test: Agent callable interface")
    
    class TestAgent(BaseAgent):
        def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
            return {**state, "processed": True}
    
    agent = TestAgent(name="test")
    
    # Test __call__ interface
    state = {"input": "test"}
    result = agent(state)  # Should work via __call__
    
    assert "processed" in result
    assert result["processed"] is True
    
    # Check metrics were recorded
    metrics = agent.record_metrics()
    assert metrics["status"] == "success"
    
    print("✅ PASSED: Agent callable interface works correctly")
    return True


def test_agent_validation():
    """Test agent result validation"""
    print("\n✅ Test: Agent result validation")
    
    class ValidatingAgent(BaseAgent):
        def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
            return {**state, "valid": True}
        
        def validate(self, result: Dict[str, Any]) -> bool:
            # Only accept results with 'valid' key
            return "valid" in result
    
    agent = ValidatingAgent(name="validator")
    state = {"input": "test"}
    result = agent(state)
    
    assert result["valid"] is True
    
    print("✅ PASSED: Agent validation works correctly")
    return True


def test_metrics_tracking():
    """Test automatic metrics tracking"""
    print("\n✅ Test: Automatic metrics tracking")
    
    class MetricsAgent(BaseAgent):
        def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
            # Simulate some work
            self.metrics.api_calls += 1
            self.metrics.tokens_used += 50
            return state
    
    agent = MetricsAgent(name="metrics-test")
    state = {}
    result = agent(state)
    
    metrics = agent.record_metrics()
    assert metrics["status"] == "success"
    assert metrics["api_calls"] == 1
    assert metrics["tokens_used"] == 50
    assert metrics["agent_name"] == "metrics-test"
    
    print("✅ PASSED: Metrics tracking works correctly")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("BASE AGENT CLASS TESTS")
    print("="*60)
    
    tests = [
        test_base_agent_exists,
        test_execution_metrics,
        test_planner_agent_initialization,
        test_implementer_agent_initialization,
        test_reviewer_agent_initialization,
        test_decision_agent_initialization,
        test_reporter_agent_initialization,
        test_stateful_agent,
        test_composable_agent,
        test_backward_compatibility,
        test_agent_callable_interface,
        test_agent_validation,
        test_metrics_tracking,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ FAILED: {test.__name__}")
            print(f"   Error: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
