"""Advanced creative analyzer for project analysis and insights."""

import random
from typing import Dict, List, Any, Optional
from datetime import datetime


class AdvancedCreativeAnalyzer:
    """Advanced analyzer for creative projects providing insights and recommendations."""
    
    def __init__(self):
        # Initialize with some sample analysis categories
        self.categories = [
            "composition", "color_harmony", "typography", "brand_consistency", 
            "creativity", "technical_execution", "target_audience_alignment",
            "market_appeal", "innovation", "usability"
        ]
    
    async def comprehensive_project_audit(self, project) -> Dict[str, Any]:
        """Perform a comprehensive audit of a creative project."""
        
        # Generate mock analysis results based on project data
        category_scores = {}
        for category in self.categories:
            # Generate scores between 0.3 and 0.95 for realism
            score = 0.3 + (random.random() * 0.65)
            category_scores[category] = score
        
        # Calculate overall score as weighted average
        overall_score = sum(category_scores.values()) / len(category_scores)
        
        # Generate detailed insights
        detailed_insights = self._generate_insights(project, category_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(project, category_scores)
        
        return {
            "overall_score": overall_score,
            "category_scores": category_scores,
            "detailed_insights": detailed_insights,
            "recommendations": recommendations,
            "analysis_date": datetime.utcnow().isoformat(),
            "analyzer_version": "1.0.0"
        }
    
    def _generate_insights(self, project, category_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate insights based on analysis."""
        insights = []
        
        # Generate insights for high-scoring categories
        high_scores = [(cat, score) for cat, score in category_scores.items() if score > 0.7]
        for category, score in high_scores[:3]:
            insights.append({
                "title": f"Strong {category.replace('_', ' ').title()}",
                "description": f"This project demonstrates excellent {category.replace('_', ' ')} with a score of {score:.1%}. This is a key strength that enhances the overall impact.",
                "score": score,
                "type": "strength",
                "category": category
            })
        
        # Generate insights for areas needing improvement
        low_scores = [(cat, score) for cat, score in category_scores.items() if score < 0.6]
        for category, score in low_scores[:3]:
            insights.append({
                "title": f"Improvement Opportunity in {category.replace('_', ' ').title()}",
                "description": f"The {category.replace('_', ' ')} could be enhanced to better align with best practices. Current score: {score:.1%}.",
                "score": score,
                "type": "improvement",
                "category": category
            })
        
        # Add project-specific insights based on type
        if hasattr(project, 'project_type'):
            type_specific_insight = self._get_type_specific_insight(project.project_type, category_scores)
            if type_specific_insight:
                insights.append(type_specific_insight)
        
        return insights
    
    def _generate_recommendations(self, project, category_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Find the lowest scoring categories for improvement recommendations
        sorted_scores = sorted(category_scores.items(), key=lambda x: x[1])
        
        for category, score in sorted_scores[:5]:
            if score < 0.7:  # Only recommend improvement for scores below 70%
                priority = "high" if score < 0.5 else "medium" if score < 0.6 else "low"
                
                rec = {
                    "title": f"Enhance {category.replace('_', ' ').title()}",
                    "description": self._get_improvement_suggestion(category, score),
                    "priority": priority,
                    "category": category,
                    "estimated_impact": self._calculate_impact(score),
                    "effort_level": self._estimate_effort(category)
                }
                recommendations.append(rec)
        
        # Add general recommendations
        recommendations.extend(self._get_general_recommendations(project, category_scores))
        
        return recommendations
    
    def _get_type_specific_insight(self, project_type: str, scores: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Get insights specific to project type."""
        type_insights = {
            "branding": {
                "title": "Brand Identity Cohesiveness",
                "description": "For branding projects, consistency across all brand elements is crucial for recognition and trust.",
                "focus_areas": ["brand_consistency", "color_harmony", "typography"]
            },
            "web_design": {
                "title": "User Experience Focus",
                "description": "Web design projects should prioritize usability and user journey optimization.",
                "focus_areas": ["usability", "target_audience_alignment", "technical_execution"]
            },
            "print_design": {
                "title": "Print Production Considerations",
                "description": "Print design requires attention to color profiles, resolution, and production constraints.",
                "focus_areas": ["technical_execution", "color_harmony", "composition"]
            }
        }
        
        if project_type in type_insights:
            insight_template = type_insights[project_type]
            relevant_scores = [scores.get(area, 0.5) for area in insight_template["focus_areas"]]
            avg_score = sum(relevant_scores) / len(relevant_scores)
            
            return {
                "title": insight_template["title"],
                "description": insight_template["description"],
                "score": avg_score,
                "type": "project_type_specific",
                "category": project_type
            }
        
        return None
    
    def _get_improvement_suggestion(self, category: str, score: float) -> str:
        """Get specific improvement suggestions for categories."""
        suggestions = {
            "composition": "Consider applying the rule of thirds, improving visual hierarchy, or adjusting element placement for better balance.",
            "color_harmony": "Review color relationships using color theory principles, check contrast ratios, and ensure accessibility compliance.",
            "typography": "Evaluate font choices for readability, hierarchy, and brand alignment. Consider spacing and sizing improvements.",
            "brand_consistency": "Ensure all brand elements align with brand guidelines and maintain consistency across touchpoints.",
            "creativity": "Explore more innovative approaches, unique concepts, or unconventional solutions to stand out.",
            "technical_execution": "Improve file quality, resolution, or technical implementation for professional standards.",
            "target_audience_alignment": "Research target audience preferences and adjust design elements to better resonate with them.",
            "market_appeal": "Analyze current market trends and competitor approaches to enhance commercial viability.",
            "innovation": "Incorporate cutting-edge design trends or novel approaches to differentiate from competitors.",
            "usability": "Conduct user testing and improve interface elements for better user experience."
        }
        
        return suggestions.get(category, f"Focus on improving {category.replace('_', ' ')} through research and iterative refinement.")
    
    def _calculate_impact(self, score: float) -> str:
        """Calculate potential impact of improvement."""
        if score < 0.4:
            return "high"
        elif score < 0.6:
            return "medium"
        else:
            return "low"
    
    def _estimate_effort(self, category: str) -> str:
        """Estimate effort required for improvement."""
        high_effort = ["technical_execution", "creativity", "innovation"]
        medium_effort = ["composition", "color_harmony", "typography", "brand_consistency"]
        
        if category in high_effort:
            return "high"
        elif category in medium_effort:
            return "medium"
        else:
            return "low"
    
    def _get_general_recommendations(self, project, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get general recommendations applicable to most projects."""
        general_recs = []
        
        overall_avg = sum(scores.values()) / len(scores)
        
        if overall_avg < 0.6:
            general_recs.append({
                "title": "Comprehensive Design Review",
                "description": "Consider a thorough design review session with stakeholders to identify core improvement areas.",
                "priority": "high",
                "category": "process",
                "estimated_impact": "high",
                "effort_level": "medium"
            })
        
        if overall_avg > 0.8:
            general_recs.append({
                "title": "Document Best Practices",
                "description": "This project demonstrates strong execution. Document the successful approaches for future reference.",
                "priority": "low",
                "category": "process",
                "estimated_impact": "medium",
                "effort_level": "low"
            })
        
        return general_recs