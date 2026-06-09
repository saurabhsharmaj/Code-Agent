"""
Decision Agent Node
Makes decisions on whether to approve deployment or retry based on review score
"""

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import json

decision_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=1000
)

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


def decision_node(state):
    """
    Decision node: Makes approval/retry decisions based on review
    
    Args:
        state: Current agent state with review data
        
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
            
            return {
                "decision": decision,
                "errors": state.get("errors", []) + [f"Max retries ({max_retries}) reached"]
            }
        
        # Get LLM decision
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
            "decision": final_decision,
            "decision_reasoning": reasoning,
            "suggested_fixes": decision_data.get("suggested_fixes", []),
            "errors": []
        }
        
    except Exception as e:
        # On decision error, lean towards retry if retries available
        error_msg = f"Decision error: {str(e)}"
        if state.get("retries", 0) < state.get("max_retries", 3):
            return {
                "decision": "retry",
                "errors": state.get("errors", []) + [error_msg]
            }
        else:
            return {
                "decision": "approve",
                "errors": state.get("errors", []) + [error_msg]
            }
