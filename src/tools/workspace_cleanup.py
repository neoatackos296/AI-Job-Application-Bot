import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional

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

def cleanup_workspace() -> None:
    """Clean up workspace by removing temporary files and fixing git issues"""
    setup_logging()
    
    workspace_root = get_workspace_root()
    if not workspace_root:
        logging.error("Could not determine workspace root")
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
    
    try:
        # Clean up temporary files
        for pattern in files_to_remove:
            for file_path in workspace_root.rglob(pattern):
                remove_file(file_path)
        
        # Ensure required directories exist
        required_dirs = [
            workspace_root / "src" / "database",
            workspace_root / "src" / "static" / "uploads",
            workspace_root / "logs"
        ]
        
        for directory in required_dirs:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logging.info(f"Ensured directory exists: {directory}")
            except Exception as e:
                logging.error(f"Failed to create directory {directory}: {e}")
        
        # Create empty .gitkeep files in empty directories
        for directory in required_dirs:
            if directory.exists() and not any(directory.iterdir()):
                keep_file = directory / ".gitkeep"
                try:
                    keep_file.touch()
                    logging.info(f"Created .gitkeep in: {directory}")
                except Exception as e:
                    logging.error(f"Failed to create .gitkeep in {directory}: {e}")
        
        # Remove stray git file if it exists
        git_file = workspace_root / "t Initializing Git repository..."
        if git_file.exists():
            try:
                git_file.unlink()
                logging.info("Removed stray git file")
            except Exception as e:
                logging.error(f"Failed to remove stray git file: {e}")
        
        logging.info("Workspace cleanup completed successfully!")
        
    except Exception as e:
        logging.error(f"Workspace cleanup failed: {e}")
        raise

if __name__ == "__main__":
    cleanup_workspace()
