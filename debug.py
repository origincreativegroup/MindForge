#!/usr/bin/env python3
"""
MindForge Casey - Debug Check

This script validates your local dev environment:
- Python version
- File structure (supports both apps/backend and backend layouts)
- Dependencies (poetry or pip)
- Database models/config presence
- Environment variables
- Port 8000 availability
- Basic import of FastAPI app

Run:
    python debug.py
"""

import importlib.util
import os
import sys
import platform
from pathlib import Path



def check_file_structure() -> bool:
    base = repo_root()
    required_common = ["README.md"]
    found = True

    for rel in required_common:
        if not (base / rel).exists():
            print(f"⚠️  Missing file: {rel}")
            found = False

    apps_layout = has_apps_layout()
    backend_layout = has_flat_backend_layout()

    if apps_layout:
        print("✅ Found apps/ layout: apps/backend/app.py")
    if backend_layout:
        print("✅ Found backend/ layout: backend/app.py")

    if not (apps_layout or backend_layout):
        print("❌ Could not find FastAPI app at apps/backend/app.py or backend/app.py")
        return False

    # Helpful runner hints
    if (base / "run.sh").exists():
        print("✅ Found run.sh")

    if (base / "pyproject.toml").exists():
        print("✅ Found pyproject.toml (Poetry project)")
    elif (base / "backend" / "requirements.txt").exists():
        print("✅ Found backend/requirements.txt (pip project)")

    return found

def check_dependencies() -> bool:
    required_packages = [
        "fastapi",
        "uvicorn",
        "jinja2",
        "pydantic",
        "httpx",
    ]
    optional_packages = [
        "orjson",
        "pypdf",
        "sqlalchemy",
    ]

    missing_required = [pkg for pkg in required_packages if importlib.util.find_spec(pkg) is None]
    missing_optional = [pkg for pkg in optional_packages if importlib.util.find_spec(pkg) is None]

    if missing_required:
        print(f"❌ Missing required packages: {missing_required}")

        return False

    print("✅ Required dependencies OK")

    if missing_optional:
        print(f"⚠️  Missing optional packages: {missing_optional}")
        print("Some features may be limited.")
    else:
        print("✅ Optional dependencies OK")

    return True

def check_database_setup() -> bool:
    layout = ensure_sys_path()
    try:


    try:
        from backend.db import engine, get_db  # noqa: F401
        print("✅ Database configuration found (backend.db)")
    except Exception as e:
        print(f"⚠️  Database configuration missing or failed to import: {e}")
        return False

    return True

def check_environment() -> bool:
    issues = []

    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY not set (LLM features will use fallbacks)")

    use_db = os.getenv("USE_DATABASE", "false").lower() == "true"
    print(f"Database mode: {'enabled' if use_db else 'disabled'}")

    if issues:
        print("⚠️  Environment issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Environment OK")

    return True

def check_ports() -> bool:
    import socket

    port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port))
        if result == 0:
            print(f"⚠️  Port {port} is already in use")
            return False
        else:
            print(f"✅ Port {port} is available")
            return True

def run_basic_import_test() -> bool:
    try:

        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False


# ---------- Suggestions ----------

def suggest_fixes():
    print("\n🔧 Common fixes:")


def main():
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
    passed = sum(1 for r in results if r)
    total = len(results)

    if passed == total:
        print("🎉 All checks passed! You should be able to run the application.")

    else:
        print(f"⚠️  {passed}/{total} checks passed. See issues above.")
        suggest_fixes()


if __name__ == "__main__":
    main()
