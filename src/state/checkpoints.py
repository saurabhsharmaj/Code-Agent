"""
Checkpoint management for workflow persistence
Handles saving and loading workflow state for resume capabilities
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class CheckpointManager:
    """Manages workflow checkpoints for persistence and recovery"""

    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

    def save_checkpoint(self, state: Dict[str, Any], checkpoint_id: Optional[str] = None) -> str:
        """
        Save workflow state as checkpoint

        Args:
            state: Workflow state to save
            checkpoint_id: Optional custom checkpoint ID

        Returns:
            Checkpoint ID
        """
        checkpoint_id = checkpoint_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"

        with open(checkpoint_file, "w") as f:
            json.dump(state, f, indent=2, default=str)

        return checkpoint_id

    def load_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Load workflow state from checkpoint

        Args:
            checkpoint_id: Checkpoint ID to load

        Returns:
            Workflow state
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"

        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")

        with open(checkpoint_file, "r") as f:
            return json.load(f)

    def list_checkpoints(self) -> list[str]:
        """List all available checkpoints"""
        return [f.stem for f in self.checkpoint_dir.glob("*.json")]
