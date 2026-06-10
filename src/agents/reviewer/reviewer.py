"""
Reviewer Agent
Validates and reviews K8s deployment YAML for best practices and issues
"""

from typing import Any, Dict
from langchain_core.prompts import PromptTemplate
from src.llm.factory import LLMFactory
from src.agents.base import BaseAgent
from src.prompts.registry import PromptRegistry
import json


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent: Validates and reviews K8s deployments.
    
    Analyzes deployment YAML for best practices, security, and production readiness.
    Provides scoring and recommendations for improvements.
    """
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute reviewer logic: Review K8s deployment.
        
        Args:
            state: Current workflow state with deployment_yaml
            
        Returns:
            Updated state with review results
        """
        try:
            if not state.get("deployment_yaml"):
                error_msg = "No deployment YAML generated"
                state.setdefault("errors", []).append(error_msg)
                return {
                    **state,
                    "review": {
                        "score": 0,
                        "issues": [error_msg],
                        "recommendation": "Cannot review empty deployment"
                    },
                }

            # Get LLM review
            reviewer_llm = LLMFactory.get_reviewer_llm()
            prompt_template = PromptRegistry.get("reviewer", "review")
            prompt = prompt_template.format(deployment_yaml=state["deployment_yaml"])
            response = reviewer_llm.invoke(prompt)

            # Parse response
            response_text = response.content.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            review_data = json.loads(response_text)

            return {
                **state,
                "review": review_data,
            }

        except json.JSONDecodeError as e:
            self._handle_error(e, "JSON parsing")
            error_msg = f"Failed to parse review response: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            return {
                **state,
                "review": {
                    "score": 5,
                    "issues": [error_msg],
                    "recommendation": "Review failed, retry recommended"
                },
            }
        except Exception as e:
            self._handle_error(e, "reviewer execution")
            error_msg = f"Review error: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            return {
                **state,
                "review": {
                    "score": 5,
                    "issues": [error_msg],
                    "recommendation": "Review failed"
                },
            }


# Backward compatibility: Keep review_node function
def review_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reviewer node function for backward compatibility.
    
    Delegates to ReviewerAgent instance.
    """
    agent = ReviewerAgent(name="reviewer")
    return agent(state)
