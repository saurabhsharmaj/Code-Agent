"""
Planner Agent
Analyzes requirements and creates a plan for K8s deployment generation
"""

from typing import Any, Dict
from langchain_core.prompts import PromptTemplate
from src.llm.factory import LLMFactory
from src.agents.base import BaseAgent
from src.prompts.registry import PromptRegistry
import json


class PlannerAgent(BaseAgent):
    """
    Planner Agent: Creates deployment strategy using LLM.
    
    Analyzes user requirements and generates a detailed deployment plan
    with configuration recommendations.
    """
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute planner logic: Generate deployment strategy.
        
        Args:
            state: Current workflow state with task
            
        Returns:
            Updated state with plan and deployment_config
        """
        try:
            # Get LLM from factory
            planner_llm = LLMFactory.get_planner_llm()
            
            # Load prompt from registry and format it
            prompt_template = PromptRegistry.get("planner", "strategy")
            prompt = prompt_template.format(task=state["task"])
            response = planner_llm.invoke(prompt)

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

            deployment_config = json.loads(response_text)
            plan = deployment_config.get("strategy", "No strategy provided")

            return {
                **state,
                "plan": plan,
                "deployment_config": deployment_config,
            }

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse planner response: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            return {
                **state,
                "plan": "Error: Failed to create plan",
                "deployment_config": {},
            }
        except Exception as e:
            self._handle_error(e, "planner execution")
            error_msg = f"Planner error: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            return {
                **state,
                "plan": "Error: Planner failed",
                "deployment_config": {},
            }


# Backward compatibility: Keep planner_node function
def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Planner node function for backward compatibility.
    
    Delegates to PlannerAgent instance.
    """
    agent = PlannerAgent(name="planner")
    return agent(state)
