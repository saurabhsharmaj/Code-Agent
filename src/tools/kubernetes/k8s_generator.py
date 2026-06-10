"""
Kubernetes Deployment File Generator
Utilities for generating and validating K8s deployment YAML files
"""

import yaml
from typing import Dict, Any, Optional
from datetime import datetime


class K8sDeploymentGenerator:
    """Generate valid Kubernetes deployment manifests"""

    @staticmethod
    def generate_basic_deployment(
        app_name: str,
        image: str,
        replicas: int = 3,
        port: int = 8080,
        env_vars: Optional[Dict[str, str]] = None,
        resource_limits: Optional[Dict[str, Any]] = None,
        namespace: str = "default"
    ) -> str:
        """
        Generate a basic K8s deployment YAML

        Args:
            app_name: Application name
            image: Docker image URI
            replicas: Number of replicas
            port: Container port
            env_vars: Environment variables
            resource_limits: CPU/Memory limits and requests
            namespace: K8s namespace

        Returns:
            YAML string of the deployment
        """

        if resource_limits is None:
            resource_limits = {
                "requests": {"cpu": "100m", "memory": "128Mi"},
                "limits": {"cpu": "500m", "memory": "512Mi"}
            }

        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": app_name,
                "namespace": namespace,
                "labels": {
                    "app": app_name,
                    "managed-by": "ai-agent",
                    "created": datetime.now().isoformat()
                }
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": app_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": app_name,
                            "version": "v1"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": app_name,
                                "image": image,
                                "imagePullPolicy": "IfNotPresent",
                                "ports": [
                                    {
                                        "containerPort": port,
                                        "name": "http"
                                    }
                                ],
                                "resources": resource_limits,
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": port
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": port
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5
                                }
                            }
                        ]
                    }
                }
            }
        }

        if env_vars:
            deployment["spec"]["template"]["spec"]["containers"][0]["env"] = [
                {"name": k, "value": v} for k, v in env_vars.items()
            ]

        return yaml.dump(deployment, default_flow_style=False, sort_keys=False)

    @staticmethod
    def generate_service(
        app_name: str,
        port: int = 8080,
        service_type: str = "ClusterIP",
        namespace: str = "default"
    ) -> str:
        """Generate a K8s Service manifest"""

        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{app_name}-svc",
                "namespace": namespace,
                "labels": {
                    "app": app_name
                }
            },
            "spec": {
                "type": service_type,
                "selector": {
                    "app": app_name
                },
                "ports": [
                    {
                        "port": port,
                        "targetPort": port,
                        "protocol": "TCP",
                        "name": "http"
                    }
                ]
            }
        }

        return yaml.dump(service, default_flow_style=False, sort_keys=False)

    @staticmethod
    def generate_hpa(
        app_name: str,
        min_replicas: int = 2,
        max_replicas: int = 10,
        target_cpu_percent: int = 70,
        namespace: str = "default"
    ) -> str:
        """Generate a Horizontal Pod Autoscaler manifest"""

        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{app_name}-hpa",
                "namespace": namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": app_name
                },
                "minReplicas": min_replicas,
                "maxReplicas": max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": target_cpu_percent
                            }
                        }
                    }
                ]
            }
        }

        return yaml.dump(hpa, default_flow_style=False, sort_keys=False)

    @staticmethod
    def validate_deployment_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate deployment configuration

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Check required fields
        if not config.get("app_name"):
            errors.append("app_name is required")
        if not config.get("image"):
            errors.append("image is required")
        if not config.get("replicas"):
            errors.append("replicas is required and must be > 0")
        elif config["replicas"] < 1:
            errors.append("replicas must be at least 1")

        # Validate image format (basic)
        image = config.get("image", "")
        if image and ":" not in image:
            errors.append("image should include tag (e.g., app:v1.0)")

        return len(errors) == 0, errors
