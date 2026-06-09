"""
Planner Agent Node
Analyzes requirements and creates a plan for K8s deployment generation
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import json

planner_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    max_tokens=2000
)

PLANNER_PROMPT = PromptTemplate(
    input_variables=["task"],
    template="""You are a Kubernetes deployment planner. Analyze the user's request and create a detailed plan.

User Request:
{task}

Provide a JSON response with the following structure:
{{
    "strategy": "Your detailed strategy for creating the K8s deployment",
    "app_name": "Proposed application name",
    "image": "Docker image to use (with tag)",
    "replicas": 3,
    "port": 8080,
    "namespace": "default",
    "env_vars": {{"KEY": "VALUE"}},
    "resources": {{
        "requests": {{"cpu": "100m", "memory": "128Mi"}},
        "limits": {{"cpu": "500m", "memory": "512Mi"}}
    }},
    "considerations": ["key consideration 1", "key consideration 2"]
}}

IMPORTANT: Return ONLY valid JSON, no markdown formatting or code blocks."""
)


def planner_node(state):
    """
    Planner node: Creates deployment strategy using Groq LLM
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with plan and deployment_config
    """
    try:
        # Generate plan from user task
        prompt = PLANNER_PROMPT.format(task=state["task"])
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
            "plan": plan,
            "deployment_config": deployment_config,
            "errors": []
        }
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse planner response: {str(e)}"
        return {
            "plan": "Error: Failed to create plan",
            "deployment_config": {},
            "errors": [error_msg],
            "decision": "retry"
        }
    except Exception as e:
        error_msg = f"Planner error: {str(e)}"
        return {
            "plan": "Error: Planner failed",
            "deployment_config": {},
            "errors": [error_msg],
            "decision": "retry"
        }
