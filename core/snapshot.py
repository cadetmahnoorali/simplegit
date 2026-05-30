from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pathlib import Path
import json 

@dataclass
class Snapshot:
    """Represents a single snapshot in the repository."""

    id: str
    message:str
    timestamp: str
    parent: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert snapshot to dictionary for JSON storage."""
        return {
            "id": self.id,
            "message": self.message,
            "timestamp": self.timestamp,
            "parent": self.parent
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Snapshot':
        return Snapshot(
            id=data["id"],
            message=data["message"],
            timestamp=data["timestamp"],
            parent=data.get("parent")
        )

class SnapshotManager:
    """Manages snapshot creation, restoration, and metadata."""

    def __init__(self, dir=Path):
        self.dir = dir
        self.snapshots_dir = dir / "snapshots"
        self.timeline_dir = dir / "timeline"
        self.head_file = "HEAD.json"


    def create_snapshot(
        self,
        message: str,
        project_dir: Path,
        file_manager,
        timeline_manager
        )-> Snapshot:
        """
        Create a new snapshot.
        
        Args:
            message: Snapshot description
            project_dir: Path to project directory
            file_manager: FileManager instance for copying files
            timeline_manager: TimelineManager instance for updating timeline
            
        Returns:
            Created Snapshot object
        """
        snapshot_id = self._generate_snap_id()

        parent_snapshot = self._get_current_snapshot()

        parent_id = parent_snapshot.id if parent_snapshot else None

        # Create snapshot directory
        snapshot_path = self.snapshots_dir / snapshot_id
        snapshot_path.mkdir(parents=True, exist_ok=True)

        files_path = snapshot_path / "files"
        files_path.mkdir(exist_ok=True)

        # ! filemanager yet to write 
        file_manager.copy_project_files(project_dir, files_path)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        snapshot = Snapshot(
            id=snapshot_id,
            message=message,
            timestamp=timestamp,
            parent=parent_id
        )
        
        # Save metadata
        self._save_snapshot_metadata(snapshot)
        
        # Update timeline
        timeline_manager.add_snapshot(snapshot_id)
        
        # Update HEAD
        self._update_head(snapshot_id)
        
        return snapshot


    def _update_head(self, snapshot_id: str) -> None:
        """Update HEAD to point to snapshot."""
        head_data = {"current_snapshot": snapshot_id}
        
        with open(self.head_file, 'w') as f:
            json.dump(head_data, f, indent=2)


    def _save_snapshot_metadata(self, snapshot: Snapshot) -> None:
        """Save snapshot metadata to file."""
        snapshot_path = self.snapshots_dir / snapshot.id
        metadata_file = snapshot_path / "meta.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2)


    def _get_current_snapshot(self) ->  Optional[Snapshot]:
        """Get currently checked out snapshot."""
        if not self.head_file.exists():
            return None
        
        try:
            with open(self.head_file, 'r') as f:
                data = json.load(f)
            snapshot_id = data.get("current_snapshot")
            return self.get_snapshot(snapshot_id) if snapshot_id else None
        except (json.JSONDecodeError, KeyError):
            return None
        

    def get_all_snapshots(self) -> list[Snapshot]:
        snapshots = []

        if not self.snapshots_dir.exists():
            return snapshots
        
        for snapshot_dir in sorted(self.snapshots_dir.iterdir()):
            if snapshot_dir.is_dir():
                snapshot = self.get_snapshot(snapshot_dir.name)
                if snapshot:
                    snapshots.append(snapshot)

        return snapshots
    

    def _generate_snap_id(self):
        snapshots = self.get_all_snapshots()
        next_number = len(snapshots) + 1
        return f"{next_number}"

    