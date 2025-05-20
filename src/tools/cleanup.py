import os
import shutil
from pathlib import Path

def cleanup_workspace():
    """Clean up workspace by removing temporary files and fixing git issues"""
    workspace_root = Path(__file__).parent.parent.parent
    
    # Files to remove
    files_to_remove = [
        "t Initializing Git repository...",
        "jobs.db",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "pip-log.txt",
    ]
    
    # Clean up temporary files
    for pattern in files_to_remove:
        for file_path in workspace_root.rglob(pattern):
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")
    
    # Ensure database directory exists
    db_dir = workspace_root / "src" / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    
    print("Workspace cleanup completed successfully!")

if __name__ == "__main__":
    cleanup_workspace()
