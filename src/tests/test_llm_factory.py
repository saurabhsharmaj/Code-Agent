"""
LLM Factory Tests
Unit tests for LLM factory pattern and configuration
"""

import pytest
from unittest.mock import Mock, patch
from src.llm.factory import LLMFactory, LLMConfig
from src.state.schemas import AgentState


class MockResponse:
    """Mock LLM response"""
    def __init__(self, content="{}"):
        self.content = content


class MockLLM:
    """Mock LLM for testing"""
    def __init__(self, response_content="{}"):
        self.response_content = response_content
        self.call_count = 0
        
    def invoke(self, prompt):
        self.call_count += 1
        return MockResponse(self.response_content)


@pytest.fixture
def clean_factory():
    """Fixture to clean factory state between tests"""
    LLMFactory.clear_cache()
    LLMFactory.set_test_mode(False)
    yield
    LLMFactory.clear_cache()
    LLMFactory.set_test_mode(False)


class TestLLMFactory:
    """Test LLM Factory functionality"""

    def test_factory_initialization(self, clean_factory):
        """Test factory initializes with default config"""
        factory = LLMFactory()
        config = factory.get_config()
        assert config is not None
        assert "planner" in config.model_config

    def test_get_specific_llms(self, clean_factory):
        """Test getting specific LLM instances"""
        planner_llm = LLMFactory.get_planner_llm()
        implementer_llm = LLMFactory.get_implementer_llm()
        reviewer_llm = LLMFactory.get_reviewer_llm()
        decision_llm = LLMFactory.get_decision_llm()
        
        assert planner_llm is not None
        assert implementer_llm is not None
        assert reviewer_llm is not None
        assert decision_llm is not None

    def test_llm_caching(self, clean_factory):
        """Test that LLM instances are cached"""
        llm1 = LLMFactory.get_planner_llm()
        llm2 = LLMFactory.get_planner_llm()
        
        # Should return same instance
        assert llm1 is llm2

    def test_generic_get_llm(self, clean_factory):
        """Test generic get_llm method"""
        planner_llm = LLMFactory.get_llm("planner")
        assert planner_llm is not None
        
        # Should be same as specific method
        specific_llm = LLMFactory.get_planner_llm()
        assert planner_llm is specific_llm

    def test_test_mode_with_mock(self, clean_factory):
        """Test enabling test mode with mock LLM"""
        mock_llm = MockLLM('{"test": "response"}')
        LLMFactory.set_test_mode(True, mock_llm)
        
        # All gets should return mock
        planner = LLMFactory.get_planner_llm()
        implementer = LLMFactory.get_implementer_llm()
        reviewer = LLMFactory.get_reviewer_llm()
        decision = LLMFactory.get_decision_llm()
        
        # All should be the same mock instance
        assert planner is mock_llm
        assert implementer is mock_llm
        assert reviewer is mock_llm
        assert decision is mock_llm

    def test_clear_cache(self, clean_factory):
        """Test clearing cache creates new instances"""
        llm1 = LLMFactory.get_planner_llm()
        LLMFactory.clear_cache()
        llm2 = LLMFactory.get_planner_llm()
        
        # Should be different instances
        assert llm1 is not llm2

    def test_update_model(self, clean_factory):
        """Test updating model configuration"""
        # Get initial config
        config = LLMFactory.get_config()
        original_model = config.model_config["planner"]["model"]
        
        # Update model
        new_model = "different-model"
        LLMFactory.update_model("planner", new_model)
        
        # Check config updated
        updated_config = LLMFactory.get_config()
        assert updated_config.model_config["planner"]["model"] == new_model
        
        # Cache should be cleared
        # (next call would create new LLM with new model)

    def test_invalid_agent_type(self, clean_factory):
        """Test error handling for invalid agent type"""
        with pytest.raises(ValueError):
            LLMFactory.get_llm("invalid_agent")


class TestLLMFactoryIntegration:
    """Integration tests with agent nodes"""

    def test_planner_node_with_factory(self, clean_factory):
        """Test planner node uses factory correctly"""
        from src.agents.planner.planner import planner_node
        
        # Setup mock
        mock_response = MockResponse('{"plan": "test", "strategy": "test", "app_name": "test", "image": "test:1.0", "replicas": 1}')
        mock_llm = MockLLM()
        mock_llm.invoke = Mock(return_value=mock_response)
        
        LLMFactory.set_test_mode(True, mock_llm)
        
        # Create test state
        state: AgentState = {
            "task": "Test task",
            "plan": "",
            "deployment_config": {},
            "deployment_yaml": "",
            "review": {},
            "decision": "",
            "retries": 0,
            "max_retries": 3,
            "errors": [],
            "final_output": None
        }
        
        # Run planner
        result = planner_node(state)
        
        # Verify
        assert result["plan"] == "test"
        assert mock_llm.call_count > 0

    def test_reviewer_node_with_factory(self, clean_factory):
        """Test reviewer node uses factory correctly"""
        from src.agents.reviewer.reviewer import review_node
        
        # Setup mock
        mock_response = MockResponse('{"score": 8, "issues": [], "recommendation": "approve", "strengths": ["good"], "improvements": []}')
        mock_llm = MockLLM()
        mock_llm.invoke = Mock(return_value=mock_response)
        
        LLMFactory.set_test_mode(True, mock_llm)
        
        # Create test state
        state: AgentState = {
            "task": "Test",
            "plan": "Test plan",
            "deployment_config": {},
            "deployment_yaml": "apiVersion: v1\nkind: Pod",
            "review": {},
            "decision": "",
            "retries": 0,
            "max_retries": 3,
            "errors": [],
            "final_output": None
        }
        
        # Run reviewer
        result = review_node(state)
        
        # Verify
        assert result["review"]["score"] == 8
        assert mock_llm.call_count > 0


class TestLLMFactoryConfiguration:
    """Test LLM configuration management"""

    def test_config_structure(self, clean_factory):
        """Test configuration structure"""
        config = LLMFactory.get_config()
        
        required_agents = ["planner", "implementer", "reviewer", "decision"]
        required_fields = ["model", "temperature", "max_tokens"]
        
        for agent in required_agents:
            assert agent in config.model_config
            for field in required_fields:
                assert field in config.model_config[agent]

    def test_config_values(self, clean_factory):
        """Test configuration values are reasonable"""
        config = LLMFactory.get_config()
        
        for agent, cfg in config.model_config.items():
            # Temperature should be between 0 and 1
            assert 0 <= cfg["temperature"] <= 1
            # Max tokens should be positive
            assert cfg["max_tokens"] > 0
            # Model should be a string
            assert isinstance(cfg["model"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
