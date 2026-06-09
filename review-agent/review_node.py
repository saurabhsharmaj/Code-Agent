"""
Review Agent Node
Validates and reviews K8s deployment YAML for best practices and issues
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from common.reviewoutput import ReviewOutput
import json

reviewer_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    max_tokens=2000
)

REVIEW_PROMPT = PromptTemplate(
    input_variables=["deployment_yaml"],
    template="""You are a Kubernetes expert reviewer. Analyze the provided K8s deployment YAML for:
1. Best practices compliance
2. Security considerations
3. Resource optimization
4. High availability setup
5. Production readiness

Deployment YAML:
{deployment_yaml}

Provide a JSON response with:
{{
    "score": 0-10,
    "issues": ["issue 1", "issue 2"],
    "recommendation": "Your recommendation",
    "strengths": ["strength 1", "strength 2"],
    "improvements": ["improvement 1", "improvement 2"]
}}

IMPORTANT: Return ONLY valid JSON, no markdown formatting."""
)


def review_node(state):
    """
    Review node: Validates K8s deployment using Groq LLM
    
    Args:
        state: Current agent state with deployment_yaml
        
    Returns:
        Updated state with review results
    """
    try:
        if not state.get("deployment_yaml"):
            return {
                "review": {
                    "score": 0,
                    "issues": ["No deployment YAML generated"],
                    "recommendation": "Cannot review empty deployment"
                },
                "decision": "retry"
            }
        
        # Get LLM review
        prompt = REVIEW_PROMPT.format(deployment_yaml=state["deployment_yaml"])
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
            "review": review_data,
            "errors": []
        }
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse review response: {str(e)}"
        return {
            "review": {
                "score": 5,
                "issues": [error_msg],
                "recommendation": "Review failed, retry recommended"
            },
            "errors": [error_msg]
        }
    except Exception as e:
        error_msg = f"Review error: {str(e)}"
        return {
            "review": {
                "score": 0,
                "issues": [error_msg],
                "recommendation": "Review failed"
            },
            "errors": [error_msg]
        }
