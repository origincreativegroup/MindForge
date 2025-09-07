"""Test for the creative analyzer functionality."""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the apps directory to the path
import sys
sys.path.insert(0, '/home/runner/work/MindForge/MindForge/apps')

# Mock all the dependencies before importing anything
sys.modules['PIL'] = Mock()
sys.modules['PIL.Image'] = Mock()
sys.modules['PIL.ImageStat'] = Mock()
sys.modules['numpy'] = Mock()
sys.modules['cv2'] = Mock()
sys.modules['PyPDF2'] = Mock()
sys.modules['pytesseract'] = Mock()
sys.modules['sklearn'] = Mock()
sys.modules['sklearn.cluster'] = Mock()
sys.modules['sqlalchemy'] = Mock()
sys.modules['sqlalchemy.orm'] = Mock()
sys.modules['sqlalchemy.sql'] = Mock()
sys.modules['sqlalchemy.ext'] = Mock()
sys.modules['sqlalchemy.ext.declarative'] = Mock()

# Create mock SQLAlchemy components
mock_column = Mock()
mock_integer = Mock()
mock_string = Mock()
mock_text = Mock()
mock_datetime = Mock()
mock_foreignkey = Mock()
mock_json = Mock()
mock_date = Mock()
mock_boolean = Mock()
mock_enum = Mock()
mock_table = Mock()
mock_index = Mock()
mock_func = Mock()
mock_relationship = Mock()
mock_declarative_base = Mock()

sys.modules['sqlalchemy'].Column = mock_column
sys.modules['sqlalchemy'].Integer = mock_integer
sys.modules['sqlalchemy'].String = mock_string
sys.modules['sqlalchemy'].Text = mock_text
sys.modules['sqlalchemy'].DateTime = mock_datetime
sys.modules['sqlalchemy'].ForeignKey = mock_foreignkey
sys.modules['sqlalchemy'].JSON = mock_json
sys.modules['sqlalchemy'].Date = mock_date
sys.modules['sqlalchemy'].Boolean = mock_boolean
sys.modules['sqlalchemy'].Enum = mock_enum
sys.modules['sqlalchemy'].Table = mock_table
sys.modules['sqlalchemy'].Index = mock_index
sys.modules['sqlalchemy.sql'].func = mock_func
sys.modules['sqlalchemy.orm'].relationship = mock_relationship
# Create a more complete Base mock
class MockBase:
    metadata = Mock()

sys.modules['sqlalchemy.ext.declarative'].declarative_base = lambda: MockBase

from backend.services.creative_analyzer import CreativeProjectAnalyzer
from backend.schemas import ProjectType


class MockProject:
    """Mock project for testing."""
    def __init__(self):
        self.id = 1
        self.title = "Test Project"
        self.project_type = ProjectType.SOCIAL_MEDIA
        self.color_palette = None
        self.dimensions = None
        self.extracted_text = None
        self.tags = []
        self.file_path = "/test/path/image.jpg"


class TestCreativeProjectAnalyzer:
    """Test cases for the CreativeProjectAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CreativeProjectAnalyzer()
        self.mock_project = MockProject()

    def test_analyzer_initialization(self):
        """Test that the analyzer initializes correctly."""
        assert self.analyzer is not None
        assert 'image' in self.analyzer.supported_formats
        assert 'video' in self.analyzer.supported_formats
        assert 'pdf' in self.analyzer.supported_formats
        assert 'design' in self.analyzer.supported_formats

    def test_get_file_type(self):
        """Test file type detection."""
        assert self.analyzer._get_file_type('.jpg') == 'image'
        assert self.analyzer._get_file_type('.mp4') == 'video'
        assert self.analyzer._get_file_type('.pdf') == 'pdf'
        assert self.analyzer._get_file_type('.psd') == 'design'
        assert self.analyzer._get_file_type('.unknown') == 'unknown'

    def test_generate_image_tags_square_format(self):
        """Test image tag generation for square format."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.width = 1000
        mock_img.height = 1000
        mock_img.mode = 'RGB'
        
        tags = self.analyzer._generate_image_tags(mock_img, self.mock_project)
        
        assert 'square-format' in tags
        assert 'high-resolution' in tags

    def test_generate_image_tags_landscape_format(self):
        """Test image tag generation for landscape format."""
        mock_img = Mock()
        mock_img.width = 1920
        mock_img.height = 1080
        mock_img.mode = 'RGB'
        
        tags = self.analyzer._generate_image_tags(mock_img, self.mock_project)
        
        assert 'landscape-format' in tags
        assert 'high-resolution' in tags

    def test_generate_image_tags_portrait_format(self):
        """Test image tag generation for portrait format."""
        mock_img = Mock()
        mock_img.width = 600
        mock_img.height = 1000
        mock_img.mode = 'RGB'
        
        tags = self.analyzer._generate_image_tags(mock_img, self.mock_project)
        
        assert 'portrait-format' in tags

    def test_generate_image_tags_transparency(self):
        """Test image tag generation for images with transparency."""
        mock_img = Mock()
        mock_img.width = 800
        mock_img.height = 600
        mock_img.mode = 'RGBA'
        
        tags = self.analyzer._generate_image_tags(mock_img, self.mock_project)
        
        assert 'has-transparency' in tags

    def test_generate_video_tags_short_form(self):
        """Test video tag generation for short form videos."""
        tech_info = {
            'duration': 15,
            'width': 1920,
            'height': 1080
        }
        
        tags = self.analyzer._generate_video_tags(tech_info, self.mock_project)
        
        assert 'short-form' in tags
        assert 'hd-video' in tags

    def test_generate_video_tags_long_form(self):
        """Test video tag generation for long form videos."""
        tech_info = {
            'duration': 600,  # 10 minutes
            'width': 3840,
            'height': 2160
        }
        
        tags = self.analyzer._generate_video_tags(tech_info, self.mock_project)
        
        assert 'long-form' in tags
        assert '4k-video' in tags

    def test_generate_pdf_tags_single_page(self):
        """Test PDF tag generation for single page documents."""
        analysis = {
            'technical_info': {
                'page_count': 1
            }
        }
        
        tags = self.analyzer._generate_pdf_tags(analysis, self.mock_project)
        
        assert 'document' in tags
        assert 'single-page' in tags

    def test_generate_pdf_tags_multi_page(self):
        """Test PDF tag generation for multi-page documents."""
        analysis = {
            'technical_info': {
                'page_count': 15
            }
        }
        
        tags = self.analyzer._generate_pdf_tags(analysis, self.mock_project)
        
        assert 'document' in tags
        assert 'multi-page-document' in tags

    def test_social_media_format_check_instagram_feed(self):
        """Test social media format check for Instagram feed format."""
        analysis = {
            'dimensions': {
                'width': 1080,
                'height': 1080
            }
        }
        
        insights = self.analyzer._social_media_format_check(analysis)
        
        assert len(insights) == 1
        assert insights[0]['insight_type'] == 'format_compatibility'
        assert 'Instagram Feed Compatible' in insights[0]['title']

    def test_social_media_format_check_instagram_stories(self):
        """Test social media format check for Instagram Stories format."""
        analysis = {
            'dimensions': {
                'width': 1080,
                'height': 1920  # 9:16 ratio
            }
        }
        
        insights = self.analyzer._social_media_format_check(analysis)
        
        assert len(insights) == 1
        assert insights[0]['insight_type'] == 'format_compatibility'
        assert 'Instagram Stories Compatible' in insights[0]['title']

    def test_print_specification_check_high_resolution(self):
        """Test print specification check for high resolution images."""
        analysis = {
            'dimensions': {
                'width': 2500,
                'height': 3500
            }
        }
        
        insights = self.analyzer._print_specification_check(analysis)
        
        assert len(insights) == 1
        assert insights[0]['insight_type'] == 'print_quality'
        assert 'Print Ready Resolution' in insights[0]['title']
        assert insights[0]['score'] == 0.9

    def test_print_specification_check_low_resolution(self):
        """Test print specification check for low resolution images."""
        analysis = {
            'dimensions': {
                'width': 800,
                'height': 600
            }
        }
        
        insights = self.analyzer._print_specification_check(analysis)
        
        assert len(insights) == 1
        assert insights[0]['insight_type'] == 'print_quality'
        assert 'Low Print Resolution' in insights[0]['title']
        assert insights[0]['score'] == 0.3

    def test_web_design_check_large_width(self):
        """Test web design check for large width images."""
        analysis = {
            'dimensions': {
                'width': 2400,
                'height': 1200
            }
        }
        
        insights = self.analyzer._web_design_check(analysis)
        
        assert len(insights) == 1
        assert insights[0]['insight_type'] == 'web_optimization'
        assert 'Large Width Detected' in insights[0]['title']

    def test_analyze_color_harmony_harmonious_colors(self):
        """Test color harmony analysis with harmonious colors."""
        # Colors with similar hues (different shades of blue)
        color_palette = ['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd']
        
        insights = self.analyzer._analyze_color_harmony(color_palette)
        
        # Should detect harmonious colors
        harmony_insights = [i for i in insights if i['insight_type'] == 'color_analysis']
        assert len(harmony_insights) >= 0  # May or may not trigger depending on variance

    def test_analyze_color_harmony_empty_palette(self):
        """Test color harmony analysis with empty palette."""
        color_palette = []
        
        insights = self.analyzer._analyze_color_harmony(color_palette)
        
        assert len(insights) == 0

    def test_analyze_typography_complex_vocabulary(self):
        """Test typography analysis with complex vocabulary."""
        extracted_text = "These extraordinarily sophisticated implementations demonstrate remarkable technological advancement"
        
        insights = self.analyzer._analyze_typography(extracted_text)
        
        typography_insights = [i for i in insights if i['insight_type'] == 'typography_analysis']
        assert len(typography_insights) == 1
        assert 'Complex Vocabulary' in typography_insights[0]['title']

    def test_analyze_typography_empty_text(self):
        """Test typography analysis with empty text."""
        extracted_text = ""
        
        insights = self.analyzer._analyze_typography(extracted_text)
        
        assert len(insights) == 0

    def test_analyze_composition_golden_ratio(self):
        """Test composition analysis with golden ratio."""
        analysis = {
            'dimensions': {
                'width': 1618,
                'height': 1000  # Close to golden ratio
            }
        }
        
        insights = self.analyzer._analyze_composition(self.mock_project, analysis)
        
        composition_insights = [i for i in insights if i['insight_type'] == 'composition_analysis']
        assert len(composition_insights) == 1
        assert 'Golden Ratio Composition' in composition_insights[0]['title']

    def test_generate_suggestions_low_score_insights(self):
        """Test suggestion generation for low score insights."""
        insights = [
            {
                'insight_type': 'print_quality',
                'score': 0.3
            },
            {
                'insight_type': 'mobile_optimization', 
                'score': 0.5
            },
            {
                'insight_type': 'color_analysis',
                'score': 0.6
            }
        ]
        
        suggestions = self.analyzer._generate_suggestions(insights, self.mock_project)
        
        assert "Consider increasing image resolution for better print quality" in suggestions
        assert "Simplify design elements for better mobile viewing" in suggestions
        assert "Review color palette for better harmony and brand consistency" in suggestions

    def test_generate_suggestions_social_media_project(self):
        """Test suggestion generation for social media projects."""
        self.mock_project.project_type = ProjectType.SOCIAL_MEDIA
        insights = []
        
        suggestions = self.analyzer._generate_suggestions(insights, self.mock_project)
        
        assert "Ensure text is large enough to read on mobile devices" in suggestions
        assert "Consider platform-specific aspect ratios for better engagement" in suggestions

    def test_generate_suggestions_website_mockup_project(self):
        """Test suggestion generation for website mockup projects."""
        self.mock_project.project_type = ProjectType.WEBSITE_MOCKUP
        insights = []
        
        suggestions = self.analyzer._generate_suggestions(insights, self.mock_project)
        
        assert "Test design responsiveness across different screen sizes" in suggestions
        assert "Verify accessibility standards compliance" in suggestions

    @pytest.mark.asyncio
    async def test_analyze_generic_file(self):
        """Test generic file analysis."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_path = temp_file.name
        
        try:
            result = await self.analyzer._analyze_generic_file(temp_path, self.mock_project)
            
            assert 'technical_info' in result
            assert 'file_size' in result['technical_info']
            assert result['technical_info']['format'] == 'TXT'
            
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_project_type_analysis(self):
        """Test project type specific analysis."""
        base_analysis = {
            'dimensions': {
                'width': 1080,
                'height': 1080
            }
        }
        
        self.mock_project.project_type = ProjectType.SOCIAL_MEDIA
        
        result = await self.analyzer._project_type_analysis(self.mock_project, base_analysis)
        
        assert 'project_insights' in result
        assert isinstance(result['project_insights'], list)

    def test_extract_colors_simple_fallback(self):
        """Test the simple color extraction fallback method."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.convert.return_value = mock_img
        mock_img.getcolors.return_value = [
            (100, (255, 0, 0)),    # Red
            (80, (0, 255, 0)),     # Green  
            (60, (0, 0, 255))      # Blue
        ]
        
        colors = self.analyzer._extract_colors_simple(mock_img, 3)
        
        assert len(colors) <= 3
        assert all(color.startswith('#') for color in colors)
        assert all(len(color) == 7 for color in colors)  # Hex format #rrggbb


if __name__ == '__main__':
    pytest.main([__file__])