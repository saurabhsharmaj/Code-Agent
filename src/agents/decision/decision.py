"""
Decision Agent
Makes decisions on whether to approve deployment or retry based on review score
"""

from typing import Any, Dict
from langchain_core.prompts import PromptTemplate
from src.llm.factory import LLMFactory
from src.agents.base import BaseAgent
import json

DECISION_PROMPT = PromptTemplate(
    input_variables=["review", "retries", "max_retries"],
    template="""You are a deployment decision maker. Based on the review score and retry count, decide whether to approve or retry.

Review Data:
{review}

Retry Status: {retries}/{max_retries}

Rules:
1. If score >= 8: Recommend "approve"
2. If score >= 6 and retries < max_retries: Consider "retry" with specific improvements
3. If score < 6 and retries < max_retries: Recommend "retry" with fixes
4. If max_retries reached: Recommend "approve_with_warnings" or "reject" based on score

Provide JSON response:
{{
    "decision": "approve|retry|approve_with_warnings|reject",
    "reasoning": "Your decision reasoning",
    "suggested_fixes": ["fix 1", "fix 2"],
    "can_retry": true|false
}}"""
)


class DecisionAgent(BaseAgent):
    """
    Decision Agent: Makes approval/retry decisions based on reviews.
    
    Evaluates review scores and retry count to determine whether to approve,
    reject, or request modifications to the deployment.
    """
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute decision logic: Approve or retry deployment.
        
        Args:
            state: Current workflow state with review data
            
        Returns:
            Updated state with decision
        """
        try:
            review = state.get("review", {})
            score = review.get("score", 0)
            retries = state.get("retries", 0)
            max_retries = state.get("max_retries", 3)

            # Check if max retries reached
            if retries >= max_retries:
                if score >= 6:
                    decision = "approve"
                else:
                    decision = "reject"

                error_msg = f"Max retries ({max_retries}) reached"
                state.setdefault("errors", []).append(error_msg)
                return {
                    **state,
                    "decision": decision,
                }

            # Get LLM decision
            decision_llm = LLMFactory.get_decision_llm()
            review_json = json.dumps(review, indent=2)
            prompt = DECISION_PROMPT.format(
                review=review_json,
                retries=retries,
                max_retries=max_retries
            )

            response = decision_llm.invoke(prompt)
            response_text = response.content.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()
            decision_data = json.loads(response_text)

            decision = decision_data.get("decision", "retry").lower()
            reasoning = decision_data.get("reasoning", "")

            # Map decision to our flow
            if decision == "approve":
                final_decision = "approve"
            elif decision == "reject":
                final_decision = "reject"
            else:  # retry, approve_with_warnings, etc
                final_decision = "retry"

            return {
                **state,
                "decision": final_decision,
            }

        except json.JSONDecodeError as e:
            self._handle_error(e, "JSON parsing")
            error_msg = f"Failed to parse decision response: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            return {
                **state,
                "decision": "retry",
            }
        except Exception as e:
            self._handle_error(e, "decision execution")
            error_msg = f"Decision error: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            return {
                **state,
                "decision": "retry",
            }


# Backward compatibility: Keep decision_node function
def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decision node function for backward compatibility.
    
    Delegates to DecisionAgent instance.
    """
    agent = DecisionAgent(name="decision")
    return agent(state)
