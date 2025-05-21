"""Test script to verify project setup"""
import os
import sys
import logging
from pathlib import Path

def verify_setup():
    """Verify project setup and requirements"""
    try:
        # Check directories
        required_dirs = ['database', 'logs', 'templates']
        for dir_name in required_dirs:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"✓ Directory '{dir_name}' exists")

        # Check environment variables
        required_env = ['OPENAI_API_KEY', 'DATABASE_URL']
        for env_var in required_env:
            if os.getenv(env_var):
                print(f"✓ Environment variable '{env_var}' is set")
            else:
                print(f"✗ Missing environment variable: {env_var}")

        # Test imports
        from src.database import init_db
        from src.models import Job, Application
        from src.browser import Browser
        print("✓ All imports successful")

        return True

    except Exception as e:
        print(f"✗ Setup verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_setup():
        print("\n✓ Project setup complete!")
    else:
        print("\n✗ Project setup incomplete. Please check errors above.")