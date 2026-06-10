"""
Human Approval Agent
Implements the human approval gate for critical deployments
"""

from typing import Any, Dict, Optional
from src.agents.base import BaseAgent
from src.tools.risk_assessment import RiskAssessor


class HumanApprovalAgent(BaseAgent):
    """
    Human Approval Gate: Routes critical deployments for human review.
    
    Responsibilities:
    - Assess deployment risk
    - Flag deployments that need human approval
    - Collect human approval/rejection
    - Add human notes to deployment record
    
    Risk Factors:
    - Production namespace
    - High replica count
    - Missing resource limits
    - Low review score
    - Security concerns
    """
    
    def __init__(self, name: str = "human_approval", auto_approve_low_risk: bool = False):
        """
        Initialize Human Approval Agent.
        
        Args:
            name: Agent name
            auto_approve_low_risk: If True, auto-approve deployments below risk threshold
        """
        super().__init__(name)
        self.auto_approve_low_risk = auto_approve_low_risk
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute human approval logic.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with risk and approval information
        """
        try:
            # Assess deployment risk
            risk_score = RiskAssessor.assess_risk(state)
            requires_approval = RiskAssessor.should_require_human_approval(state)
            risk_factors = RiskAssessor.get_risk_factors(state)
            
            # Update state with risk information
            state["risk_score"] = risk_score
            state["requires_human_approval"] = requires_approval
            
            if requires_approval:
                # High-risk deployment - require human approval
                state = self._handle_high_risk_deployment(state, risk_factors)
            else:
                # Low-risk deployment - auto-approve if configured
                if self.auto_approve_low_risk:
                    state["human_approval"] = "auto_approved"
                    state["human_notes"] = "Auto-approved (low risk deployment)"
                else:
                    state["human_approval"] = "pending"
                    state["human_notes"] = "Awaiting human review"
            
            return state
            
        except Exception as e:
            self._handle_error(e, "human approval execution")
            error_msg = f"Human approval error: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            
            # On error, mark as requiring manual review
            state["requires_human_approval"] = True
            state["human_approval"] = "pending"
            state["human_notes"] = f"Review required due to error: {str(e)}"
            
            return state
    
    def _handle_high_risk_deployment(self, state: Dict[str, Any], risk_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle high-risk deployment requiring human approval.
        
        Args:
            state: Current workflow state
            risk_factors: Risk assessment details
            
        Returns:
            Updated state
        """
        risk_score = risk_factors["risk_score"]
        review_score = risk_factors["review_score"]
        
        # Format approval request
        approval_summary = self._format_approval_summary(state, risk_factors)
        
        # Simulate/collect human approval
        # In production, this would integrate with:
        # - Email notification system
        # - Approval dashboard UI
        # - Webhook for external approval systems
        # - Multi-person approval workflows
        
        approval_result = self._collect_human_approval(approval_summary)
        
        state["human_approval"] = approval_result["status"]
        state["human_notes"] = approval_result["notes"]
        
        return state
    
    def _format_approval_summary(self, state: Dict[str, Any], risk_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format deployment summary for human review.
        
        Args:
            state: Current workflow state
            risk_factors: Risk assessment details
            
        Returns:
            Formatted summary for human review
        """
        config = state.get("deployment_config", {})
        review = state.get("review", {})
        
        summary = {
            "app_name": config.get("app_name", "unknown"),
            "namespace": config.get("namespace", "default"),
            "image": config.get("image", "unknown"),
            "replicas": config.get("replicas", 1),
            "risk_score": risk_factors["risk_score"],
            "review_score": review.get("score", 0),
            "critical_factors": self._get_critical_factors(risk_factors),
            "review_issues": review.get("issues", []),
            "review_strengths": review.get("strengths", []),
        }
        
        return summary
    
    def _get_critical_factors(self, risk_factors: Dict[str, Any]) -> list:
        """
        Extract critical risk factors for human review.
        
        Args:
            risk_factors: Full risk assessment
            
        Returns:
            List of critical factors
        """
        critical = []
        
        for factor_name, factor_data in risk_factors.get("factors", {}).items():
            if factor_data.get("risk", 0) > 0:
                critical.append({
                    "name": factor_name,
                    "value": factor_data.get("value"),
                    "risk_level": factor_data.get("risk"),
                    "reason": factor_data.get("reason")
                })
        
        return critical
    
    def _collect_human_approval(self, summary: Dict[str, Any]) -> Dict[str, str]:
        """
        Collect human approval for high-risk deployment.
        
        In production, this would:
        - Send approval request email
        - Log to audit system
        - Wait for webhook/response
        - Support multi-level approval
        
        For now: Simulates approval with logging.
        
        Args:
            summary: Deployment summary
            
        Returns:
            Approval result with status and notes
        """
        print("\n" + "="*70)
        print("🚨 HUMAN APPROVAL REQUIRED")
        print("="*70)
        print(f"\nApp: {summary.get('app_name')}")
        print(f"Namespace: {summary.get('namespace')}")
        print(f"Image: {summary.get('image')}")
        print(f"Replicas: {summary.get('replicas')}")
        print(f"\n📊 Risk Assessment:")
        print(f"   Risk Score: {summary.get('risk_score')}/10")
        print(f"   Review Score: {summary.get('review_score')}/10")
        
        if summary.get("critical_factors"):
            print(f"\n⚠️  Critical Factors:")
            for factor in summary["critical_factors"]:
                print(f"   - {factor['name']}: {factor['reason']}")
        
        if summary.get("review_issues"):
            print(f"\n🔍 Review Issues:")
            for issue in summary["review_issues"][:3]:  # Show top 3
                print(f"   - {issue}")
        
        print("\n" + "-"*70)
        print("In production, this would send an approval request to:")
        print("- Deployment review team")
        print("- Infrastructure team")
        print("- Security team (if needed)")
        print("-"*70)
        
        # Simulate approval (in demo mode, auto-approve with notes)
        # In production, this would wait for actual human response
        return {
            "status": "pending_human_review",
            "notes": "Awaiting human approval from deployment team. Risk factors require manual review before proceeding to production."
        }


def human_approval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Human Approval node function for LangGraph.
    
    Delegates to HumanApprovalAgent instance.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    agent = HumanApprovalAgent(
        name="human_approval",
        auto_approve_low_risk=True  # Auto-approve low-risk deployments
    )
    return agent(state)
