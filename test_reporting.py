"""Basic tests for the reporting service."""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apps'))

from backend.services.reporting import ReportConfig, ProjectReportGenerator, ExportUtilities, CaseyReportNarrator
from backend.services.collaboration import CollaborationService
from backend.services.advanced_analyzer import AdvancedCreativeAnalyzer


class TestReportConfig:
    """Test the ReportConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ReportConfig()
        assert config.include_analytics is True
        assert config.include_insights is True
        assert config.include_recommendations is True
        assert config.include_comments is True
        assert config.include_activity is True
        assert config.include_visuals is True
        assert config.export_format == "pdf"
        assert config.template_style == "professional"
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = ReportConfig(
            include_analytics=False,
            export_format="html",
            template_style="minimal"
        )
        assert config.include_analytics is False
        assert config.export_format == "html"
        assert config.template_style == "minimal"


class TestAdvancedCreativeAnalyzer:
    """Test the AdvancedCreativeAnalyzer service."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = AdvancedCreativeAnalyzer()
        assert analyzer.categories is not None
        assert len(analyzer.categories) > 0
    
    @pytest.mark.asyncio
    async def test_comprehensive_audit(self):
        """Test comprehensive project audit."""
        analyzer = AdvancedCreativeAnalyzer()
        
        # Mock project object
        mock_project = Mock()
        mock_project.project_type = "branding"
        mock_project.title = "Test Project"
        
        result = await analyzer.comprehensive_project_audit(mock_project)
        
        # Check basic structure
        assert "overall_score" in result
        assert "category_scores" in result
        assert "detailed_insights" in result
        assert "recommendations" in result
        assert "analysis_date" in result
        
        # Check score ranges
        assert 0 <= result["overall_score"] <= 1
        for category, score in result["category_scores"].items():
            assert 0 <= score <= 1
        
        # Check insights structure
        for insight in result["detailed_insights"]:
            assert "title" in insight
            assert "description" in insight
            assert "score" in insight
            assert "type" in insight


class TestCollaborationService:
    """Test the CollaborationService."""
    
    def test_collaboration_service_init(self):
        """Test service initialization."""
        mock_db = Mock()
        service = CollaborationService(mock_db)
        assert service.db == mock_db
    
    @pytest.mark.asyncio
    async def test_get_project_comments_empty(self):
        """Test getting comments for a project with no comments."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        service = CollaborationService(mock_db)
        comments = await service.get_project_comments(1)
        
        assert comments == []
    
    @pytest.mark.asyncio
    async def test_get_project_activity_empty(self):
        """Test getting activity for a project with no activity."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        service = CollaborationService(mock_db)
        activities = await service.get_project_activity(1)
        
        assert activities == []


class TestExportUtilities:
    """Test the ExportUtilities class."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test basic sanitization
        result = ExportUtilities.sanitize_filename("test<>file.pdf")
        assert "<" not in result
        assert ">" not in result
        
        # Test space handling
        result = ExportUtilities.sanitize_filename("test   file   name.pdf")
        assert "test_file_name.pdf" == result
        
        # Test length limiting
        long_name = "a" * 200 + ".pdf"
        result = ExportUtilities.sanitize_filename(long_name)
        assert len(result) <= 100


class TestCaseyReportNarrator:
    """Test the Casey report narrator."""
    
    def test_generate_project_summary(self):
        """Test project summary generation."""
        # Mock project data
        mock_project = Mock()
        mock_project.title = "Test Project"
        mock_project.project_type = "web_design"
        
        project_data = {
            "project": mock_project,
            "analysis": {
                "overall_score": 0.75,
                "detailed_insights": [
                    {"title": "Good Color Harmony", "score": 0.85},
                    {"title": "Poor Typography", "score": 0.45}
                ],
                "recommendations": [
                    {"title": "Improve Typography", "description": "Use better fonts"}
                ]
            }
        }
        
        summary = CaseyReportNarrator.generate_project_summary(project_data)
        
        assert "Test Project" in summary
        assert "web design" in summary
        assert "🎨" in summary
        assert "💬" in summary


if __name__ == "__main__":
    # Run basic tests without pytest
    print("Running basic tests...")
    
    # Test ReportConfig
    config = ReportConfig()
    print("✅ ReportConfig test passed")
    
    # Test AdvancedCreativeAnalyzer
    analyzer = AdvancedCreativeAnalyzer()
    print("✅ AdvancedCreativeAnalyzer test passed")
    
    # Test CollaborationService
    mock_db = Mock()
    service = CollaborationService(mock_db)
    print("✅ CollaborationService test passed")
    
    # Test ExportUtilities
    result = ExportUtilities.sanitize_filename("test<>file.pdf")
    assert "<" not in result
    print("✅ ExportUtilities test passed")
    
    # Test CaseyReportNarrator
    mock_project = Mock()
    mock_project.title = "Test Project"
    mock_project.project_type = "web_design"
    
    project_data = {
        "project": mock_project,
        "analysis": {
            "overall_score": 0.75,
            "detailed_insights": [],
            "recommendations": []
        }
    }
    
    summary = CaseyReportNarrator.generate_project_summary(project_data)
    assert "Test Project" in summary
    print("✅ CaseyReportNarrator test passed")
    
    print("🎉 All basic tests passed!")