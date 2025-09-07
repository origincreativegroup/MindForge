import os
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import mimetypes
import colorsys
from collections import Counter

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image, ImageStat
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from ..models import Project as CreativeProject
from ..schemas import ProjectType

class CreativeProjectAnalyzer:
    """Analyzes uploaded creative files to extract insights and metadata"""

    def __init__(self):
        self.supported_formats = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
            'pdf': ['.pdf'],
            'design': ['.psd', '.ai', '.sketch', '.fig', '.xd']
        }

    async def analyze_project(self, project: CreativeProject, file_path: str) -> Dict[str, Any]:
        """Main analysis function that routes to specific analyzers"""
        
        file_ext = Path(file_path).suffix.lower()
        analysis_result = {
            'file_type': self._get_file_type(file_ext),
            'dimensions': None,
            'color_palette': None,
            'extracted_text': None,
            'tags': [],
            'insights': [],
            'technical_info': {}
        }
        
        try:
            if file_ext in self.supported_formats['image']:
                analysis_result.update(await self._analyze_image(file_path, project))
            elif file_ext in self.supported_formats['video']:
                analysis_result.update(await self._analyze_video(file_path, project))
            elif file_ext in self.supported_formats['pdf']:
                analysis_result.update(await self._analyze_pdf(file_path, project))
            else:
                analysis_result.update(await self._analyze_generic_file(file_path, project))
                
        except Exception as e:
            print(f"Analysis error: {e}")
            analysis_result['error'] = str(e)
        
        # Add project-type specific analysis
        analysis_result.update(await self._project_type_analysis(project, analysis_result))
        
        return analysis_result

    async def comprehensive_analysis(self, project: CreativeProject) -> Dict[str, Any]:
        """Run comprehensive analysis including design principles evaluation"""
        
        # Get base analysis if not already done
        if not project.color_palette and not project.dimensions:
            base_analysis = await self.analyze_project(project, project.file_path)
        else:
            base_analysis = {
                'color_palette': project.color_palette,
                'dimensions': project.dimensions,
                'extracted_text': project.extracted_text,
                'tags': project.tags or []
            }
        
        insights = []
        suggestions = []
        
        # Design principle analysis
        if project.project_type == ProjectType.WEBSITE_MOCKUP:
            insights.extend(self._analyze_web_design_principles(project, base_analysis))
        elif project.project_type == ProjectType.SOCIAL_MEDIA:
            insights.extend(self._analyze_social_media_best_practices(project, base_analysis))
        elif project.project_type == ProjectType.PRINT_GRAPHIC:
            insights.extend(self._analyze_print_design_principles(project, base_analysis))
        elif project.project_type == ProjectType.BRANDING:
            insights.extend(self._analyze_branding_guidelines(project, base_analysis))
        
        # General design analysis
        insights.extend(self._analyze_color_harmony(base_analysis.get('color_palette', [])))
        insights.extend(self._analyze_typography(base_analysis.get('extracted_text', '')))
        insights.extend(self._analyze_composition(project, base_analysis))
        
        # Generate suggestions based on insights
        suggestions = self._generate_suggestions(insights, project)
        
        return {
            'insights': insights,
            'suggestions': suggestions,
            'analysis_complete': True
        }

    async def _analyze_image(self, file_path: str, project: CreativeProject) -> Dict[str, Any]:
        """Analyze image files for dimensions, colors, text, etc."""
        result = {}
        
        if not PIL_AVAILABLE:
            result['error'] = "PIL not available for image analysis"
            return result
        
        try:
            with Image.open(file_path) as img:
                # Basic image info
                result['dimensions'] = {'width': img.width, 'height': img.height}
                result['technical_info'] = {
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
                
                # Color palette extraction
                result['color_palette'] = self._extract_color_palette(img)
                
                # Text extraction using OCR
                if TESSERACT_AVAILABLE:
                    try:
                        extracted_text = pytesseract.image_to_string(img)
                        if extracted_text.strip():
                            result['extracted_text'] = extracted_text.strip()
                    except Exception as e:
                        print(f"OCR failed: {e}")
                
                # Generate tags based on analysis
                result['tags'] = self._generate_image_tags(img, project)
                
        except Exception as e:
            result['error'] = f"Image analysis failed: {str(e)}"
        
        return result

    async def _analyze_video(self, file_path: str, project: CreativeProject) -> Dict[str, Any]:
        """Analyze video files for basic metadata"""
        result = {}
        
        if not OPENCV_AVAILABLE:
            result['error'] = "OpenCV not available for video analysis"
            return result
        
        try:
            cap = cv2.VideoCapture(file_path)
            
            # Basic video info
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            result['dimensions'] = {'width': width, 'height': height}
            result['technical_info'] = {
                'fps': fps,
                'duration': duration,
                'frame_count': frame_count
            }
            
            # Extract color palette from first frame
            ret, frame = cap.read()
            if ret and PIL_AVAILABLE:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                result['color_palette'] = self._extract_color_palette(pil_image)
            
            cap.release()
            
            # Generate video-specific tags
            result['tags'] = self._generate_video_tags(result['technical_info'], project)
            
        except Exception as e:
            result['error'] = f"Video analysis failed: {str(e)}"
        
        return result

    async def _analyze_pdf(self, file_path: str, project: CreativeProject) -> Dict[str, Any]:
        """Analyze PDF files for text content and basic info"""
        result = {}
        
        if not PDF_AVAILABLE:
            result['error'] = "PyPDF2 not available for PDF analysis"
            return result
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Basic PDF info
                num_pages = len(pdf_reader.pages)
                result['technical_info'] = {
                    'page_count': num_pages,
                    'format': 'PDF'
                }
                
                # Extract text from all pages
                text_content = []
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())
                
                if text_content:
                    result['extracted_text'] = '\n'.join(text_content).strip()
                
                # Generate PDF-specific tags
                result['tags'] = self._generate_pdf_tags(result, project)
                
        except Exception as e:
            result['error'] = f"PDF analysis failed: {str(e)}"
        
        return result

    async def _analyze_generic_file(self, file_path: str, project: CreativeProject) -> Dict[str, Any]:
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

    def _extract_color_palette(self, img, num_colors: int = 8) -> List[str]:
        """Extract dominant colors from an image"""
        if not PIL_AVAILABLE:
            return []
            
        try:
            # Resize image for faster processing
            img_small = img.resize((150, 150))
            
            # Convert to RGB if necessary
            if img_small.mode != 'RGB':
                img_small = img_small.convert('RGB')
            
            # Use k-means clustering to find dominant colors if numpy and sklearn are available
            if NUMPY_AVAILABLE:
                try:
                    # Get pixel data
                    pixels = np.array(img_small).reshape(-1, 3)
                    
                    from sklearn.cluster import KMeans
                    
                    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
                    kmeans.fit(pixels)
                    
                    # Convert colors to hex
                    colors = []
                    for color in kmeans.cluster_centers_:
                        hex_color = '#{:02x}{:02x}{:02x}'.format(
                            int(color[0]), int(color[1]), int(color[2])
                        )
                        colors.append(hex_color)
                    
                    return colors
                except ImportError:
                    # Fallback method without sklearn
                    pass
            
            # Fallback method without numpy/sklearn
            return self._extract_colors_simple(img, num_colors)
            
        except Exception as e:
            print(f"Color extraction failed: {e}")
            return []

    def _extract_colors_simple(self, img, num_colors: int = 8) -> List[str]:
        """Simple color extraction without ML libraries"""
        if not PIL_AVAILABLE:
            return []
            
        try:
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get all colors and count frequency
            colors = img.getcolors(256 * 256 * 256)
            
            if not colors:
                return []
            
            # Sort by frequency and take top colors
            colors.sort(key=lambda x: x[0], reverse=True)
            
            # Convert to hex
            hex_colors = []
            for count, color in colors[:num_colors]:
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                hex_colors.append(hex_color)
            
            return hex_colors
            
        except Exception as e:
            print(f"Simple color extraction failed: {e}")
            return []

    def _get_file_type(self, file_ext: str) -> str:
        """Determine file type category"""
        for file_type, extensions in self.supported_formats.items():
            if file_ext in extensions:
                return file_type
        return 'unknown'

    def _generate_image_tags(self, img, project: CreativeProject) -> List[str]:
        """Generate descriptive tags for images"""
        if not PIL_AVAILABLE:
            return []
            
        tags = []
        
        # Aspect ratio tags
        aspect_ratio = img.width / img.height
        if 0.9 <= aspect_ratio <= 1.1:
            tags.append('square-format')
        elif aspect_ratio > 1.5:
            tags.append('landscape-format')
        elif aspect_ratio < 0.7:
            tags.append('portrait-format')
        
        # Resolution tags
        total_pixels = img.width * img.height
        if total_pixels > 8000000:  # > 8MP
            tags.append('high-resolution')
        elif total_pixels < 500000:  # < 0.5MP
            tags.append('low-resolution')
        
        # Format tags
        if img.mode in ('RGBA', 'LA') or 'transparency' in img.info:
            tags.append('has-transparency')
        
        return tags

    def _generate_video_tags(self, tech_info: Dict, project: CreativeProject) -> List[str]:
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

    def _generate_pdf_tags(self, analysis: Dict, project: CreativeProject) -> List[str]:
        """Generate tags for PDF content"""
        tags = ['document']
        
        page_count = analysis.get('technical_info', {}).get('page_count', 0)
        if page_count == 1:
            tags.append('single-page')
        elif page_count > 10:
            tags.append('multi-page-document')
        
        return tags

    async def _project_type_analysis(self, project: CreativeProject, base_analysis: Dict) -> Dict[str, Any]:
        """Add project-type specific analysis"""
        additional_insights = []
        
        if project.project_type == ProjectType.SOCIAL_MEDIA:
            additional_insights.extend(self._social_media_format_check(base_analysis))
        elif project.project_type == ProjectType.PRINT_GRAPHIC:
            additional_insights.extend(self._print_specification_check(base_analysis))
        elif project.project_type == ProjectType.WEBSITE_MOCKUP:
            additional_insights.extend(self._web_design_check(base_analysis))
        
        return {'project_insights': additional_insights}

    def _social_media_format_check(self, analysis: Dict) -> List[Dict]:
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

    def _print_specification_check(self, analysis: Dict) -> List[Dict]:
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

    def _web_design_check(self, analysis: Dict) -> List[Dict]:
        """Check web design considerations"""
        insights = []
        
        # Check if responsive-friendly
        dimensions = analysis.get('dimensions', {})
        if dimensions and dimensions['width'] > 1920:
            insights.append({
                'insight_type': 'web_optimization',
                'title': 'Large Width Detected',
                'description': 'Consider responsive design for mobile devices',
                'score': 0.6
            })
        
        return insights

    def _analyze_web_design_principles(self, project: CreativeProject, analysis: Dict) -> List[Dict]:
        """Analyze web design principles"""
        insights = []
        
        # Visual hierarchy analysis
        if analysis.get('extracted_text'):
            text_length = len(analysis['extracted_text'])
            if text_length > 500:
                insights.append({
                    'insight_type': 'design_analysis',
                    'title': 'Text Density Analysis',
                    'description': 'High text density detected. Consider breaking content into sections.',
                    'score': 0.7,
                    'data': {'text_length': text_length}
                })
        
        return insights

    def _analyze_social_media_best_practices(self, project: CreativeProject, analysis: Dict) -> List[Dict]:
        """Analyze social media best practices"""
        insights = []
        
        # Color contrast for mobile viewing
        colors = analysis.get('color_palette', [])
        if len(colors) > 6:
            insights.append({
                'insight_type': 'mobile_optimization',
                'title': 'Color Complexity',
                'description': 'Many colors detected. Consider simplifying for mobile viewing.',
                'score': 0.6,
                'data': {'color_count': len(colors)}
            })
        
        return insights

    def _analyze_print_design_principles(self, project: CreativeProject, analysis: Dict) -> List[Dict]:
        """Analyze print design principles"""
        insights = []
        
        # CMYK vs RGB analysis
        tech_info = analysis.get('technical_info', {})
        if tech_info.get('mode') == 'RGB':
            insights.append({
                'insight_type': 'print_preparation',
                'title': 'Color Mode Warning',
                'description': 'RGB mode detected. Consider converting to CMYK for print.',
                'score': 0.5,
                'data': {'current_mode': 'RGB', 'recommended_mode': 'CMYK'}
            })
        
        return insights

    def _analyze_branding_guidelines(self, project: CreativeProject, analysis: Dict) -> List[Dict]:
        """Analyze branding consistency"""
        insights = []
        
        # Color palette consistency
        colors = analysis.get('color_palette', [])
        if len(colors) < 3:
            insights.append({
                'insight_type': 'brand_consistency',
                'title': 'Limited Color Palette',
                'description': 'Very few colors detected. Consider if this aligns with brand guidelines.',
                'score': 0.7,
                'data': {'color_count': len(colors)}
            })
        
        return insights

    def _analyze_color_harmony(self, color_palette: List[str]) -> List[Dict]:
        """Analyze color harmony and relationships"""
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
            if NUMPY_AVAILABLE:
                hue_variance = np.var(hues) if len(hues) > 1 else 0
            else:
                # Simple variance calculation without numpy
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

    def _analyze_typography(self, extracted_text: str) -> List[Dict]:
        """Analyze typography and text-related insights"""
        insights = []
        
        if not extracted_text:
            return insights
        
        # Text readability analysis
        word_count = len(extracted_text.split())
        words = extracted_text.split()
        if words:
            if NUMPY_AVAILABLE:
                avg_word_length = np.mean([len(word) for word in words])
            else:
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

    def _analyze_composition(self, project: CreativeProject, analysis: Dict) -> List[Dict]:
        """Analyze composition and layout"""
        insights = []
        
        dimensions = analysis.get('dimensions', {})
        if not dimensions:
            return insights
        
        width, height = dimensions['width'], dimensions['height']
        aspect_ratio = width / height
        
        # Golden ratio analysis
        golden_ratio = 1.618
        if abs(aspect_ratio - golden_ratio) < 0.1:
            insights.append({
                'insight_type': 'composition_analysis',
                'title': 'Golden Ratio Composition',
                'description': 'Aspect ratio close to golden ratio (1.618) - visually pleasing',
                'score': 0.95,
                'data': {'aspect_ratio': aspect_ratio, 'golden_ratio': golden_ratio}
            })
        
        return insights

    def _generate_suggestions(self, insights: List[Dict], project: CreativeProject) -> List[str]:
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
        if project.project_type == ProjectType.SOCIAL_MEDIA:
            suggestions.append("Ensure text is large enough to read on mobile devices")
            suggestions.append("Consider platform-specific aspect ratios for better engagement")
        elif project.project_type == ProjectType.WEBSITE_MOCKUP:
            suggestions.append("Test design responsiveness across different screen sizes")
            suggestions.append("Verify accessibility standards compliance")
        
        return suggestions[:5]  # Limit to top 5 suggestions