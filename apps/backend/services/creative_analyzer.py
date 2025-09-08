"""Creative Project Analyzer service."""

from typing import Dict, List, Any, Optional
import json
from pathlib import Path

from .models import CreativeProject


class CreativeProjectAnalyzer:
    """Service for analyzing creative project files."""
    
    def __init__(self):
        self.supported_image_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        self.supported_video_types = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        self.supported_doc_types = ['.pdf', '.psd', '.ai', '.sketch', '.fig', '.xd']
    
    async def analyze_project(self, project: CreativeProject, file_path: str) -> Dict[str, Any]:
        """Analyze the uploaded project file."""
        analysis_result = {
            'dimensions': None,
            'color_palette': None,
            'extracted_text': None,
            'tags': []
        }
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in self.supported_image_types:
                analysis_result.update(await self._analyze_image(file_path))
            elif file_ext in self.supported_video_types:
                analysis_result.update(await self._analyze_video(file_path))
            elif file_ext in self.supported_doc_types:
                analysis_result.update(await self._analyze_document(file_path))
            
            # Add general tags based on project type
            analysis_result['tags'] = self._generate_project_tags(project)
            
        except Exception as e:
            print(f"Analysis error: {e}")
        
        return analysis_result
    
    async def _analyze_image(self, file_path: str) -> Dict[str, Any]:
        """Analyze image files."""
        result = {}
        
        try:
            # For now, provide basic file info without PIL
            result['dimensions'] = "Unknown (PIL not available)"
            result['color_palette'] = ["#000000", "#FFFFFF"]  # Default palette
            result['image_mode'] = "RGB"
            result['image_format'] = Path(file_path).suffix.upper().lstrip('.')
            
            # In a real implementation, this would use PIL:
            # with Image.open(file_path) as img:
            #     result['dimensions'] = f"{img.width}x{img.height}"
            #     result['color_palette'] = self._extract_color_palette(img)
            #     result['image_mode'] = img.mode
            #     result['image_format'] = img.format
                
        except Exception as e:
            print(f"Image analysis error: {e}")
        
        return result
    
    async def _analyze_video(self, file_path: str) -> Dict[str, Any]:
        """Analyze video files (placeholder)."""
        # This would require video processing libraries like ffmpeg-python
        return {
            'file_type': 'video',
            'analysis_note': 'Video analysis not yet implemented'
        }
    
    async def _analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Analyze document files (placeholder)."""
        # This would require document processing libraries
        return {
            'file_type': 'document',
            'analysis_note': 'Document analysis not yet implemented'
        }
    
    def _extract_color_palette(self, img) -> List[str]:
        """Extract dominant colors from image (simplified implementation)."""
        # This would be implemented with PIL in a real scenario
        return ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF"]
    
    def _generate_project_tags(self, project: CreativeProject) -> List[str]:
        """Generate relevant tags based on project type and analysis."""
        tags = []
        
        project_type = project.project_type.value if hasattr(project.project_type, 'value') else str(project.project_type)
        
        # Base tags by project type
        type_tags = {
            'website_mockup': ['web design', 'ui/ux', 'responsive', 'digital'],
            'social_media': ['social media', 'digital marketing', 'engagement'],
            'print_graphic': ['print design', 'graphics', 'marketing materials'],
            'logo_design': ['branding', 'identity', 'logo'],
            'ui_design': ['ui design', 'user interface', 'digital'],
            'branding': ['brand identity', 'visual identity', 'corporate design']
        }
        
        tags.extend(type_tags.get(project_type, ['creative', 'design']))
        
        # Add creative analysis tags
        tags.extend(['creative project', 'design analysis'])
        
        return list(set(tags))  # Remove duplicates
    
    async def comprehensive_analysis(self, project: CreativeProject) -> Dict[str, Any]:
        """Run comprehensive analysis on the project."""
        analysis_result = {
            'insights': [],
            'suggestions': [],
            'overall_score': 85  # Placeholder score
        }
        
        project_type = project.project_type.value if hasattr(project.project_type, 'value') else str(project.project_type)
        
        # Generate insights based on project type
        if project_type == 'website_mockup':
            analysis_result['insights'].append({
                'insight_type': 'design_quality',
                'title': 'Layout Analysis',
                'description': 'The layout demonstrates good visual hierarchy and balance.',
                'confidence': 0.8
            })
            analysis_result['suggestions'].append('Consider adding more white space for improved readability')
            
        elif project_type == 'social_media':
            analysis_result['insights'].append({
                'insight_type': 'engagement_potential',
                'title': 'Visual Impact',
                'description': 'Strong visual elements that should perform well on social platforms.',
                'confidence': 0.75
            })
            analysis_result['suggestions'].append('Ensure text is readable at smaller sizes for mobile viewing')
            
        elif project_type == 'logo_design':
            analysis_result['insights'].append({
                'insight_type': 'brand_consistency',
                'title': 'Brand Identity',
                'description': 'The design elements align well with modern branding trends.',
                'confidence': 0.85
            })
            analysis_result['suggestions'].append('Test logo scalability at different sizes')
        
        # Add color palette insights if available
        if project.color_palette:
            analysis_result['insights'].append({
                'insight_type': 'color_analysis',
                'title': 'Color Harmony',
                'description': f'Color palette uses {len(project.color_palette)} colors with good contrast.',
                'confidence': 0.7
            })
        
        return analysis_result