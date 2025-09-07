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


# ---------- Helpers to support both repo layouts ----------

def repo_root() -> Path:
    return Path(__file__).parent.resolve()

def has_apps_layout() -> bool:
    return (repo_root() / "apps" / "backend" / "app.py").exists()

def has_flat_backend_layout() -> bool:
    return (repo_root() / "backend" / "app.py").exists()

def ensure_sys_path():
    """
    Add the correct source dir to sys.path depending on layout.
    Prefer apps/ layout; fall back to backend/ layout.
    """
    root = repo_root()
    if has_apps_layout():
        p = root / "apps"
        if str(p) not in sys.path:
            sys.path.append(str(p))
        return "apps"
    elif has_flat_backend_layout():
        p = root / "backend"
        if str(p) not in sys.path:
            sys.path.append(str(root))      # allow 'from backend...' imports
        return "backend"
    else:
        return "unknown"


# ---------- Checks ----------

def check_python_version() -> bool:
    ver = platform.python_version()
    major, minor, *_ = platform.python_version_tuple()
    ok = int(major) >= 3 and int(minor) >= 9
    print(f"Detected Python: {ver}")
    if not ok:
        print("⚠️  Python 3.9+ recommended.")
    return ok

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
        if (repo_root() / "pyproject.toml").exists():
            print("Run: poetry install")
        elif (repo_root() / "backend" / "requirements.txt").exists():
            print("Run: cd backend && pip install -r requirements.txt")
        else:
            print("Install with Poetry or provide backend/requirements.txt")
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
        # Try imports under backend.*
        from backend.models import Base  # noqa: F401
        from backend.models import Conversation, Message, ProcessMap  # noqa: F401
        print("✅ Database models found (backend.models)")
    except Exception as e:
        print(f"⚠️  Database models missing or failed to import: {e}")
        return False

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
        layout = ensure_sys_path()
        from backend.app import app  # noqa: F401
        src = "apps/backend" if layout == "apps" else "backend"
        print(f"✅ App imports successfully from {src}")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False


# ---------- Suggestions ----------

def suggest_fixes():
    print("\n🔧 Common fixes:")
    # pip flow
    if (repo_root() / "backend" / "requirements.txt").exists():
        print("1. Install dependencies (pip): cd backend && pip install -r requirements.txt")
        print("2. Run in simple mode: USE_DATABASE=false python -m uvicorn backend.app:app --reload")
        print("3. Enable database mode: USE_DATABASE=true python -m uvicorn backend.app:app --reload")
    # poetry flow
    if (repo_root() / "pyproject.toml").exists():
        print("1. Install dependencies (Poetry): poetry install")
        if has_apps_layout():
            print("2. Run simple mode: USE_DATABASE=false poetry run uvicorn apps.backend.app:app --reload")
            print("3. DB mode:       USE_DATABASE=true  poetry run uvicorn apps.backend.app:app --reload")
        else:
            print("2. Run simple mode: USE_DATABASE=false poetry run uvicorn backend.app:app --reload")
            print("3. DB mode:       USE_DATABASE=true  poetry run uvicorn backend.app:app --reload")

    print("4. On macOS run ./start-mac.sh or double-click MindForge.app")
    print("5. Check logs for detailed errors")
    print("6. Ensure you're in a virtual environment (e.g., `source .venv/bin/activate`)")

# ---------- Main ----------

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
        if has_apps_layout():
            print("Try: ./run.sh  or  poetry run uvicorn apps.backend.app:app --reload")
        else:
            print("Try: ./run.sh  or  python -m uvicorn backend.app:app --reload")
    else:
        print(f"⚠️  {passed}/{total} checks passed. See issues above.")
        suggest_fixes()


if __name__ == "__main__":
    main()
