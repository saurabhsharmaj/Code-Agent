#!/usr/bin/env python3
"""
Test workflow with high-risk deployment requiring human approval
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state.schemas import AgentState
from src.graphs.deployment_graph.builder import build_deployment_graph


def create_initial_state(task: str, max_retries: int = 3) -> AgentState:
    """Create initial state for the workflow"""
    return {
        "task": task,
        "plan": "",
        "deployment_config": {},
        "deployment_yaml": "",
        "review": {},
        "decision": "",
        "risk_score": 0,
        "requires_human_approval": False,
        "human_approval": None,
        "human_notes": None,
        "retries": 0,
        "max_retries": max_retries,
        "errors": [],
        "final_output": None
    }


def test_high_risk_deployment():
    """Test deployment that should trigger human approval"""
    
    print("\n" + "="*60)
    print("[HIGH-RISK DEPLOYMENT TEST]")
    print("="*60)
    print("This deployment will require human approval due to:")
    print("- Production namespace")
    print("- 5 replicas (critical infrastructure)")
    print("- High stakes deployment")
    print("="*60 + "\n")
    
    task = """
    Create a critical Kubernetes deployment for a production payment processing service with:
    - Docker image: "payment-service:v2.0"
    - 5 replicas for high availability (critical service)
    - Port 443 (HTTPS only)
    - CPU requests: 500m, limits: 1000m
    - Memory requests: 512Mi, limits: 1Gi
    - Environment variables: ENVIRONMENT=production, LOG_LEVEL=info
    - Auto-scaling: min 3, max 20 replicas based on 50% CPU utilization
    - Include liveness and readiness probes
    - Namespace: production
    - Database: PostgreSQL with SSL
    - Security: Network policies, pod security policies required
    """
    
    # Build and execute graph
    graph = build_deployment_graph()
    initial_state = create_initial_state(task, max_retries=3)
    
    print("Running workflow...\n")
    final_state = graph.invoke(initial_state)
    
    # Display results
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    print(f"✓ Final Decision: {final_state.get('decision', 'unknown').upper()}")
    print(f"✓ Risk Score: {final_state.get('risk_score', 0)}/10")
    print(f"✓ Requires Human Approval: {'YES [!!!]' if final_state.get('requires_human_approval') else 'NO'}")
    
    if final_state.get('human_approval'):
        approval_status = final_state.get('human_approval', 'unknown').upper()
        if 'REVIEW' in approval_status or 'PENDING' in approval_status:
            print(f"✓ Approval Status: {approval_status} [LOCKED]")
        else:
            print(f"✓ Approval Status: {approval_status}")
    
    if final_state.get('human_notes'):
        print(f"✓ Notes: {final_state.get('human_notes')}")
            
    print(f"✓ Retries Used: {final_state.get('retries', 0)}/3")
    print(f"✓ Review Score: {final_state.get('review', {}).get('score', 'N/A')}/10")
    
    print("\n" + "="*60)
    print("[SUCCESS] Human Approval Layer Test Complete")
    print("="*60 + "\n")
    
    return final_state


if __name__ == "__main__":
    test_high_risk_deployment()
