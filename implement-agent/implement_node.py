"""
Implement Agent Node
Generates K8s deployment YAML files based on the plan
"""

from langchain_groq import ChatGroq
from common.k8s_generator import K8sDeploymentGenerator
import json

coder_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=1500
)


def implement_node(state):
    """
    Implement node: Generates K8s deployment files
    
    Args:
        state: Current agent state with deployment_config
        
    Returns:
        Updated state with deployment_yaml
    """
    try:
        if not state.get("deployment_config"):
            return {
                "deployment_yaml": "",
                "errors": state.get("errors", []) + ["No deployment config provided"]
            }
        
        config = state["deployment_config"]
        
        # Validate configuration
        generator = K8sDeploymentGenerator()
        is_valid, validation_errors = generator.validate_deployment_config(config)
        
        if not is_valid:
            return {
                "deployment_yaml": "",
                "errors": state.get("errors", []) + validation_errors
            }
        
        # Generate deployment YAML
        deployment_yaml = generator.generate_basic_deployment(
            app_name=config.get("app_name", "app"),
            image=config.get("image", "app:latest"),
            replicas=config.get("replicas", 3),
            port=config.get("port", 8080),
            env_vars=config.get("env_vars"),
            resource_limits=config.get("resources"),
            namespace=config.get("namespace", "default")
        )
        
        # Generate additional manifests
        service_yaml = generator.generate_service(
            app_name=config.get("app_name", "app"),
            port=config.get("port", 8080),
            namespace=config.get("namespace", "default")
        )
        
        hpa_yaml = generator.generate_hpa(
            app_name=config.get("app_name", "app"),
            namespace=config.get("namespace", "default")
        )
        
        # Combine all manifests with separators
        combined_yaml = f"""---
# Deployment Manifest
{deployment_yaml}---
# Service Manifest
{service_yaml}---
# Horizontal Pod Autoscaler
{hpa_yaml}"""
        
        return {
            "deployment_yaml": combined_yaml,
            "errors": []
        }
        
    except Exception as e:
        error_msg = f"Implementation error: {str(e)}"
        return {
            "deployment_yaml": "",
            "errors": state.get("errors", []) + [error_msg]
        }
