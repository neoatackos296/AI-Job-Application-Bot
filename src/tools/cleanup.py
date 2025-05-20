import os
import shutil
from pathlib import Path

def setup_logging() -> None:
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_workspace_root() -> Optional[Path]:
    """Get the workspace root directory"""
    try:
        return Path(__file__).parent.parent.parent
    except Exception as e:
        logging.error(f"Failed to determine workspace root: {e}")
        return None

def remove_file(path: Path) -> None:
    """Safely remove a file or directory"""
    try:
        if path.is_file():
            path.unlink()
            logging.info(f"Removed file: {path}")
        elif path.is_dir():
            shutil.rmtree(path)
            logging.info(f"Removed directory: {path}")
    except Exception as e:
        logging.error(f"Error removing {path}: {e}")

def cleanup_workspace():
    """Clean up workspace by removing temporary files and fixing git issues"""
    setup_logging()
    
    workspace_root = get_workspace_root()
    if not workspace_root:
        return
    
    # Files and patterns to remove
    files_to_remove = [
        "t Initializing Git repository...",
        "jobs.db",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "pip-log.txt",
        "*.swp",
        "*.swo",
        ".DS_Store",
        "Thumbs.db"
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
