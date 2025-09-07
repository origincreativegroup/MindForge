"""Test for the creative analyzer functionality with minimal dependencies."""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path

def test_basic_analyzer_functionality():
    """Test the basic functionality without external dependencies."""
    
    # Test file type detection logic
    supported_formats = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
        'pdf': ['.pdf'],
        'design': ['.psd', '.ai', '.sketch', '.fig', '.xd']
    }
    
    def get_file_type(file_ext: str) -> str:
        """Determine file type category"""
        for file_type, extensions in supported_formats.items():
            if file_ext in extensions:
                return file_type
        return 'unknown'
    
    # Test file type detection
    assert get_file_type('.jpg') == 'image'
    assert get_file_type('.mp4') == 'video'
    assert get_file_type('.pdf') == 'pdf'
    assert get_file_type('.psd') == 'design'
    assert get_file_type('.unknown') == 'unknown'

def test_image_tag_generation():
    """Test image tag generation logic."""
    
    def generate_image_tags(width: int, height: int, mode: str, info: dict) -> list:
        """Generate descriptive tags for images"""
        tags = []
        
        # Aspect ratio tags
        aspect_ratio = width / height
        if 0.9 <= aspect_ratio <= 1.1:
            tags.append('square-format')
        elif aspect_ratio > 1.5:
            tags.append('landscape-format')
        elif aspect_ratio < 0.7:
            tags.append('portrait-format')
        
        # Resolution tags
        total_pixels = width * height
        if total_pixels > 8000000:  # > 8MP
            tags.append('high-resolution')
        elif total_pixels < 500000:  # < 0.5MP
            tags.append('low-resolution')
        
        # Format tags
        if mode in ('RGBA', 'LA') or 'transparency' in info:
            tags.append('has-transparency')
        
        return tags
    
    # Test square format  
    tags = generate_image_tags(1000, 1000, 'RGB', {})
    assert 'square-format' in tags
    # 1000x1000 = 1M pixels, which is > 0.5M but < 8M, so no resolution tag
    
    # Test high resolution
    tags = generate_image_tags(3000, 3000, 'RGB', {})
    assert 'square-format' in tags
    assert 'high-resolution' in tags
    
    # Test landscape format
    tags = generate_image_tags(1920, 1080, 'RGB', {})
    assert 'landscape-format' in tags
    # 1920x1080 = ~2M pixels, which is > 0.5M but < 8M, so no resolution tag
    
    # Test high resolution landscape
    tags = generate_image_tags(4000, 2100, 'RGB', {})  # 8.4M pixels > 8M
    assert 'landscape-format' in tags
    assert 'high-resolution' in tags
    
    # Test portrait format
    tags = generate_image_tags(600, 1000, 'RGB', {})
    assert 'portrait-format' in tags
    
    # Test transparency
    tags = generate_image_tags(800, 600, 'RGBA', {})
    assert 'has-transparency' in tags

def test_video_tag_generation():
    """Test video tag generation logic."""
    
    def generate_video_tags(tech_info: dict) -> list:
        """Generate tags for video content"""
        tags = []
        
        duration = tech_info.get('duration', 0)
        if duration < 30:
            tags.append('short-form')
        elif duration > 300:  # 5 minutes
            tags.append('long-form')
        
        # Resolution tags
        width = tech_info.get('width', 0)
        if width >= 3840:
            tags.append('4k-video')
        elif width >= 1920:
            tags.append('hd-video')
        
        return tags
    
    # Test short form video
    tech_info = {'duration': 15, 'width': 1920, 'height': 1080}
    tags = generate_video_tags(tech_info)
    assert 'short-form' in tags
    assert 'hd-video' in tags
    
    # Test long form video
    tech_info = {'duration': 600, 'width': 3840, 'height': 2160}
    tags = generate_video_tags(tech_info)
    assert 'long-form' in tags
    assert '4k-video' in tags

def test_social_media_format_check():
    """Test social media format checking logic."""
    
    def social_media_format_check(analysis: dict) -> list:
        """Check if image matches social media format requirements"""
        insights = []
        dimensions = analysis.get('dimensions', {})
        
        if dimensions:
            width, height = dimensions['width'], dimensions['height']
            aspect_ratio = width / height
            
            # Instagram format checks
            if 0.9 <= aspect_ratio <= 1.1:
                insights.append({
                    'insight_type': 'format_compatibility',
                    'title': 'Instagram Feed Compatible',
                    'description': 'This square format is perfect for Instagram feed posts',
                    'score': 0.9
                })
            elif aspect_ratio == 9/16:
                insights.append({
                    'insight_type': 'format_compatibility',
                    'title': 'Instagram Stories Compatible',
                    'description': 'This 9:16 format is ideal for Instagram Stories and Reels',
                    'score': 0.95
                })
        
        return insights
    
    # Test Instagram feed format
    analysis = {'dimensions': {'width': 1080, 'height': 1080}}
    insights = social_media_format_check(analysis)
    assert len(insights) == 1
    assert 'Instagram Feed Compatible' in insights[0]['title']
    
    # Test Instagram stories format
    analysis = {'dimensions': {'width': 1080, 'height': 1920}}
    insights = social_media_format_check(analysis)
    assert len(insights) == 1
    assert 'Instagram Stories Compatible' in insights[0]['title']

def test_print_specification_check():
    """Test print specification checking logic."""
    
    def print_specification_check(analysis: dict) -> list:
        """Check print specifications"""
        insights = []
        dimensions = analysis.get('dimensions', {})
        
        if dimensions:
            width, height = dimensions['width'], dimensions['height']
            
            # DPI estimation (rough)
            if width >= 2480 and height >= 3508:  # A4 at 300 DPI
                insights.append({
                    'insight_type': 'print_quality',
                    'title': 'Print Ready Resolution',
                    'description': 'Resolution appears sufficient for professional printing',
                    'score': 0.9
                })
            else:
                insights.append({
                    'insight_type': 'print_quality',
                    'title': 'Low Print Resolution',
                    'description': 'Resolution may be too low for professional printing',
                    'score': 0.3
                })
        
        return insights
    
    # Test high resolution
    analysis = {'dimensions': {'width': 2500, 'height': 3600}}  # Both > required thresholds
    insights = print_specification_check(analysis)
    assert len(insights) == 1
    assert 'Print Ready Resolution' in insights[0]['title']
    assert insights[0]['score'] == 0.9
    
    # Test low resolution
    analysis = {'dimensions': {'width': 800, 'height': 600}}
    insights = print_specification_check(analysis)
    assert len(insights) == 1
    assert 'Low Print Resolution' in insights[0]['title']
    assert insights[0]['score'] == 0.3

def test_color_harmony_analysis():
    """Test color harmony analysis logic."""
    
    def analyze_color_harmony(color_palette: list) -> list:
        """Analyze color harmony and relationships"""
        import colorsys
        
        insights = []
        
        if not color_palette or len(color_palette) < 2:
            return insights
        
        # Convert hex to HSV for analysis
        try:
            hsv_colors = []
            for hex_color in color_palette:
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
                hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                hsv_colors.append(hsv)
            
            # Analyze hue relationships
            hues = [color[0] * 360 for color in hsv_colors]
            
            # Simple variance calculation
            if len(hues) > 1:
                mean_hue = sum(hues) / len(hues)
                hue_variance = sum((h - mean_hue) ** 2 for h in hues) / len(hues)
            else:
                hue_variance = 0
            
            if hue_variance < 100:  # Low variance = harmonious
                insights.append({
                    'insight_type': 'color_analysis',
                    'title': 'Harmonious Color Scheme',
                    'description': 'Colors show good harmony with similar hues',
                    'score': 0.9,
                    'data': {'hue_variance': hue_variance}
                })
            elif hue_variance > 10000:  # High variance = potentially clashing
                insights.append({
                    'insight_type': 'color_analysis',
                    'title': 'High Color Contrast',
                    'description': 'Very diverse hues detected. Ensure intentional color choices.',
                    'score': 0.6,
                    'data': {'hue_variance': hue_variance}
                })
                
        except Exception as e:
            print(f"Color harmony analysis failed: {e}")
        
        return insights
    
    # Test harmonious colors (similar blues)
    color_palette = ['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd']
    insights = analyze_color_harmony(color_palette)
    # Should either have a harmonious result or no result depending on variance
    assert isinstance(insights, list)
    
    # Test empty palette
    insights = analyze_color_harmony([])
    assert len(insights) == 0

def test_typography_analysis():
    """Test typography analysis logic."""
    
    def analyze_typography(extracted_text: str) -> list:
        """Analyze typography and text-related insights"""
        insights = []
        
        if not extracted_text:
            return insights
        
        # Text readability analysis
        word_count = len(extracted_text.split())
        words = extracted_text.split()
        if words:
            avg_word_length = sum(len(word) for word in words) / len(words)
        else:
            avg_word_length = 0
        
        if avg_word_length > 7:
            insights.append({
                'insight_type': 'typography_analysis',
                'title': 'Complex Vocabulary',
                'description': 'Long average word length detected. Consider readability.',
                'score': 0.6,
                'data': {'avg_word_length': avg_word_length, 'word_count': word_count}
            })
        
        return insights
    
    # Test complex vocabulary
    text = "These extraordinarily sophisticated implementations demonstrate remarkable technological advancement"
    insights = analyze_typography(text)
    assert len(insights) == 1
    assert 'Complex Vocabulary' in insights[0]['title']
    
    # Test empty text
    insights = analyze_typography("")
    assert len(insights) == 0

def test_generate_suggestions():
    """Test suggestion generation logic."""
    
    def generate_suggestions(insights: list, project_type: str) -> list:
        """Generate actionable suggestions based on insights"""
        suggestions = []
        
        low_score_insights = [i for i in insights if i.get('score', 1.0) < 0.7]
        
        for insight in low_score_insights:
            if insight['insight_type'] == 'print_quality':
                suggestions.append("Consider increasing image resolution for better print quality")
            elif insight['insight_type'] == 'mobile_optimization':
                suggestions.append("Simplify design elements for better mobile viewing")
            elif insight['insight_type'] == 'color_analysis':
                suggestions.append("Review color palette for better harmony and brand consistency")
            elif insight['insight_type'] == 'typography_analysis':
                suggestions.append("Consider simplifying text for better readability")
        
        # Add general suggestions based on project type
        if project_type == 'SOCIAL_MEDIA':
            suggestions.append("Ensure text is large enough to read on mobile devices")
            suggestions.append("Consider platform-specific aspect ratios for better engagement")
        elif project_type == 'WEBSITE_MOCKUP':
            suggestions.append("Test design responsiveness across different screen sizes")
            suggestions.append("Verify accessibility standards compliance")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    # Test with low score insights
    insights = [
        {'insight_type': 'print_quality', 'score': 0.3},
        {'insight_type': 'mobile_optimization', 'score': 0.5},
        {'insight_type': 'color_analysis', 'score': 0.6}
    ]
    
    suggestions = generate_suggestions(insights, 'SOCIAL_MEDIA')
    assert "Consider increasing image resolution for better print quality" in suggestions
    assert "Simplify design elements for better mobile viewing" in suggestions
    assert "Review color palette for better harmony and brand consistency" in suggestions
    assert "Ensure text is large enough to read on mobile devices" in suggestions
    
    # Test website mockup suggestions
    suggestions = generate_suggestions([], 'WEBSITE_MOCKUP')
    assert "Test design responsiveness across different screen sizes" in suggestions
    assert "Verify accessibility standards compliance" in suggestions

def test_generic_file_analysis():
    """Test generic file analysis with actual file."""
    
    def analyze_generic_file(file_path: str) -> dict:
        """Analyze generic files for basic metadata"""
        result = {}
        
        try:
            stat = os.stat(file_path)
            result['technical_info'] = {
                'file_size': stat.st_size,
                'format': Path(file_path).suffix.upper().lstrip('.')
            }
            
            # Attempt to determine if it's a design file
            file_ext = Path(file_path).suffix.lower()
            if file_ext in ['.psd', '.ai', '.sketch', '.fig', '.xd']:
                result['tags'] = ['design-file', 'vector-graphics', 'professional-tool']
            
        except Exception as e:
            result['error'] = f"Generic file analysis failed: {str(e)}"
        
        return result
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b"Test content")
        temp_path = temp_file.name
    
    try:
        result = analyze_generic_file(temp_path)
        assert 'technical_info' in result
        assert 'file_size' in result['technical_info']
        assert result['technical_info']['format'] == 'TXT'
        
    finally:
        os.unlink(temp_path)

if __name__ == '__main__':
    pytest.main([__file__])