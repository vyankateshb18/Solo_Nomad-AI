"""Workflow state persistence and checkpointing engine for Human-in-the-Loop review."""
import json
import os
import logging
from typing import Optional, Dict, Any
from solo_travel.models.state import SoloTravelState

logger = logging.getLogger(__name__)


class StateCheckpointer:
    """Saves and restores SoloTravelState from local checkpoint files."""

    def __init__(self, storage_dir: str = ".checkpoints"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_path(self, session_id: str) -> str:
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("-", "_"))
        return os.path.join(self.storage_dir, f"{safe_id}.json")

    def save_checkpoint(self, session_id: str, state: SoloTravelState) -> str:
        """Serializes current state into a JSON checkpoint."""
        filepath = self._get_path(session_id)
        try:
            data = state.model_dump(mode="json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return filepath
        except Exception as exc:
            logger.error(f"Failed to save state checkpoint: {exc}")
            raise

    def load_checkpoint(self, session_id: str) -> Optional[SoloTravelState]:
        """Loads and deserializes state from a JSON checkpoint."""
        filepath = self._get_path(session_id)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SoloTravelState(**data)
        except Exception as exc:
            logger.error(f"Failed to load state checkpoint: {exc}")
            return None

    def delete_checkpoint(self, session_id: str) -> None:
        """Deletes checkpoint after workflow finalization."""
        filepath = self._get_path(session_id)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
