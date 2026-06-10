"""
Reporting Agent
Generates final report and stores output files
"""

from typing import Any, Dict
from datetime import datetime
import json
from pathlib import Path
from src.agents.base import BaseAgent


class ReporterAgent(BaseAgent):
    """
    Reporter Agent: Generates final reports and stores outputs.
    
    Creates comprehensive reports of the deployment generation process,
    saves deployment YAML files, and generates summary documentation.
    """
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute reporter logic: Generate reports and save files.
        
        Args:
            state: Final agent state
            
        Returns:
            Updated state with final_output and output_path
        """
        try:
            # Create output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("outputs") / timestamp
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save deployment YAML
            deployment_file = output_dir / "deployment.yaml"
            if state.get("deployment_yaml"):
                deployment_file.write_text(state["deployment_yaml"])

            # Create summary report
            report = {
                "timestamp": timestamp,
                "status": state.get("decision", "unknown"),
                "retries_used": state.get("retries", 0),
                "task": state.get("task", ""),
                "plan_summary": state.get("plan", ""),
                "review_score": state.get("review", {}).get("score", 0),
                "review_issues": state.get("review", {}).get("issues", []),
                "review_strengths": state.get("review", {}).get("strengths", []),
                "errors": state.get("errors", [])
            }

            # Save report
            report_file = output_dir / "report.json"
            report_file.write_text(json.dumps(report, indent=2))

            # Create summary text
            summary = f"""
=== K8s Deployment Generation Report ===
Generated: {timestamp}
Status: {report['status'].upper()}
Retries Used: {report['retries_used']}

Task:
{report['task']}

Planning Strategy:
{report['plan_summary']}

Review Results:
- Score: {report['review_score']}/10
- Issues: {len(report['review_issues'])}
- Strengths: {len(report['review_strengths'])}

Output Files:
- Deployment YAML: {deployment_file}
- Report JSON: {report_file}

Errors: {len(report['errors'])}
"""

            summary_file = output_dir / "SUMMARY.txt"
            summary_file.write_text(summary)

            final_output = f"""
Deployment Generation Complete!
================================

Output Location: {output_dir}

Files Generated:
1. deployment.yaml - K8s deployment manifests (Deployment, Service, HPA)
2. report.json - Detailed generation report
3. SUMMARY.txt - Quick summary

Status: {report['status'].upper()}
Review Score: {report['review_score']}/10

To deploy:
kubectl apply -f {deployment_file}
"""

            return {
                **state,
                "final_output": final_output,
                "output_path": str(output_dir)
            }

        except Exception as e:
            self._handle_error(e, "report generation")
            error_msg = f"Report generation error: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            return {
                **state,
                "final_output": f"Error generating report: {error_msg}",
            }


# Backward compatibility: Keep report_node function
def report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report node function for backward compatibility.
    
    Delegates to ReporterAgent instance.
    """
    agent = ReporterAgent(name="reporter")
    return agent(state)
