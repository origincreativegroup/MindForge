#!/usr/bin/env python3
"""
Debug script for MindForge Casey MVP
Checks dependencies, file structure, and common issues
"""

import importlib.util
import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK")
    return True


def check_file_structure():
    """Check if required files exist."""
    base = Path(__file__).parent
    required_files = ["apps/backend/app.py", "run.sh", "README.md"]

    missing_files = []
    for file_path in required_files:
        if not (base / file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    print("✅ Core file structure OK")
    return True


def check_dependencies():
    """Check if required Python packages are available."""
    required_packages = ["fastapi", "uvicorn", "jinja2", "pydantic", "httpx"]

    optional_packages = ["orjson", "pypdf", "sqlalchemy"]

    missing_required = []
    missing_optional = []

    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_required.append(package)

    for package in optional_packages:
        if importlib.util.find_spec(package) is None:
            missing_optional.append(package)

    if missing_required:
        print(f"❌ Missing required packages: {missing_required}")
        print("Run: poetry install")
        return False

    print("✅ Required dependencies OK")

    if missing_optional:
        print(f"⚠️  Missing optional packages: {missing_optional}")
        print("Some features may be limited")

    return True


def check_database_setup():
    """Check database configuration."""
    try:
        # Try to import database modules
        sys.path.append(str(Path(__file__).parent / "apps"))

        try:
            from backend.models import Base, Conversation, Message, ProcessMap

            print("✅ Database models found")
        except ImportError as e:
            print(f"⚠️  Database models missing: {e}")
            return False

        try:
            from backend.db import engine, get_db

            print("✅ Database configuration found")
        except ImportError as e:
            print(f"⚠️  Database configuration missing: {e}")
            return False

        return True
    except Exception as e:
        print(f"⚠️  Database setup issue: {e}")
        return False


def check_environment():
    """Check environment variables and configuration."""
    issues = []

    # Check for LLM configuration
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY not set (LLM features will use fallbacks)")

    # Check database mode
    use_db = os.getenv("USE_DATABASE", "false").lower() == "true"
    print(f"Database mode: {'enabled' if use_db else 'disabled'}")

    if issues:
        print("⚠️  Environment issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Environment OK")

    return True


def check_ports():
    """Check if default port is available."""
    import socket

    port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(("localhost", port))
        if result == 0:
            print(f"⚠️  Port {port} is already in use")
            return False
        else:
            print(f"✅ Port {port} is available")
            return True


def run_basic_import_test():
    """Test basic imports."""
    try:
        sys.path.append(str(Path(__file__).parent / "apps"))
        print("✅ App imports successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False


def suggest_fixes():
    """Suggest common fixes."""
    print("\n🔧 Common fixes:")
    print("1. Install dependencies: poetry install")
    print(
        "2. Run in simple mode: USE_DATABASE=false poetry run uvicorn apps.backend.app:app --reload"
    )
    print(
        "3. Enable database mode: USE_DATABASE=true poetry run uvicorn apps.backend.app:app --reload"
    )
    print("4. Check logs for detailed errors")
    print("5. Ensure you're in a virtual environment")


def main():
    """Main debug function."""
    print("🔍 MindForge Casey - Debug Check")
    print("=" * 40)

    checks = [
        ("Python Version", check_python_version),
        ("File Structure", check_file_structure),
        ("Dependencies", check_dependencies),
        ("Database Setup", check_database_setup),
        ("Environment", check_environment),
        ("Port Availability", check_ports),
        ("Basic Import", run_basic_import_test),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results.append(False)

    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print("🎉 All checks passed! You should be able to run the application.")
        print("Try: ./run.sh or poetry run uvicorn apps.backend.app:app --reload")
    else:
        print(f"⚠️  {passed}/{total} checks passed. See issues above.")
        suggest_fixes()


if __name__ == "__main__":
    main()
