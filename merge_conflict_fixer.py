#!/usr/bin/env python3
"""
MindForge PR #65 - Merge Conflict Diagnostic and Auto-Fix Script
Run this script to identify and automatically fix common merge issues.
"""

import sys
import subprocess
import re
from pathlib import Path


class MergeConflictFixer:
    def __init__(self) -> None:
        self.issues_found = []
        self.fixes_applied = []
        self.backend_path = Path("apps/backend")

    def check_git_status(self) -> bool:
        """Check if we're in a git repo with conflicts"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            if result.returncode != 0:
                print("❌ Not in a git repository")
                return False

            conflicts = [
                line
                for line in result.stdout.split("\n")
                if line.startswith("UU") or line.startswith("AA")
            ]

            if conflicts:
                print(f"🔍 Found {len(conflicts)} files with merge conflicts:")
                for conflict in conflicts:
                    print(f"   {conflict}")
                return True
            print("✅ No active merge conflicts detected")
            return False
        except FileNotFoundError:
            print("❌ Git not found in PATH")
            return False

    def find_conflict_markers(self) -> list[Path]:
        """Find files with conflict markers"""
        conflict_files: list[Path] = []

        if not self.backend_path.exists():
            print(f"❌ Backend path not found: {self.backend_path}")
            return conflict_files

        for py_file in self.backend_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            if any(
                marker in content for marker in ["<<<<<<<", ">>>>>>>", "======="]
            ):
                conflict_files.append(py_file)

        if conflict_files:
            print(f"🔍 Found conflict markers in {len(conflict_files)} files:")
            for file in conflict_files:
                print(f"   {file}")
        else:
            print("✅ No conflict markers found in Python files")

        return conflict_files

    def check_import_issues(self) -> list[dict]:
        """Check for problematic import patterns"""
        import_issues: list[dict] = []

        problematic_patterns = [
            (r"from \.business_partner", "Relative import detected"),
            (r"from \.creative_analyzer", "Relative import detected"),
            (r"from \.project_questioner", "Relative import detected"),
        ]

        for py_file in self.backend_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for pattern, issue_type in problematic_patterns:
                    if re.search(pattern, line):
                        import_issues.append(
                            {
                                "file": py_file,
                                "line": line_num,
                                "content": line.strip(),
                                "issue": issue_type,
                            }
                        )

        if import_issues:
            print(f"🔍 Found {len(import_issues)} import issues:")
            for issue in import_issues:
                print(f"   {issue['file']}:{issue['line']} - {issue['issue']}")
                print(f"     {issue['content']}")
        else:
            print("✅ No problematic import patterns found")

        return import_issues

    def fix_imports(self, dry_run: bool = True) -> list[Path]:
        """Fix relative imports to absolute imports"""
        fixes = {
            r"from \.business_partner": "from apps.backend.services.business_partner",
            r"from \.creative_analyzer": "from apps.backend.services.creative_analyzer",
            r"from \.project_questioner": "from apps.backend.services.project_questioner",
        }

        files_modified: list[Path] = []

        for py_file in self.backend_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            for pattern, replacement in fixes.items():
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                files_modified.append(py_file)
                if not dry_run:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)

        if files_modified:
            action = "Would modify" if dry_run else "Modified"
            print(f"🔧 {action} {len(files_modified)} files:")
            for file in files_modified:
                print(f"   {file}")
        else:
            print("✅ No import fixes needed")

        return files_modified

    def check_missing_dependencies(self) -> bool:
        """Check if requirements.txt has all needed dependencies"""
        req_file = self.backend_path / "requirements.txt"

        if not req_file.exists():
            print("❌ requirements.txt not found")
            return False

        with open(req_file, "r", encoding="utf-8") as f:
            current_reqs = f.read().lower()

        required_deps = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "python-multipart",
            "orjson",
            "pypdf",
            "alembic",
            "python-dotenv",
            "httpx",
            "openai",
        ]

        missing_deps = [dep for dep in required_deps if dep not in current_reqs]

        if missing_deps:
            print(f"🔍 Missing dependencies: {', '.join(missing_deps)}")
            return False
        print("✅ All required dependencies found")
        return True

    def check_file_structure(self) -> bool:
        """Check if expected files exist"""
        expected_files = [
            "apps/backend/app.py",
            "apps/backend/models.py",
            "apps/backend/schemas.py",
            "apps/backend/services/project_questioner.py",
            "apps/backend/services/creative_analyzer.py",
            "apps/backend/routers/creative_projects.py",
        ]

        missing_files = [file_path for file_path in expected_files if not Path(file_path).exists()]

        if missing_files:
            print("🔍 Missing expected files:")
            for file in missing_files:
                print(f"   {file}")
            return False
        print("✅ All expected files found")
        return True

    def run_tests(self) -> bool:
        """Try to run the application to check for runtime errors"""
        print("🧪 Testing application startup...")

        sys.path.insert(0, str(self.backend_path))

        try:
            from app import app  # type: ignore  # noqa: F401

            print("✅ Application imports successfully")
            return True
        except ImportError as e:  # pragma: no cover - diagnostic tool
            print(f"❌ Import error: {e}")
            return False
        except Exception as e:  # pragma: no cover - diagnostic tool
            print(f"❌ Runtime error: {e}")
            return False

    def generate_fix_commands(self) -> None:
        """Generate commands to fix common issues"""
        commands = [
            "# Fix import paths",
            "find apps/backend -name '*.py' -type f -exec sed -i 's/from \\.business_partner/from apps.backend.services.business_partner/g' {} \\",
            ";",
            "",
            "# Install missing dependencies",
            "cd apps/backend && pip install -r requirements.txt",
            "",
            "# Check for remaining conflicts",
            "grep -r '<<<<<<< HEAD' apps/backend/ || echo 'No conflicts found'",
            "",
            "# Test the application",
            "cd apps/backend && python -c 'from app import app; print(\"✅ App loads successfully\")'",
            "",
            "# Start the server",
            "cd apps/backend && uvicorn app:app --reload --port 8000",
        ]

        print("\n📋 Suggested fix commands:")
        for cmd in commands:
            print(cmd)

    def run_full_diagnostic(self) -> None:
        """Run all diagnostic checks"""
        print("🔍 Running MindForge PR #65 merge conflict diagnostic...\n")

        has_conflicts = self.check_git_status()
        print()

        conflict_files = self.find_conflict_markers()
        print()

        import_issues = self.check_import_issues()
        print()

        deps_ok = self.check_missing_dependencies()
        print()

        files_ok = self.check_file_structure()
        print()

        app_ok = self.run_tests()
        print()

        print("📊 DIAGNOSTIC SUMMARY:")
        print(f"   Merge conflicts: {'❌' if has_conflicts else '✅'}")
        print(f"   Conflict markers: {'❌' if conflict_files else '✅'}")
        print(f"   Import issues: {'❌' if import_issues else '✅'}")
        print(f"   Dependencies: {'✅' if deps_ok else '❌'}")
        print(f"   File structure: {'✅' if files_ok else '❌'}")
        print(f"   App startup: {'✅' if app_ok else '❌'}")

        if import_issues:
            choice = input("\n🔧 Would you like to auto-fix import issues? (y/n): ")
            if choice.lower().startswith("y"):
                self.fix_imports(dry_run=False)
                print("✅ Import fixes applied")

        if not all(
            [not has_conflicts, not conflict_files, not import_issues, deps_ok, files_ok, app_ok]
        ):
            print("\n📋 See suggested fix commands below:")
            self.generate_fix_commands()
        else:
            print("\n🎉 All checks passed! The merge should be ready.")


if __name__ == "__main__":
    fixer = MergeConflictFixer()
    fixer.run_full_diagnostic()
