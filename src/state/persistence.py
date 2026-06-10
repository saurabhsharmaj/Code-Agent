"""
State persistence layer for workflow data
Handles storage and retrieval of workflow states across sessions
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
from pathlib import Path


class PersistenceBackend(ABC):
    """Abstract base class for persistence backends"""

    @abstractmethod
    def save(self, key: str, value: Any) -> None:
        """Save value with key"""
        pass

    @abstractmethod
    def load(self, key: str) -> Any:
        """Load value by key"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value by key"""
        pass


class FilePersistence(PersistenceBackend):
    """File-based persistence backend"""

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    def save(self, key: str, value: Any) -> None:
        """Save to JSON file"""
        file_path = self.base_path / f"{key}.json"
        with open(file_path, "w") as f:
            json.dump(value, f, indent=2, default=str)

    def load(self, key: str) -> Any:
        """Load from JSON file"""
        file_path = self.base_path / f"{key}.json"
        if not file_path.exists():
            raise KeyError(f"Key {key} not found")
        with open(file_path, "r") as f:
            return json.load(f)

    def exists(self, key: str) -> bool:
        """Check if file exists"""
        return (self.base_path / f"{key}.json").exists()

    def delete(self, key: str) -> None:
        """Delete file"""
        file_path = self.base_path / f"{key}.json"
        if file_path.exists():
            file_path.unlink()


class StateStore:
    """High-level state persistence interface"""

    def __init__(self, backend: Optional[PersistenceBackend] = None):
        self.backend = backend or FilePersistence()

    def save_state(self, state_id: str, state: Dict[str, Any]) -> None:
        """Save workflow state"""
        self.backend.save(f"state_{state_id}", state)

    def load_state(self, state_id: str) -> Dict[str, Any]:
        """Load workflow state"""
        return self.backend.load(f"state_{state_id}")

    def state_exists(self, state_id: str) -> bool:
        """Check if state exists"""
        return self.backend.exists(f"state_{state_id}")
