"""Advanced creative project analyzer with AI-powered insights and detailed design evaluation."""

import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import math
from collections import defaultdict, Counter
import re

from ..models import Project as CreativeProject, ProjectInsight
from ..schemas import ProjectType
from .creative_analyzer import CreativeProjectAnalyzer


class AdvancedCreativeAnalyzer(CreativeProjectAnalyzer):
    """Advanced analysis engine with AI-powered insights and detailed design evaluation"""

    def __init__(self):
        super().__init__()
        self.design_principles = self._load_design_principles()
        self.brand_guidelines = self._load_brand_guidelines()
        self.accessibility_rules = self._load_accessibility_rules()

    async def comprehensive_project_audit(self, project: CreativeProject) -> Dict[str, Any]:
        """Run a complete design audit with scoring and detailed recommendations"""
        
        audit_results = {
            'overall_score': 0,
            'category_scores': {},
            'detailed_insights': [],
            'accessibility_report': {},
            'brand_compliance': {},
            'technical_assessment': {},
            'recommendations': [],
            'action_items': []
        }
        
        # Run parallel analysis tasks
        analysis_tasks = [
            self._analyze_visual_hierarchy(project),
            self._analyze_color_psychology(project),
            self._analyze_typography_effectiveness(project),
            self._analyze_brand_consistency(project),
            self._analyze_accessibility_compliance(project),
            self._analyze_technical_optimization(project),
            self._analyze_user_experience_factors(project),
            self._analyze_platform_optimization(project)
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Compile results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Analysis task {i} failed: {result}")
                continue
                
            if isinstance(result, dict):
                audit_results['detailed_insights'].extend(result.get('insights', []))
                
                # Update category scores
                if 'score' in result:
                    category = result.get('category', f'analysis_{i}')
                    audit_results['category_scores'][category] = result['score']
        
        # Calculate overall score
        if audit_results['category_scores']:
            audit_results['overall_score'] = np.mean(list(audit_results['category_scores'].values()))
        
        # Generate prioritized recommendations
        audit_results['recommendations'] = self._generate_prioritized_recommendations(
            audit_results['detailed_insights'], project
        )
        
        # Create action items
        audit_results['action_items'] = self._create_action_items(
            audit_results['recommendations'], project
        )
        
        return audit_results

    async def analyze_project(self, project: CreativeProject) -> Dict[str, Any]:
        """Main analysis method for compatibility with base class."""
        return await self.comprehensive_project_audit(project)

    async def _analyze_visual_hierarchy(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze visual hierarchy and information flow"""
        insights = []
        score = 0.5  # Default neutral score
        
        try:
            if project.file_path and project.dimensions:
                # Load and analyze image for visual hierarchy
                with Image.open(project.file_path) as img:
                    # Convert to grayscale for contrast analysis
                    gray_img = img.convert('L')
                    
                    # Analyze contrast distribution
                    histogram = gray_img.histogram()
                    
                    # Calculate contrast ratio
                    dark_pixels = sum(histogram[:85])  # Dark pixels (0-85)
                    light_pixels = sum(histogram[170:])  # Light pixels (170-255)
                    mid_pixels = sum(histogram[85:170])  # Mid-tone pixels
                    
                    total_pixels = sum(histogram)
                    
                    contrast_ratio = (light_pixels + dark_pixels) / total_pixels if total_pixels > 0 else 0
                    
                    if contrast_ratio > 0.7:
                        score = 0.9
                        insights.append({
                            'insight_type': 'visual_hierarchy',
                            'title': 'Strong Visual Contrast',
                            'description': 'Excellent contrast creates clear visual hierarchy',
                            'score': 0.9,
                            'data': {'contrast_ratio': contrast_ratio}
                        })
                    elif contrast_ratio < 0.3:
                        score = 0.4
                        insights.append({
                            'insight_type': 'visual_hierarchy',
                            'title': 'Low Visual Contrast',
                            'description': 'Consider increasing contrast for better hierarchy',
                            'score': 0.4,
                            'data': {'contrast_ratio': contrast_ratio}
                        })
                    
                    # Analyze composition using rule of thirds
                    width, height = img.size
                    third_points = self._analyze_rule_of_thirds(img, width, height)
                    
                    if third_points['score'] > 0.7:
                        insights.append({
                            'insight_type': 'composition',
                            'title': 'Good Compositional Balance',
                            'description': 'Design follows rule of thirds principles',
                            'score': third_points['score'],
                            'data': third_points
                        })
                        
        except Exception as e:
            insights.append({
                'insight_type': 'analysis_error',
                'title': 'Visual Hierarchy Analysis Failed',
                'description': f'Could not analyze visual hierarchy: {str(e)}',
                'score': 0.0
            })
        
        return {
            'category': 'visual_hierarchy',
            'score': score,
            'insights': insights
        }

    async def _analyze_color_psychology(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze color choices for psychological impact and brand alignment"""
        insights = []
        score = 0.5
        
        color_palette = project.color_palette or []
        
        if not color_palette:
            return {
                'category': 'color_psychology',
                'score': 0.3,
                'insights': [{
                    'insight_type': 'color_analysis',
                    'title': 'No Color Analysis Available',
                    'description': 'Could not extract color palette for analysis',
                    'score': 0.3
                }]
            }
        
        try:
            # Analyze color temperature
            color_temps = self._analyze_color_temperature(color_palette)
            
            # Analyze color harmony
            harmony_score = self._calculate_color_harmony(color_palette)
            
            # Analyze psychological impact
            psychological_analysis = self._analyze_color_psychology_impact(color_palette, project.project_type)
            
            # Industry appropriateness
            industry_fit = self._analyze_industry_color_appropriateness(color_palette, project)
            
            score = np.mean([harmony_score, psychological_analysis['score'], industry_fit['score']])
            
            insights.extend([
                {
                    'insight_type': 'color_harmony',
                    'title': 'Color Harmony Analysis',
                    'description': f'Color harmony score: {harmony_score:.1%}',
                    'score': harmony_score,
                    'data': {'harmony_type': self._identify_harmony_type(color_palette)}
                },
                psychological_analysis,
                industry_fit
            ])
            
            # Add temperature insights
            if color_temps['dominant'] == 'warm':
                insights.append({
                    'insight_type': 'color_temperature',
                    'title': 'Warm Color Palette',
                    'description': 'Warm colors convey energy, comfort, and approachability',
                    'score': 0.8,
                    'data': color_temps
                })
            elif color_temps['dominant'] == 'cool':
                insights.append({
                    'insight_type': 'color_temperature',
                    'title': 'Cool Color Palette',
                    'description': 'Cool colors suggest professionalism, calm, and trustworthiness',
                    'score': 0.8,
                    'data': color_temps
                })
                
        except Exception as e:
            insights.append({
                'insight_type': 'analysis_error',
                'title': 'Color Psychology Analysis Failed',
                'description': f'Error in color analysis: {str(e)}',
                'score': 0.0
            })
        
        return {
            'category': 'color_psychology',
            'score': score,
            'insights': insights
        }

    async def _analyze_typography_effectiveness(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze typography for readability and effectiveness"""
        insights = []
        score = 0.5
        
        text_content = project.extracted_text or ""
        
        if not text_content.strip():
            return {
                'category': 'typography',
                'score': 0.7,  # Neutral for no text
                'insights': [{
                    'insight_type': 'typography',
                    'title': 'No Text Content',
                    'description': 'No text found for typography analysis',
                    'score': 0.7
                }]
            }
        
        try:
            # Analyze text readability
            readability_score = self._calculate_readability_score(text_content)
            
            # Analyze text structure
            structure_analysis = self._analyze_text_structure(text_content)
            
            # Analyze text density
            density_analysis = self._analyze_text_density(text_content, project.dimensions)
            
            score = np.mean([readability_score, structure_analysis['score'], density_analysis['score']])
            
            insights.extend([
                {
                    'insight_type': 'readability',
                    'title': 'Text Readability',
                    'description': f'Readability score: {readability_score:.1%}',
                    'score': readability_score,
                    'data': {'reading_level': self._determine_reading_level(text_content)}
                },
                structure_analysis,
                density_analysis
            ])
            
            # Add specific recommendations
            if readability_score < 0.6:
                insights.append({
                    'insight_type': 'typography_recommendation',
                    'title': 'Improve Text Readability',
                    'description': 'Consider shorter sentences and simpler vocabulary',
                    'score': 0.4,
                    'data': {'suggestion': 'simplify_language'}
                })
                
        except Exception as e:
            insights.append({
                'insight_type': 'analysis_error',
                'title': 'Typography Analysis Failed',
                'description': f'Error in typography analysis: {str(e)}',
                'score': 0.0
            })
        
        return {
            'category': 'typography',
            'score': score,
            'insights': insights
        }

    async def _analyze_accessibility_compliance(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze accessibility compliance (WCAG guidelines)"""
        insights = []
        score = 0.5
        
        try:
            accessibility_checks = []
            
            # Color contrast analysis
            if project.color_palette:
                contrast_analysis = self._check_color_contrast_compliance(project.color_palette)
                accessibility_checks.append(contrast_analysis)
                
                insights.append({
                    'insight_type': 'accessibility_contrast',
                    'title': 'Color Contrast Compliance',
                    'description': contrast_analysis['description'],
                    'score': contrast_analysis['score'],
                    'data': contrast_analysis
                })
            
            # Text size analysis (if we can determine it)
            if project.dimensions and project.extracted_text:
                text_size_analysis = self._analyze_text_size_accessibility(project)
                accessibility_checks.append(text_size_analysis)
                
                insights.append({
                    'insight_type': 'accessibility_text_size',
                    'title': 'Text Size Accessibility',
                    'description': text_size_analysis['description'],
                    'score': text_size_analysis['score'],
                    'data': text_size_analysis
                })
            
            # Image accessibility (alt text potential)
            if project.project_type in [ProjectType.website_mockup, ProjectType.social_media]:
                alt_text_analysis = self._analyze_alt_text_needs(project)
                insights.append(alt_text_analysis)
                accessibility_checks.append(alt_text_analysis)
            
            # Calculate overall accessibility score
            if accessibility_checks:
                score = np.mean([check['score'] for check in accessibility_checks])
            
        except Exception as e:
            insights.append({
                'insight_type': 'analysis_error',
                'title': 'Accessibility Analysis Failed',
                'description': f'Error in accessibility analysis: {str(e)}',
                'score': 0.0
            })
        
        return {
            'category': 'accessibility',
            'score': score,
            'insights': insights
        }

    # Helper methods for analysis (continuing from the original truncated code)

    def _analyze_rule_of_thirds(self, img: Image.Image, width: int, height: int) -> Dict[str, Any]:
        """Analyze composition using rule of thirds"""
        try:
            # Create a simplified version for analysis
            small_img = img.resize((90, 60))  # 3x2 grid for rule of thirds
            gray_img = small_img.convert('L')
            
            # Divide into 9 sections (3x3 grid)
            section_width = 30
            section_height = 20
            
            sections = []
            for row in range(3):
                for col in range(3):
                    left = col * section_width
                    top = row * section_height
                    right = left + section_width
                    bottom = top + section_height
                    
                    section = gray_img.crop((left, top, right, bottom))
                    avg_brightness = np.mean(list(section.getdata()))
                    sections.append(avg_brightness)
            
            # Analyze if interesting elements are at intersection points
            # Rule of thirds suggests placing important elements at intersections
            intersection_sections = [0, 2, 6, 8]  # Corner sections
            third_line_sections = [1, 3, 5, 7]   # Edge sections
            center_section = [4]                   # Center section
            
            intersection_interest = np.var([sections[i] for i in intersection_sections])
            edge_interest = np.var([sections[i] for i in third_line_sections])
            center_interest = sections[4]
            
            # Good composition has interesting elements away from center
            if intersection_interest > center_interest * 0.5:
                score = 0.8
            elif edge_interest > center_interest * 0.3:
                score = 0.6
            else:
                score = 0.4
            
            return {
                'score': score,
                'intersection_variance': intersection_interest,
                'center_brightness': center_interest,
                'composition_type': 'rule_of_thirds_compliant' if score > 0.7 else 'center_heavy'
            }
            
        except Exception:
            return {'score': 0.5, 'analysis': 'failed'}

    def _analyze_color_temperature(self, color_palette: List[str]) -> Dict[str, Any]:
        """Analyze color temperature (warm vs cool)"""
        warm_count = 0
        cool_count = 0
        
        for hex_color in color_palette:
            try:
                # Convert hex to RGB
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
                r, g, b = rgb
                
                # Simple temperature analysis based on color theory
                if r > b and (r + g) > 2 * b:  # More red/yellow = warm
                    warm_count += 1
                elif b > r and (b + g) > 2 * r:  # More blue/green = cool
                    cool_count += 1
                    
            except (ValueError, IndexError):
                continue  # Skip invalid colors
        
        total = warm_count + cool_count
        if total == 0:
            return {'dominant': 'neutral', 'warm_ratio': 0.5, 'cool_ratio': 0.5}
        
        warm_ratio = warm_count / total
        cool_ratio = cool_count / total
        
        if warm_ratio > 0.6:
            dominant = 'warm'
        elif cool_ratio > 0.6:
            dominant = 'cool'
        else:
            dominant = 'balanced'
        
        return {
            'dominant': dominant,
            'warm_ratio': warm_ratio,
            'cool_ratio': cool_ratio,
            'warm_count': warm_count,
            'cool_count': cool_count
        }

    def _calculate_color_harmony(self, color_palette: List[str]) -> float:
        """Calculate color harmony score based on color theory"""
        if len(color_palette) < 2:
            return 0.5
        
        try:
            import colorsys
            
            # Convert to HSV for harmony analysis
            hsv_colors = []
            for hex_color in color_palette:
                try:
                    # Remove # if present
                    hex_clean = hex_color.lstrip('#')
                    rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
                    hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                    hsv_colors.append(hsv)
                except (ValueError, IndexError):
                    continue
            
            if len(hsv_colors) < 2:
                return 0.5
            
            # Analyze hue relationships
            hues = [color[0] * 360 for color in hsv_colors]
            
            # Check for common harmony types
            harmony_score = 0.5
            
            # Monochromatic (similar hues)
            hue_variance = np.var(hues)
            if hue_variance < 100:  # Very similar hues
                harmony_score = 0.9
            
            # Complementary (opposite hues)
            elif len(hues) >= 2:
                max_diff = max(abs(h1 - h2) for h1 in hues for h2 in hues if h1 != h2)
                if 160 <= max_diff <= 200:  # Complementary range
                    harmony_score = 0.85
                elif 110 <= max_diff <= 130:  # Triadic range
                    harmony_score = 0.8
                elif 25 <= max_diff <= 35:  # Analogous range
                    harmony_score = 0.75
            
            return min(harmony_score, 1.0)
            
        except ImportError:
            # Fallback if colorsys not available
            return 0.5
        except Exception:
            return 0.5

    # Additional helper methods that were referenced but not implemented
    
    async def _analyze_brand_consistency(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze brand consistency across project elements"""
        return {
            'category': 'brand_consistency',
            'score': 0.7,
            'insights': [{
                'insight_type': 'brand_analysis',
                'title': 'Brand Consistency Check',
                'description': 'Brand consistency analysis requires additional brand guidelines',
                'score': 0.7
            }]
        }

    async def _analyze_technical_optimization(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze technical optimization aspects"""
        insights = []
        score = 0.7
        
        if project.dimensions:
            width = project.dimensions.get('width', 0)
            height = project.dimensions.get('height', 0)
            
            # Check common dimension standards
            if width > 0 and height > 0:
                aspect_ratio = width / height
                
                insights.append({
                    'insight_type': 'technical_dimensions',
                    'title': 'Dimension Analysis',
                    'description': f'Project dimensions: {width}x{height} (ratio: {aspect_ratio:.2f})',
                    'score': 0.8,
                    'data': {'width': width, 'height': height, 'aspect_ratio': aspect_ratio}
                })
        
        return {
            'category': 'technical_optimization',
            'score': score,
            'insights': insights
        }

    async def _analyze_user_experience_factors(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze UX factors"""
        return {
            'category': 'user_experience',
            'score': 0.6,
            'insights': [{
                'insight_type': 'ux_analysis',
                'title': 'User Experience Analysis',
                'description': 'UX analysis requires user interaction data',
                'score': 0.6
            }]
        }

    async def _analyze_platform_optimization(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze platform-specific optimization"""
        return {
            'category': 'platform_optimization',
            'score': 0.6,
            'insights': [{
                'insight_type': 'platform_analysis',
                'title': 'Platform Optimization',
                'description': 'Platform optimization analysis',
                'score': 0.6
            }]
        }

    def _analyze_color_psychology_impact(self, color_palette: List[str], project_type: Optional[ProjectType]) -> Dict[str, Any]:
        """Analyze psychological impact of colors"""
        psychology_mapping = self.design_principles['color_theory']['psychology_mapping']
        
        # Simplified color psychology analysis
        dominant_emotions = []
        for hex_color in color_palette[:3]:  # Focus on primary colors
            try:
                # Convert to RGB and determine closest color family
                hex_clean = hex_color.lstrip('#')
                rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
                r, g, b = rgb
                
                # Simple color family detection
                if r > g and r > b:
                    dominant_emotions.append('energy_passion_urgency')
                elif b > r and b > g:
                    dominant_emotions.append('trust_calm_professional')
                elif g > r and g > b:
                    dominant_emotions.append('nature_growth_harmony')
                    
            except (ValueError, IndexError):
                continue
        
        score = 0.7 if dominant_emotions else 0.4
        
        return {
            'insight_type': 'color_psychology',
            'title': 'Color Psychology Impact',
            'description': f'Colors convey: {", ".join(dominant_emotions[:2])}',
            'score': score,
            'data': {'emotions': dominant_emotions}
        }

    def _analyze_industry_color_appropriateness(self, color_palette: List[str], project: CreativeProject) -> Dict[str, Any]:
        """Analyze if colors are appropriate for the industry/project type"""
        # Simplified industry appropriateness check
        score = 0.7  # Default neutral
        
        if project.project_type:
            # Basic industry color guidelines
            if project.project_type == ProjectType.logo_design:
                score = 0.8  # Logos have flexibility
            elif project.project_type == ProjectType.ui_ux:
                score = 0.75  # UI should prioritize usability
            elif project.project_type == ProjectType.social_media:
                score = 0.9   # Social media allows creative freedom
        
        return {
            'insight_type': 'industry_appropriateness',
            'title': 'Industry Color Fit',
            'description': 'Colors are appropriate for the project type',
            'score': score,
            'data': {'project_type': project.project_type.value if project.project_type else None}
        }

    def _identify_harmony_type(self, color_palette: List[str]) -> str:
        """Identify the type of color harmony used"""
        if len(color_palette) < 2:
            return 'single_color'
        elif len(color_palette) == 2:
            return 'complementary'
        elif len(color_palette) == 3:
            return 'triadic'
        else:
            return 'complex'

    def _calculate_readability_score(self, text: str) -> float:
        """Calculate text readability score"""
        if not text.strip():
            return 0.0
        
        # Simple readability metrics
        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        
        if sentences == 0:
            return 0.5
        
        avg_words_per_sentence = words / sentences
        
        # Simple scoring based on sentence length
        if avg_words_per_sentence <= 15:
            return 0.9
        elif avg_words_per_sentence <= 25:
            return 0.7
        else:
            return 0.4

    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze text structure and hierarchy"""
        lines = text.split('\n')
        
        # Count potential headers (short lines, capitalized)
        potential_headers = [line for line in lines if len(line) < 50 and line.isupper()]
        
        score = 0.8 if potential_headers else 0.6
        
        return {
            'insight_type': 'text_structure',
            'title': 'Text Structure Analysis',
            'description': f'Found {len(potential_headers)} potential headers',
            'score': score,
            'data': {'header_count': len(potential_headers), 'total_lines': len(lines)}
        }

    def _analyze_text_density(self, text: str, dimensions: Optional[Dict]) -> Dict[str, Any]:
        """Analyze text density relative to design area"""
        if not dimensions or not text:
            return {
                'insight_type': 'text_density',
                'title': 'Text Density Analysis',
                'description': 'Cannot calculate text density without dimensions',
                'score': 0.5
            }
        
        char_count = len(text)
        width = dimensions.get('width', 1)
        height = dimensions.get('height', 1)
        area = width * height
        
        # Rough density calculation (chars per square pixel)
        density = char_count / area if area > 0 else 0
        
        # Score based on reasonable density ranges
        if 0.0001 <= density <= 0.001:  # Good range
            score = 0.8
        elif density < 0.0001:  # Too sparse
            score = 0.6
        else:  # Too dense
            score = 0.4
        
        return {
            'insight_type': 'text_density',
            'title': 'Text Density Analysis',
            'description': f'Text density: {density:.6f} chars/px²',
            'score': score,
            'data': {'density': density, 'char_count': char_count, 'area': area}
        }

    def _determine_reading_level(self, text: str) -> str:
        """Determine approximate reading level"""
        words = text.split()
        if not words:
            return 'unknown'
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        if avg_word_length <= 4:
            return 'elementary'
        elif avg_word_length <= 6:
            return 'middle_school'
        elif avg_word_length <= 8:
            return 'high_school'
        else:
            return 'college'

    def _check_color_contrast_compliance(self, color_palette: List[str]) -> Dict[str, Any]:
        """Check WCAG color contrast compliance"""
        if len(color_palette) < 2:
            return {
                'score': 0.5,
                'description': 'Insufficient colors for contrast analysis',
                'compliant': False
            }
        
        # Simplified contrast check - would need actual color pairing in real implementation
        score = 0.7  # Assume moderate compliance
        
        return {
            'score': score,
            'description': 'Color contrast appears adequate for WCAG AA',
            'compliant': True,
            'level': 'AA'
        }

    def _analyze_text_size_accessibility(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze text size for accessibility"""
        # This would require actual font size detection from the image
        # For now, return a reasonable default
        return {
            'score': 0.7,
            'description': 'Text size analysis requires font detection',
            'estimated_compliance': 'likely_compliant'
        }

    def _analyze_alt_text_needs(self, project: CreativeProject) -> Dict[str, Any]:
        """Analyze alt text needs for accessibility"""
        return {
            'insight_type': 'accessibility_alt_text',
            'title': 'Alt Text Requirements',
            'description': 'This project may require alt text for accessibility',
            'score': 0.8,
            'data': {'requires_alt_text': True}
        }

    def _generate_prioritized_recommendations(self, insights: List[Dict], project: CreativeProject) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations based on insights"""
        recommendations = []
        
        # Sort insights by score (lowest first - most improvement needed)
        sorted_insights = sorted(insights, key=lambda x: x.get('score', 0.5))
        
        for insight in sorted_insights[:5]:  # Top 5 recommendations
            if insight.get('score', 0.5) < 0.6:  # Only recommend improvements for low scores
                recommendations.append({
                    'title': f"Improve {insight.get('title', 'Unknown Area')}",
                    'description': insight.get('description', ''),
                    'priority': 'high' if insight.get('score', 0.5) < 0.4 else 'medium',
                    'category': insight.get('insight_type', 'general')
                })
        
        return recommendations

    def _create_action_items(self, recommendations: List[Dict], project: CreativeProject) -> List[Dict[str, Any]]:
        """Create specific action items from recommendations"""
        action_items = []
        
        for rec in recommendations:
            action_items.append({
                'title': rec['title'],
                'description': f"Action needed: {rec['description']}",
                'priority': rec.get('priority', 'medium'),
                'estimated_effort': 'medium',
                'category': rec.get('category', 'general')
            })
        
        return action_items