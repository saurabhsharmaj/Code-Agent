"""
Risk Assessment Module
Evaluates deployment risk and determines if human approval is needed
"""

from typing import Dict, Any
import re


class RiskAssessor:
    """
    Analyzes deployment configurations and YAML for risk factors.
    
    Risk Factors:
    - Production namespace
    - High replica count
    - Resource limits
    - Security settings
    - Review score
    """
    
    # Risk thresholds
    RISK_THRESHOLD = 6  # Score >= 6 requires human approval
    REVIEW_THRESHOLD = 8  # Review score < 8 may need review
    
    @classmethod
    def assess_risk(cls, state: Dict[str, Any]) -> int:
        """
        Calculate overall risk score (0-10).
        
        Args:
            state: Current agent state
            
        Returns:
            Risk score 0-10
        """
        risk_score = 0
        
        config = state.get("deployment_config", {})
        yaml_content = state.get("deployment_yaml", "")
        review = state.get("review", {})
        
        # Factor 1: Namespace (production = higher risk)
        namespace = config.get("namespace", "default").lower()
        if namespace == "production":
            risk_score += 3
        elif namespace in ["prod", "main", "live"]:
            risk_score += 2
        
        # Factor 2: Replica count (more replicas = more critical infrastructure)
        replicas = config.get("replicas", 1)
        if replicas >= 5:
            risk_score += 2
        elif replicas >= 3:
            risk_score += 1
        
        # Factor 3: Resource limits (no limits = risky)
        resources = config.get("resources", {})
        limits = resources.get("limits", {})
        
        if not limits or not limits.get("cpu") or not limits.get("memory"):
            risk_score += 2
        
        # Factor 4: Security concerns from review
        review_issues = review.get("issues", [])
        security_keywords = ["security", "exposed", "vulnerability", "secret", "auth"]
        security_issues = sum(
            1 for issue in review_issues 
            if any(keyword in issue.lower() for keyword in security_keywords)
        )
        if security_issues > 0:
            risk_score += security_issues
        
        # Factor 5: Low review score (< 6 is risky)
        review_score = review.get("score", 5)
        if review_score < 6:
            risk_score += 2
        elif review_score < 8:
            risk_score += 1
        
        # Factor 6: Production deployment with auto-scaling
        is_production = namespace == "production"
        has_autoscaling = "HorizontalPodAutoscaler" in yaml_content
        
        if is_production and has_autoscaling:
            risk_score += 1
        
        # Factor 7: No liveness/readiness probes
        has_probes = "livenessProbe" in yaml_content and "readinessProbe" in yaml_content
        if not has_probes:
            risk_score += 1
        
        # Cap at 10
        return min(risk_score, 10)
    
    @classmethod
    def should_require_human_approval(cls, state: Dict[str, Any]) -> bool:
        """
        Determine if human approval is required.
        
        Returns True if:
        - Risk score > RISK_THRESHOLD
        - Review score < REVIEW_THRESHOLD
        - Deployment to production
        - Low review score despite high replicas
        
        Args:
            state: Current agent state
            
        Returns:
            True if human approval needed
        """
        risk_score = cls.assess_risk(state)
        review = state.get("review", {})
        review_score = review.get("score", 5)
        config = state.get("deployment_config", {})
        namespace = config.get("namespace", "default").lower()
        
        # Always require approval for high-risk deployments
        if risk_score >= cls.RISK_THRESHOLD:
            return True
        
        # Always require approval for production with low review score
        if namespace == "production" and review_score < cls.REVIEW_THRESHOLD:
            return True
        
        # Require approval if review score is below threshold
        if review_score < cls.REVIEW_THRESHOLD and risk_score >= 5:
            return True
        
        return False
    
    @classmethod
    def get_risk_factors(cls, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed risk factors breakdown.
        
        Returns:
            Dictionary with risk factors and reasoning
        """
        config = state.get("deployment_config", {})
        yaml_content = state.get("deployment_yaml", "")
        review = state.get("review", {})
        risk_score = cls.assess_risk(state)
        
        namespace = config.get("namespace", "default").lower()
        replicas = config.get("replicas", 1)
        review_score = review.get("score", 5)
        resources = config.get("resources", {})
        limits = resources.get("limits", {})
        
        factors = {
            "risk_score": risk_score,
            "review_score": review_score,
            "requires_approval": cls.should_require_human_approval(state),
            "factors": {
                "namespace": {
                    "value": namespace,
                    "risk": 3 if namespace == "production" else (2 if namespace in ["prod", "main", "live"] else 0),
                    "reason": f"Deploying to {namespace} namespace"
                },
                "replicas": {
                    "value": replicas,
                    "risk": (2 if replicas >= 5 else (1 if replicas >= 3 else 0)),
                    "reason": f"{replicas} replicas affects multiple instances"
                },
                "resource_limits": {
                    "value": bool(limits),
                    "risk": 0 if limits and limits.get("cpu") and limits.get("memory") else 2,
                    "reason": "No resource limits defined" if not limits else "Resource limits configured"
                },
                "review_score": {
                    "value": review_score,
                    "risk": (2 if review_score < 6 else (1 if review_score < 8 else 0)),
                    "reason": f"Review score {review_score}/10"
                },
                "probes": {
                    "value": "livenessProbe" in yaml_content and "readinessProbe" in yaml_content,
                    "risk": 1 if not ("livenessProbe" in yaml_content and "readinessProbe" in yaml_content) else 0,
                    "reason": "Health probes configured" if ("livenessProbe" in yaml_content and "readinessProbe" in yaml_content) else "Missing health probes"
                }
            }
        }
        
        return factors
