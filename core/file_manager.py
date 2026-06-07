from pathlib import Path
import shutil


class FileManager:
    """Handles copying, restoring, and clearing project files."""

    SIMPLEGIT_DIR = ".simplegit"

    def copy_project_files(self, project_dir, files_path):
        """
        Copy project files into a snapshot folder.

        The .simplegit folder is skipped so snapshots do not copy themselves.
        """
        project_dir = Path(project_dir)
        files_path = Path(files_path)
        files_path.mkdir(parents=True, exist_ok=True)

        for item in project_dir.rglob("*"):
            relative_path = item.relative_to(project_dir)

            if self.SIMPLEGIT_DIR in relative_path.parts:
                continue

            destination = files_path / relative_path

            if item.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            elif item.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, destination)

    def restore_files(self, snapshot_files, project_dir):
        """Restore files from a snapshot folder back into the project."""
        snapshot_files = Path(snapshot_files)
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)

        for item in snapshot_files.rglob("*"):
            relative_path = item.relative_to(snapshot_files)

            if self.SIMPLEGIT_DIR in relative_path.parts:
                continue

            destination = project_dir / relative_path

            if item.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            elif item.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, destination)

    def delete_working_files(self, project_dir):
        """
        Delete current project files before restoring a snapshot.

        The .simplegit folder is preserved because it stores repository data.
        """
        project_dir = Path(project_dir)

        for item in project_dir.iterdir():
            if item.name == self.SIMPLEGIT_DIR:
                continue

            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
