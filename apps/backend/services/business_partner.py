"""
Business Partner Service - Core integration of all business intelligence capabilities
"""

from typing import Dict, List, Any, Optional
from .casey_ai import (
    AdvancedCaseyAI, 
    BusinessOpportunity, 
    PortfolioInsight, 
    ConversationContext
)


class BusinessPartnerService:
    """
    Main service orchestrating all business partner capabilities
    """
    
    def __init__(self):
        self.casey_ai = AdvancedCaseyAI()
        self.active_opportunities = []
        self.tracked_metrics = {}
        
    def analyze_business_conversation(self, user_input: str, conversation_id: str = "default") -> Dict[str, Any]:
        """
        Comprehensive business analysis of user conversation
        """
        result = self.casey_ai.analyze_conversation_turn(user_input, conversation_id)
        
        # Enhance with business-specific insights
        business_analysis = self._enhance_business_analysis(result, conversation_id)
        
        return {
            **result,
            "business_analysis": business_analysis,
            "action_items": self._generate_action_items(result),
            "next_steps": self._suggest_next_steps(result)
        }
    
    def get_opportunities(self, conversation_id: str = "default") -> List[BusinessOpportunity]:
        """Get current business opportunities for user"""
        context = self.casey_ai.user_profiles[conversation_id]
        
        # Get opportunities from lead generation engine
        skills = self._extract_skills_from_context(context)
        opportunities = self.casey_ai.lead_generator.find_opportunities(skills, context.preferences)
        
        return opportunities
    
    def analyze_portfolio(self, portfolio_data: Dict, conversation_id: str = "default") -> Dict[str, Any]:
        """Analyze portfolio for optimization opportunities"""
        context = self.casey_ai.user_profiles[conversation_id]
        
        # Get portfolio insights
        insights = self.casey_ai.portfolio_analyzer.analyze_project_performance(
            portfolio_data.get("projects", [])
        )
        
        # Get presentation improvements
        presentation_improvements = self.casey_ai.portfolio_analyzer.optimize_presentation(portfolio_data)
        
        return {
            "insights": insights,
            "presentation_improvements": presentation_improvements,
            "positioning_recommendations": self._get_positioning_recommendations(context),
            "conversion_optimization": self._get_conversion_optimization(portfolio_data)
        }
    
    def get_rate_recommendations(self, current_info: Dict, conversation_id: str = "default") -> Dict[str, Any]:
        """Get rate optimization recommendations"""
        context = self.casey_ai.user_profiles[conversation_id]
        
        # Get market analysis
        skills = self._extract_skills_from_context(context)
        market_analysis = self.casey_ai.rate_optimizer.analyze_market_rates(
            skills=skills,
            location=current_info.get("location", "US"),
            experience=context.user_expertise
        )
        
        # Get pricing models
        pricing_models = self.casey_ai.rate_optimizer.suggest_pricing_models(
            context.business_context.get("type", "freelancer")
        )
        
        return {
            "market_analysis": market_analysis,
            "pricing_models": pricing_models,
            "implementation_plan": self._create_rate_increase_plan(current_info, market_analysis),
            "justification_points": self._create_rate_justification(context)
        }
    
    def get_brand_strategy(self, current_brand: Dict, conversation_id: str = "default") -> Dict[str, Any]:
        """Get brand building and positioning strategy"""
        context = self.casey_ai.user_profiles[conversation_id]
        
        # Analyze current positioning
        positioning_analysis = self.casey_ai.brand_builder.analyze_positioning(current_brand)
        
        # Get content strategy
        content_strategy = self.casey_ai.brand_builder.generate_content_strategy(
            niche=context.portfolio_type,
            expertise=context.user_expertise
        )
        
        # Get specialization suggestions
        skills = self._extract_skills_from_context(context)
        specializations = self.casey_ai.brand_builder.suggest_specialization(
            skills=skills,
            interests=current_brand.get("interests", [])
        )
        
        return {
            "positioning_analysis": positioning_analysis,
            "content_strategy": content_strategy,
            "specialization_options": specializations,
            "implementation_roadmap": self._create_brand_roadmap(positioning_analysis, content_strategy)
        }
    
    def get_business_intelligence(self, conversation_id: str = "default") -> Dict[str, Any]:
        """Get comprehensive business intelligence dashboard"""
        context = self.casey_ai.user_profiles[conversation_id]
        
        # Get performance insights
        performance_insights = self.casey_ai.business_intelligence.generate_insights()
        
        return {
            "performance_insights": performance_insights,
            "growth_trajectory": self._calculate_growth_trajectory(context),
            "risk_assessment": self._assess_business_risks(context),
            "optimization_opportunities": self._identify_optimization_opportunities(context)
        }
    
    def _enhance_business_analysis(self, result: Dict, conversation_id: str) -> Dict[str, Any]:
        """Enhance analysis with business context"""
        context = self.casey_ai.user_profiles[conversation_id]
        
        return {
            "business_readiness": self._assess_business_readiness(context),
            "revenue_potential": self._estimate_revenue_potential(context),
            "competitive_positioning": self._analyze_competitive_position(context),
            "market_opportunities": self._identify_market_opportunities(context)
        }
    
    def _generate_action_items(self, result: Dict) -> List[str]:
        """Generate specific action items based on analysis"""
        action_items = []
        
        insights = result.get("insights", [])
        for insight in insights:
            if insight.actionable_steps:
                action_items.extend(insight.actionable_steps[:2])  # Top 2 per insight
        
        # Add business-specific actions
        if result.get("business_opportunities"):
            action_items.append("Review identified business opportunities")
        
        if result.get("rate_recommendations"):
            action_items.append("Implement rate optimization strategy")
            
        return action_items[:5]  # Limit to top 5 actions
    
    def _suggest_next_steps(self, result: Dict) -> List[str]:
        """Suggest immediate next steps"""
        next_steps = []
        
        # Based on conversation analysis, suggest logical next steps
        context = result.get("context")
        if context and hasattr(context, 'business_stage'):
            if context.business_stage == "starting":
                next_steps = [
                    "Complete portfolio optimization analysis",
                    "Set competitive rates based on market research",
                    "Create lead generation strategy"
                ]
            elif context.business_stage == "growing":
                next_steps = [
                    "Implement retainer client strategy",
                    "Develop specialization positioning",
                    "Create business intelligence dashboard"
                ]
            else:
                next_steps = [
                    "Explore premium market opportunities",
                    "Develop thought leadership content",
                    "Consider agency/scaling model"
                ]
        
        return next_steps
    
    def _extract_skills_from_context(self, context: ConversationContext) -> List[str]:
        """Extract skills from conversation context"""
        skills = []
        
        if context.portfolio_type != "unknown":
            skills.append(context.portfolio_type)
        
        if context.domain != "general":
            skills.append(context.domain)
            
        # Add default creative skills
        skills.extend(["design", "creative", "visual"])
        
        return skills
    
    def _get_positioning_recommendations(self, context: ConversationContext) -> List[str]:
        """Get positioning recommendations"""
        recommendations = []
        
        if context.portfolio_type != "unknown":
            recommendations.append(f"Position as specialized {context.portfolio_type.replace('_', ' ')}")
        
        if context.user_expertise == "expert":
            recommendations.append("Emphasize senior-level expertise and thought leadership")
        
        recommendations.extend([
            "Focus on business outcomes rather than design process",
            "Highlight measurable results and client success stories",
            "Create authority content in your specialization"
        ])
        
        return recommendations
    
    def _get_conversion_optimization(self, portfolio_data: Dict) -> List[str]:
        """Get portfolio conversion optimization tips"""
        return [
            "Add clear call-to-action on every project page",
            "Include client testimonials with specific results",
            "Show before/after comparisons where possible",
            "Create dedicated 'About' page with clear positioning",
            "Add contact form with project brief questions"
        ]
    
    def _create_rate_increase_plan(self, current_info: Dict, market_analysis: Dict) -> List[Dict[str, Any]]:
        """Create step-by-step rate increase plan"""
        return [
            {
                "phase": "Immediate (Next 30 days)",
                "action": "Increase rates by 15% for all new clients",
                "rationale": "Market research justification",
                "expected_result": "Higher quality leads, reduced price objections"
            },
            {
                "phase": "Short-term (3 months)",
                "action": "Implement value-based project packages",
                "rationale": "Focus on outcomes rather than time",
                "expected_result": "25-40% revenue increase per project"
            },
            {
                "phase": "Medium-term (6 months)",
                "action": "Transition top clients to retainer model",
                "rationale": "Predictable income and stronger relationships",
                "expected_result": "Stable monthly revenue base"
            }
        ]
    
    def _create_rate_justification(self, context: ConversationContext) -> List[str]:
        """Create rate increase justification points"""
        justifications = [
            "Market research shows rates below industry average",
            "Specialized expertise commands premium pricing",
            "Track record of delivering measurable business results"
        ]
        
        if context.user_expertise == "expert":
            justifications.append("Senior-level experience with complex projects")
        
        if context.portfolio_type != "unknown":
            justifications.append(f"Specialization in {context.portfolio_type.replace('_', ' ')} niche")
            
        return justifications
    
    def _create_brand_roadmap(self, positioning_analysis: Dict, content_strategy: Dict) -> List[Dict[str, Any]]:
        """Create brand building roadmap"""
        return [
            {
                "milestone": "Month 1: Foundation",
                "tasks": [
                    "Define clear specialization and positioning",
                    "Update portfolio with case studies",
                    "Create professional headshots and bio"
                ]
            },
            {
                "milestone": "Month 2-3: Content Creation",
                "tasks": [
                    "Launch content strategy on LinkedIn",
                    "Publish 4-6 portfolio case studies",
                    "Start engaging in industry communities"
                ]
            },
            {
                "milestone": "Month 4-6: Authority Building", 
                "tasks": [
                    "Guest post on industry publications",
                    "Speak at industry events/podcasts",
                    "Build email list and newsletter"
                ]
            }
        ]
    
    def _assess_business_readiness(self, context: ConversationContext) -> Dict[str, Any]:
        """Assess readiness for business optimization"""
        readiness_score = 0.5  # Base score
        
        if context.user_expertise in ["intermediate", "expert"]:
            readiness_score += 0.2
        
        if context.portfolio_type != "unknown":
            readiness_score += 0.2
            
        if context.business_context.get("type") == "freelancer":
            readiness_score += 0.1
            
        return {
            "score": min(readiness_score, 1.0),
            "level": "High" if readiness_score > 0.7 else "Medium" if readiness_score > 0.4 else "Low",
            "next_steps": "Focus on portfolio optimization and rate increases" if readiness_score > 0.6 else "Build expertise and define specialization"
        }
    
    def _estimate_revenue_potential(self, context: ConversationContext) -> Dict[str, Any]:
        """Estimate revenue potential based on context"""
        base_monthly = 3000  # Conservative base
        
        if context.user_expertise == "expert":
            base_monthly *= 2.5
        elif context.user_expertise == "intermediate":
            base_monthly *= 1.5
            
        if context.portfolio_type in ["ui_designer", "ux_designer"]:
            base_monthly *= 1.3  # Tech premium
            
        return {
            "current_estimate": f"${int(base_monthly * 0.7)}-{base_monthly}",
            "optimized_potential": f"${base_monthly}-{int(base_monthly * 1.8)}",
            "timeline": "6-12 months with optimization",
            "key_factors": ["Rate increases", "Specialization", "Premium positioning"]
        }
    
    def _analyze_competitive_position(self, context: ConversationContext) -> Dict[str, str]:
        """Analyze competitive positioning"""
        return {
            "current_position": "Generalist in competitive market" if context.portfolio_type == "unknown" else f"Emerging {context.portfolio_type.replace('_', ' ')} specialist",
            "opportunity": "Differentiate through specialization and premium positioning",
            "competitive_advantage": "Deep expertise + business impact focus",
            "market_gap": "High-quality specialists who understand business strategy"
        }
    
    def _identify_market_opportunities(self, context: ConversationContext) -> List[str]:
        """Identify current market opportunities"""
        opportunities = [
            "Remote work creating global client access",
            "Digital transformation increasing design demand",
            "Small businesses need professional design help"
        ]
        
        if context.portfolio_type in ["ui_designer", "ux_designer"]:
            opportunities.append("SaaS boom creating high-demand for product designers")
        
        return opportunities
    
    def _calculate_growth_trajectory(self, context: ConversationContext) -> Dict[str, Any]:
        """Calculate potential growth trajectory"""
        return {
            "current_stage": context.business_stage,
            "next_stage": "Growing" if context.business_stage == "starting" else "Scaling",
            "timeline_to_next": "6-12 months",
            "growth_multiplier": "2-3x revenue potential",
            "key_milestones": [
                "Rate optimization (Month 1-2)",
                "Portfolio positioning (Month 2-3)",
                "Specialization development (Month 3-6)",
                "Premium client acquisition (Month 6+)"
            ]
        }
    
    def _assess_business_risks(self, context: ConversationContext) -> List[Dict[str, str]]:
        """Assess business risks"""
        risks = [
            {
                "risk": "Under-pricing services",
                "impact": "High",
                "mitigation": "Implement market-based rate increases"
            },
            {
                "risk": "Generalist positioning",
                "impact": "Medium",
                "mitigation": "Develop clear specialization strategy"
            },
            {
                "risk": "Inconsistent lead generation",
                "impact": "High",
                "mitigation": "Build systematic marketing and referral systems"
            }
        ]
        
        return risks
    
    def _identify_optimization_opportunities(self, context: ConversationContext) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities"""
        opportunities = [
            {
                "area": "Pricing Strategy",
                "potential": "25-50% revenue increase",
                "effort": "Low",
                "timeline": "Immediate"
            },
            {
                "area": "Portfolio Optimization",
                "potential": "60-80% lead quality improvement",
                "effort": "Medium",
                "timeline": "1-2 months"
            },
            {
                "area": "Specialization Development",
                "potential": "40% rate premium",
                "effort": "Medium",
                "timeline": "3-6 months"
            }
        ]
        
        return opportunities