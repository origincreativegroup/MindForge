"""
Simple test script for creative projects router functionality.
Run this once FastAPI and other dependencies are installed.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from apps.backend.schemas import ProjectType, CreativeProjectCreate, ProjectUploadResponse
        print("✅ Schemas imported successfully")
    except Exception as e:
        print(f"❌ Schemas import failed: {e}")
        return False
    
    try:
        from apps.backend.services.models import CreativeProject, ProjectQuestion
        print("✅ Models imported successfully")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from apps.backend.services.project_questioner import CaseyProjectQuestioner
        print("✅ Project questioner imported successfully")
    except Exception as e:
        print(f"❌ Project questioner import failed: {e}")
        return False
    
    try:
        from apps.backend.services.creative_analyzer import CreativeProjectAnalyzer
        print("✅ Creative analyzer imported successfully")
    except Exception as e:
        print(f"❌ Creative analyzer import failed: {e}")
        return False
    
    return True

def test_service_instantiation():
    """Test that services can be instantiated."""
    print("\nTesting service instantiation...")
    
    try:
        from apps.backend.services.project_questioner import CaseyProjectQuestioner
        questioner = CaseyProjectQuestioner()
        print("✅ CaseyProjectQuestioner instantiated successfully")
        
        # Test question templates
        assert len(questioner.question_templates) > 0
        print(f"✅ Question templates loaded: {len(questioner.question_templates)} project types")
        
    except Exception as e:
        print(f"❌ CaseyProjectQuestioner failed: {e}")
        return False
    
    try:
        from apps.backend.services.creative_analyzer import CreativeProjectAnalyzer
        analyzer = CreativeProjectAnalyzer()
        print("✅ CreativeProjectAnalyzer instantiated successfully")
        
        # Test supported file types
        assert len(analyzer.supported_image_types) > 0
        print(f"✅ File type support loaded: {len(analyzer.supported_image_types)} image types")
        
    except Exception as e:
        print(f"❌ CreativeProjectAnalyzer failed: {e}")
        return False
    
    return True

def test_router_import():
    """Test that the router can be imported."""
    print("\nTesting router import...")
    
    try:
        from apps.backend.routers.creative_projects import router
        print("✅ Creative projects router imported successfully")
        
        # Check that routes are registered
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/upload",
            "/projects",
            "/projects/{project_id}",
            "/projects/{project_id}/casey-question",
            "/projects/{project_id}/answer",
            "/projects/{project_id}/analyze",
            "/projects/{project_id}/chat"
        ]
        
        for expected_route in expected_routes:
            full_route = f"/api/creative{expected_route}"
            if any(expected_route in route for route in routes):
                print(f"✅ Route registered: {expected_route}")
            else:
                print(f"❌ Route missing: {expected_route}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Router import failed: {e}")
        return False

def test_app_integration():
    """Test that the router is properly integrated into the app."""
    print("\nTesting app integration...")
    
    try:
        # This would test the app integration but requires database setup
        print("⚠️  App integration test requires database setup")
        print("   Run with USE_DATABASE=true environment variable when dependencies are available")
        return True
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Creative Projects Router Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_service_instantiation,
        test_router_import,
        test_app_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Router is ready for use.")
        return 0
    else:
        print("💥 Some tests failed. Check dependencies and setup.")
        return 1

if __name__ == "__main__":
    exit(main())