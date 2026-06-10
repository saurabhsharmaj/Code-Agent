"""
Implementer Agent
Generates K8s deployment YAML files based on the plan
"""

from typing import Any, Dict
from src.llm.factory import LLMFactory
from src.tools.kubernetes.k8s_generator import K8sDeploymentGenerator
from src.agents.base import BaseAgent
import json


class ImplementerAgent(BaseAgent):
    """
    Implementer Agent: Generates Kubernetes deployment files.
    
    Takes a deployment plan and generates valid K8s manifests
    including Deployment, Service, and HPA resources.
    """
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute implementer logic: Generate K8s deployment YAML.
        
        Args:
            state: Current workflow state with deployment_config
            
        Returns:
            Updated state with deployment_yaml
        """
        try:
            if not state.get("deployment_config"):
                error_msg = "No deployment config provided"
                state.setdefault("errors", []).append(error_msg)
                return {
                    **state,
                    "deployment_yaml": "",
                }

            config = state["deployment_config"]

            # Validate configuration
            generator = K8sDeploymentGenerator()
            is_valid, validation_errors = generator.validate_deployment_config(config)

            if not is_valid:
                state.setdefault("errors", []).extend(validation_errors)
                return {
                    **state,
                    "deployment_yaml": "",
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
                **state,
                "deployment_yaml": combined_yaml,
            }

        except Exception as e:
            self._handle_error(e, "implementer execution")
            error_msg = f"Implementation error: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            return {
                **state,
                "deployment_yaml": "",
            }


# Backward compatibility: Keep implement_node function
def implement_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Implementer node function for backward compatibility.
    
    Delegates to ImplementerAgent instance.
    """
    agent = ImplementerAgent(name="implementer")
    return agent(state)
