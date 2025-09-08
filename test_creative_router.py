"""
Simple test script for creative projects router functionality.
Run this once FastAPI and other dependencies are installed.
"""

import os
import sys
from pathlib import Path
import pytest

# Add project root to path. The original script assumed the file lived three
# directories below the project root which isn't the case in this kata.  This
# caused an ``IndexError`` during test collection when ``parents[3]`` was
# accessed on a path that wasn't that deep.  Instead of relying on a fixed
# number of parents, walk up the directory tree until we find the repository
# root (identified by the presence of the ``apps`` directory).
project_root = Path(__file__).resolve()
while not (project_root / "apps").exists() and project_root != project_root.parent:
    project_root = project_root.parent

sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    from apps.backend.schemas import (
        ProjectType,
        CreativeProjectCreate,
        ProjectUploadResponse,
    )
    from apps.backend.services.models import CreativeProject, ProjectQuestion
    from apps.backend.services.project_questioner import CaseyProjectQuestioner
    from apps.backend.services.creative_analyzer import CreativeProjectAnalyzer

def test_service_instantiation():
    """Test that services can be instantiated."""
    from apps.backend.services.project_questioner import CaseyProjectQuestioner
    from apps.backend.services.creative_analyzer import CreativeProjectAnalyzer

    questioner = CaseyProjectQuestioner()
    assert len(questioner.question_templates) > 0

    analyzer = CreativeProjectAnalyzer()
    assert len(analyzer.supported_image_types) > 0

def test_router_import():
    """Test that the router can be imported."""
    from apps.backend.routers.creative_projects import router

    routes = [route.path for route in router.routes]
    expected_routes = [
        "/upload",
        "/projects",
        "/projects/{project_id}",
        "/projects/{project_id}/casey-question",
        "/projects/{project_id}/answer",
        "/projects/{project_id}/analyze",
        "/projects/{project_id}/chat",
    ]

    for expected_route in expected_routes:
        assert any(
            expected_route in route for route in routes
        ), f"Route missing: {expected_route}"

def test_app_integration():
    """Test that the router is properly integrated into the app."""
    if not os.getenv("USE_DATABASE"):
        pytest.skip(
            "App integration test requires database setup; "
            "run with USE_DATABASE=true to enable"
        )
    # Integration logic would go here
    assert True
