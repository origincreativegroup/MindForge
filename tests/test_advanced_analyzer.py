"""Test for AdvancedCreativeAnalyzer following the project's test patterns."""

import sys
from pathlib import Path
import asyncio
from unittest.mock import Mock
import pytest

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "apps"))

from backend.services.advanced_analyzer import AdvancedCreativeAnalyzer
from backend.services.creative_analyzer import CreativeProjectAnalyzer
from backend.services.models import Project, ProjectType, ProjectStatus


def test_analyzer_inheritance():
    """Test that AdvancedCreativeAnalyzer properly inherits from base class."""
    analyzer = AdvancedCreativeAnalyzer()
    assert isinstance(analyzer, CreativeProjectAnalyzer)
    assert hasattr(analyzer, 'analyze_project')
    assert hasattr(analyzer, 'comprehensive_project_audit')


@pytest.mark.asyncio
async def test_analyze_project_method():
    """Test the main analyze_project method that implements the abstract base."""
    analyzer = AdvancedCreativeAnalyzer()
    
    # Create a mock project
    project = Mock()
    project.id = 1
    project.title = "Test Logo Design"
    project.status = ProjectStatus.in_progress
    project.project_type = ProjectType.logo_design
    project.file_path = None
    project.dimensions = {"width": 400, "height": 400}
    project.color_palette = ["#FF5733", "#33FF57", "#3357FF"]
    project.extracted_text = "Modern logo design with clean typography."
    
    # Test the main interface method
    result = await analyzer.analyze_project(project)
    
    # Verify the result structure matches what's expected
    assert isinstance(result, dict)
    assert 'overall_score' in result
    assert 'category_scores' in result
    assert 'detailed_insights' in result
    assert 'recommendations' in result
    assert 'action_items' in result
    
    # Verify scores are in valid range
    assert 0 <= result['overall_score'] <= 1
    
    for category, score in result['category_scores'].items():
        assert 0 <= score <= 1
        assert isinstance(category, str)
    
    # Verify insights structure
    for insight in result['detailed_insights']:
        assert 'insight_type' in insight
        assert 'title' in insight
        assert 'description' in insight
        assert 'score' in insight
        assert 0 <= insight['score'] <= 1


def test_error_handling():
    """Test error handling for invalid inputs."""
    analyzer = AdvancedCreativeAnalyzer()
    
    # Test color temperature with invalid colors
    invalid_colors = ["invalid", "#GGGGGG", "not-a-color"]
    temp_result = analyzer._analyze_color_temperature(invalid_colors)
    
    # Should handle gracefully and return neutral result
    assert temp_result['dominant'] == 'neutral'
    assert temp_result['warm_ratio'] == 0.5
    assert temp_result['cool_ratio'] == 0.5
    
    # Test color harmony with invalid colors
    harmony_score = analyzer._calculate_color_harmony(invalid_colors)
    assert 0 <= harmony_score <= 1
    
    # Test readability with empty text
    readability = analyzer._calculate_readability_score("")
    assert readability == 0.0


def test_project_type_enum():
    """Test that ProjectType enum is properly defined and accessible."""
    # Test that all expected project types exist
    expected_types = [
        'branding', 'website_mockup', 'social_media', 'print_design',
        'illustration', 'photography', 'video_production', 'ui_ux',
        'packaging', 'logo_design'
    ]
    
    for type_name in expected_types:
        assert hasattr(ProjectType, type_name)
        project_type = getattr(ProjectType, type_name)
        assert project_type.value == type_name


@pytest.mark.asyncio
async def test_minimal_project_analysis():
    """Test analysis with minimal project data."""
    analyzer = AdvancedCreativeAnalyzer()
    
    # Create a project with minimal data
    project = Mock()
    project.id = 1
    project.title = "Minimal Project"
    project.status = None
    project.project_type = None
    project.file_path = None
    project.dimensions = None
    project.color_palette = []
    project.extracted_text = ""
    
    # Should still work without errors
    result = await analyzer.analyze_project(project)
    
    assert isinstance(result, dict)
    assert 'overall_score' in result
    assert isinstance(result['detailed_insights'], list)
    
    # Should have some default insights even with minimal data
    assert len(result['detailed_insights']) > 0


if __name__ == "__main__":
    # Run tests
    test_analyzer_inheritance()
    test_error_handling()
    test_project_type_enum()
    
    # Run async tests
    asyncio.run(test_analyze_project_method())
    asyncio.run(test_minimal_project_analysis())
    
    print("✅ All integration tests passed!")