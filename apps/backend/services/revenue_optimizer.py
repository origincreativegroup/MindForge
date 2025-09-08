"""
Revenue Optimization Engine - Core business model transformation system
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import math


class BusinessStage(Enum):
    """Business development stages for creators"""
    STARTING = "starting"  # Month 1-2: Portfolio Foundation
    GROWING = "growing"    # Month 3-6: Client Acquisition
    SCALING = "scaling"    # Month 6-12: Business Scaling
    EMPIRE = "empire"      # Year 2+: Creative Business Empire


class RevenueStream(Enum):
    """Different revenue streams for creators"""
    CLIENT_PROJECTS = "client_projects"
    RETAINER_CLIENTS = "retainer_clients"
    DIGITAL_PRODUCTS = "digital_products"
    EDUCATIONAL_CONTENT = "educational_content"
    SPEAKING_CONSULTING = "speaking_consulting"
    AFFILIATE_PARTNERSHIPS = "affiliate_partnerships"


@dataclass
class RevenueData:
    """Revenue data for a specific stream"""
    stream_type: RevenueStream
    monthly_amount: float
    growth_rate: float  # Monthly growth percentage
    consistency_score: float  # 0-1, how consistent the income is
    effort_required: float  # 0-1, how much ongoing effort required


@dataclass
class BusinessMetrics:
    """Core business metrics for optimization"""
    current_stage: BusinessStage
    monthly_revenue: float
    hourly_rate: float
    project_rate_range: tuple  # (min, max)
    client_count: int
    portfolio_quality_score: float  # 0-1
    market_position_percentile: float  # 0-100
    specialization_score: float  # 0-1, how specialized vs generalist


@dataclass
class OptimizationOpportunity:
    """Specific optimization opportunity"""
    area: str
    potential_increase: str  # e.g., "25-50% revenue increase"
    effort_level: str  # Low, Medium, High
    timeline: str  # e.g., "1-2 months"
    action_items: List[str]
    priority: int  # 1-5, 1 being highest


class RevenueOptimizer:
    """
    Core revenue optimization engine for creator business transformation
    """
    
    def __init__(self):
        self.stage_progression_map = {
            BusinessStage.STARTING: {
                "target_monthly_revenue": (2000, 4000),
                "focus_areas": ["portfolio_optimization", "rate_setting", "client_acquisition"],
                "key_metrics": ["portfolio_quality", "basic_rates", "first_clients"]
            },
            BusinessStage.GROWING: {
                "target_monthly_revenue": (4000, 8000),
                "focus_areas": ["rate_increases", "client_quality", "specialization"],
                "key_metrics": ["conversion_rates", "repeat_clients", "premium_pricing"]
            },
            BusinessStage.SCALING: {
                "target_monthly_revenue": (8000, 15000),
                "focus_areas": ["premium_positioning", "passive_income", "thought_leadership"],
                "key_metrics": ["waiting_list", "digital_products", "industry_recognition"]
            },
            BusinessStage.EMPIRE: {
                "target_monthly_revenue": (15000, 50000),
                "focus_areas": ["business_expansion", "team_building", "multiple_revenue_streams"],
                "key_metrics": ["agency_model", "speaking_revenue", "industry_influence"]
            }
        }
    
    def assess_business_stage(self, current_metrics: BusinessMetrics) -> Dict[str, Any]:
        """Determine creator's current business stage and readiness for progression"""
        
        # Determine current stage based on multiple factors
        stage_scores = {}
        
        for stage in BusinessStage:
            score = 0
            target_range = self.stage_progression_map[stage]["target_monthly_revenue"]
            
            # Revenue score (40% weight)
            if target_range[0] <= current_metrics.monthly_revenue <= target_range[1]:
                score += 40
            elif current_metrics.monthly_revenue > target_range[1]:
                score += 30  # Overpaid for stage
            else:
                # Below target, calculate partial score
                if current_metrics.monthly_revenue >= target_range[0] * 0.7:
                    score += 25
            
            # Portfolio quality score (25% weight)
            quality_bonus = current_metrics.portfolio_quality_score * 25
            score += quality_bonus
            
            # Market position score (20% weight)
            position_bonus = (current_metrics.market_position_percentile / 100) * 20
            score += position_bonus
            
            # Specialization score (15% weight)
            specialization_bonus = current_metrics.specialization_score * 15
            score += specialization_bonus
            
            stage_scores[stage] = score
        
        # Find the stage with highest score
        current_stage = max(stage_scores, key=stage_scores.get)
        confidence = stage_scores[current_stage] / 100
        
        # Determine next stage and readiness
        stages_list = list(BusinessStage)
        current_index = stages_list.index(current_stage)
        next_stage = stages_list[current_index + 1] if current_index < len(stages_list) - 1 else None
        
        # Calculate readiness for next stage
        readiness_score = 0
        if next_stage:
            next_target = self.stage_progression_map[next_stage]["target_monthly_revenue"]
            revenue_readiness = min(current_metrics.monthly_revenue / next_target[0], 1.0)
            readiness_score = (revenue_readiness * 0.6 + 
                             current_metrics.portfolio_quality_score * 0.25 + 
                             current_metrics.specialization_score * 0.15)
        
        return {
            "current_stage": current_stage.value,
            "confidence": confidence,
            "next_stage": next_stage.value if next_stage else None,
            "readiness_for_next": readiness_score,
            "stage_analysis": {
                "revenue_position": self._analyze_revenue_position(current_metrics, current_stage),
                "strengths": self._identify_stage_strengths(current_metrics, current_stage),
                "growth_blockers": self._identify_growth_blockers(current_metrics, current_stage)
            },
            "progression_timeline": self._calculate_progression_timeline(current_metrics, next_stage) if next_stage else None
        }
    
    def optimize_revenue_streams(self, current_revenue: List[RevenueData], target_stage: BusinessStage) -> Dict[str, Any]:
        """Optimize revenue stream mix for target business stage"""
        
        # Define optimal revenue stream mix for each stage
        optimal_mix = {
            BusinessStage.STARTING: {
                RevenueStream.CLIENT_PROJECTS: 0.90,
                RevenueStream.DIGITAL_PRODUCTS: 0.05,
                RevenueStream.EDUCATIONAL_CONTENT: 0.05
            },
            BusinessStage.GROWING: {
                RevenueStream.CLIENT_PROJECTS: 0.70,
                RevenueStream.RETAINER_CLIENTS: 0.15,
                RevenueStream.DIGITAL_PRODUCTS: 0.10,
                RevenueStream.EDUCATIONAL_CONTENT: 0.05
            },
            BusinessStage.SCALING: {
                RevenueStream.CLIENT_PROJECTS: 0.50,
                RevenueStream.RETAINER_CLIENTS: 0.25,
                RevenueStream.DIGITAL_PRODUCTS: 0.15,
                RevenueStream.EDUCATIONAL_CONTENT: 0.10
            },
            BusinessStage.EMPIRE: {
                RevenueStream.CLIENT_PROJECTS: 0.30,
                RevenueStream.RETAINER_CLIENTS: 0.20,
                RevenueStream.DIGITAL_PRODUCTS: 0.20,
                RevenueStream.EDUCATIONAL_CONTENT: 0.15,
                RevenueStream.SPEAKING_CONSULTING: 0.10,
                RevenueStream.AFFILIATE_PARTNERSHIPS: 0.05
            }
        }
        
        target_mix = optimal_mix[target_stage]
        current_total = sum(stream.monthly_amount for stream in current_revenue)
        
        # Calculate current mix
        current_mix = {}
        for stream in current_revenue:
            current_mix[stream.stream_type] = stream.monthly_amount / current_total if current_total > 0 else 0
        
        # Identify gaps and opportunities
        optimization_plan = []
        
        for stream_type, target_percentage in target_mix.items():
            current_percentage = current_mix.get(stream_type, 0)
            gap = target_percentage - current_percentage
            
            if gap > 0.05:  # Significant gap
                target_amount = current_total * target_percentage
                current_amount = current_total * current_percentage
                increase_needed = target_amount - current_amount
                
                optimization_plan.append({
                    "stream": stream_type.value,
                    "current_percentage": round(current_percentage * 100, 1),
                    "target_percentage": round(target_percentage * 100, 1),
                    "gap_percentage": round(gap * 100, 1),
                    "increase_needed": round(increase_needed, 0),
                    "priority": "high" if gap > 0.15 else "medium",
                    "action_plan": self._get_stream_action_plan(stream_type, increase_needed)
                })
        
        return {
            "current_mix": {k.value: round(v * 100, 1) for k, v in current_mix.items()},
            "target_mix": {k.value: round(v * 100, 1) for k, v in target_mix.items()},
            "optimization_opportunities": optimization_plan,
            "revenue_diversification_score": self._calculate_diversification_score(current_mix),
            "recommended_focus": self._get_revenue_focus_recommendations(optimization_plan)
        }
    
    def calculate_rate_progression(self, current_metrics: BusinessMetrics) -> Dict[str, Any]:
        """Calculate optimal rate progression strategy"""
        
        # Rate progression targets by stage
        rate_targets = {
            BusinessStage.STARTING: {"hourly": (45, 75), "project_min": 2500},
            BusinessStage.GROWING: {"hourly": (75, 125), "project_min": 5000},
            BusinessStage.SCALING: {"hourly": (125, 200), "project_min": 10000},
            BusinessStage.EMPIRE: {"hourly": (200, 500), "project_min": 25000}
        }
        
        current_stage = BusinessStage(current_metrics.current_stage)
        targets = rate_targets[current_stage]
        
        # Calculate rate increase recommendations
        current_hourly = current_metrics.hourly_rate
        target_hourly_range = targets["hourly"]
        
        rate_analysis = {
            "current_hourly": current_hourly,
            "target_range": target_hourly_range,
            "position_in_range": self._calculate_rate_position(current_hourly, target_hourly_range),
            "market_position": self._assess_market_position(current_hourly, current_stage),
            "increase_recommendations": []
        }
        
        # Immediate increase (30-60 days)
        if current_hourly < target_hourly_range[0]:
            immediate_increase = min(target_hourly_range[0], current_hourly * 1.20)  # Max 20% increase
            rate_analysis["increase_recommendations"].append({
                "timeframe": "immediate",
                "from_rate": current_hourly,
                "to_rate": immediate_increase,
                "increase_percentage": round(((immediate_increase - current_hourly) / current_hourly) * 100, 1),
                "justification": "Align with market standards for your experience level",
                "implementation": "Apply to all new client proposals starting next week"
            })
        
        # Medium-term increase (3-6 months)
        if current_hourly < target_hourly_range[1]:
            medium_term_rate = min(target_hourly_range[1], current_hourly * 1.50)
            rate_analysis["increase_recommendations"].append({
                "timeframe": "medium_term",
                "from_rate": current_hourly,
                "to_rate": medium_term_rate,
                "increase_percentage": round(((medium_term_rate - current_hourly) / current_hourly) * 100, 1),
                "justification": "Premium positioning based on specialization and results",
                "implementation": "Transition existing clients gradually, apply to all new clients"
            })
        
        # Project rate recommendations
        rate_analysis["project_pricing"] = {
            "minimum_project_value": targets["project_min"],
            "current_range": current_metrics.project_rate_range,
            "recommended_packages": self._create_pricing_packages(current_stage, target_hourly_range[1])
        }
        
        return rate_analysis
    
    def generate_growth_opportunities(self, current_metrics: BusinessMetrics) -> List[OptimizationOpportunity]:
        """Generate prioritized growth opportunities"""
        
        opportunities = []
        current_stage = BusinessStage(current_metrics.current_stage)
        
        # Rate optimization
        if current_metrics.hourly_rate < 100 and current_stage in [BusinessStage.GROWING, BusinessStage.SCALING]:
            opportunities.append(OptimizationOpportunity(
                area="Rate Optimization",
                potential_increase="25-50% revenue increase",
                effort_level="Low",
                timeline="1-2 months", 
                action_items=[
                    "Research market rates for your specialization",
                    "Prepare rate increase justification",
                    "Update proposals with new rates",
                    "Communicate changes to existing clients"
                ],
                priority=1
            ))
        
        # Portfolio specialization
        if current_metrics.specialization_score < 0.7:
            opportunities.append(OptimizationOpportunity(
                area="Specialization Development",
                potential_increase="40% rate premium",
                effort_level="Medium",
                timeline="3-6 months",
                action_items=[
                    "Identify profitable niche based on portfolio strength",
                    "Create specialized case studies",
                    "Update marketing materials to reflect specialization",
                    "Build authority content in chosen niche"
                ],
                priority=2
            ))
        
        # Client acquisition optimization
        if current_metrics.client_count < 3 and current_stage != BusinessStage.STARTING:
            opportunities.append(OptimizationOpportunity(
                area="Client Pipeline Development",
                potential_increase="60-80% lead quality improvement",
                effort_level="Medium",
                timeline="2-4 months",
                action_items=[
                    "Optimize portfolio for conversion",
                    "Develop referral system",
                    "Create content marketing strategy",
                    "Build strategic partnerships"
                ],
                priority=2
            ))
        
        # Passive income development
        if current_stage in [BusinessStage.SCALING, BusinessStage.EMPIRE]:
            opportunities.append(OptimizationOpportunity(
                area="Passive Income Streams",
                potential_increase="20-40% additional monthly revenue",
                effort_level="High",
                timeline="6-12 months",
                action_items=[
                    "Create digital product based on expertise",
                    "Develop online course or workshop",
                    "Build email list and marketing funnel",
                    "Launch affiliate partnerships"
                ],
                priority=3
            ))
        
        # Sort by priority
        opportunities.sort(key=lambda x: x.priority)
        
        return opportunities
    
    def forecast_revenue_potential(self, current_metrics: BusinessMetrics, optimization_plan: List[OptimizationOpportunity]) -> Dict[str, Any]:
        """Forecast revenue potential with optimization"""
        
        current_revenue = current_metrics.monthly_revenue
        current_stage = BusinessStage(current_metrics.current_stage)
        
        # Calculate potential increases from each opportunity
        total_potential_increase = 0
        timeline_projections = {}
        
        for opportunity in optimization_plan:
            # Extract percentage from potential_increase string
            potential_text = opportunity.potential_increase
            if "%" in potential_text:
                # Extract percentage (take the average if range like "25-50%")
                percentages = [float(x.split('%')[0]) for x in potential_text.split() if '%' in x]
                if '-' in potential_text:
                    avg_percentage = sum(percentages) / len(percentages) if percentages else 25
                else:
                    avg_percentage = percentages[0] if percentages else 25
                
                increase_amount = current_revenue * (avg_percentage / 100)
                total_potential_increase += increase_amount
                
                # Map to timeline
                timeline = opportunity.timeline
                if timeline not in timeline_projections:
                    timeline_projections[timeline] = 0
                timeline_projections[timeline] += increase_amount
        
        # Stage progression potential
        stages_list = list(BusinessStage)
        current_index = stages_list.index(current_stage)
        next_stage = stages_list[current_index + 1] if current_index < len(stages_list) - 1 else None
        
        stage_potential = {}
        if next_stage:
            next_targets = self.stage_progression_map[next_stage]["target_monthly_revenue"]
            stage_potential = {
                "next_stage": next_stage.value,
                "target_range": next_targets,
                "potential_increase": next_targets[0] - current_revenue if current_revenue < next_targets[0] else 0,
                "timeline": "6-12 months with optimization"
            }
        
        return {
            "current_monthly": current_revenue,
            "optimized_potential": current_revenue + total_potential_increase,
            "increase_potential": total_potential_increase,
            "percentage_increase": round((total_potential_increase / current_revenue) * 100, 1) if current_revenue > 0 else 0,
            "timeline_breakdown": timeline_projections,
            "stage_progression": stage_potential,
            "confidence_level": self._calculate_forecast_confidence(current_metrics, optimization_plan)
        }
    
    # Helper methods
    
    def _analyze_revenue_position(self, metrics: BusinessMetrics, stage: BusinessStage) -> str:
        """Analyze revenue position within stage"""
        target_range = self.stage_progression_map[stage]["target_monthly_revenue"]
        
        if metrics.monthly_revenue < target_range[0]:
            return f"Below target range (${target_range[0]:,} - ${target_range[1]:,})"
        elif metrics.monthly_revenue > target_range[1]:
            return f"Above target range - ready for next stage"
        else:
            return f"Within target range (${target_range[0]:,} - ${target_range[1]:,})"
    
    def _identify_stage_strengths(self, metrics: BusinessMetrics, stage: BusinessStage) -> List[str]:
        """Identify strengths for current stage"""
        strengths = []
        
        if metrics.portfolio_quality_score > 0.8:
            strengths.append("Strong portfolio quality")
        if metrics.hourly_rate > 100:
            strengths.append("Premium rate positioning")
        if metrics.specialization_score > 0.7:
            strengths.append("Clear specialization")
        if metrics.market_position_percentile > 80:
            strengths.append("Top-tier market position")
        
        return strengths
    
    def _identify_growth_blockers(self, metrics: BusinessMetrics, stage: BusinessStage) -> List[str]:
        """Identify factors blocking growth"""
        blockers = []
        
        if metrics.hourly_rate < 75:
            blockers.append("Below-market rates limiting revenue potential")
        if metrics.portfolio_quality_score < 0.6:
            blockers.append("Portfolio quality needs improvement")
        if metrics.specialization_score < 0.5:
            blockers.append("Lacks clear specialization for premium positioning")
        if metrics.client_count < 2:
            blockers.append("Insufficient client base for stability")
        
        return blockers
    
    def _calculate_progression_timeline(self, metrics: BusinessMetrics, next_stage: BusinessStage) -> str:
        """Calculate realistic timeline for stage progression"""
        if not next_stage:
            return None
            
        # Base timeline on current readiness factors
        readiness_factors = [
            metrics.portfolio_quality_score,
            metrics.specialization_score,
            min(metrics.hourly_rate / 100, 1.0),  # Normalize rate
            min(metrics.client_count / 5, 1.0)    # Normalize client count
        ]
        
        avg_readiness = sum(readiness_factors) / len(readiness_factors)
        
        if avg_readiness > 0.8:
            return "3-6 months"
        elif avg_readiness > 0.6:
            return "6-12 months"
        else:
            return "12-18 months"
    
    def _get_stream_action_plan(self, stream_type: RevenueStream, target_amount: float) -> List[str]:
        """Get action plan for developing specific revenue stream"""
        
        plans = {
            RevenueStream.DIGITAL_PRODUCTS: [
                "Identify top client pain points for product ideas",
                "Create templates from successful project deliverables",
                "Set up e-commerce platform (Gumroad, Etsy, etc.)",
                f"Target ${target_amount:,.0f}/month through product sales"
            ],
            RevenueStream.RETAINER_CLIENTS: [
                "Identify clients needing ongoing work",
                "Create retainer packages with clear scope",
                "Propose retainer model to top 3 clients",
                f"Secure ${target_amount:,.0f}/month in retainer income"
            ],
            RevenueStream.EDUCATIONAL_CONTENT: [
                "Develop course curriculum based on expertise",
                "Create lead magnets and email marketing",
                "Launch on platforms like Udemy or Teachable",
                f"Generate ${target_amount:,.0f}/month from courses"
            ],
            RevenueStream.SPEAKING_CONSULTING: [
                "Build speaker profile and portfolio",
                "Apply to industry conferences and events",
                "Develop consulting service packages",
                f"Achieve ${target_amount:,.0f}/month from speaking/consulting"
            ]
        }
        
        return plans.get(stream_type, [f"Develop {stream_type.value} to generate ${target_amount:,.0f}/month"])
    
    def _calculate_diversification_score(self, revenue_mix: Dict) -> float:
        """Calculate revenue diversification score (0-1)"""
        if not revenue_mix:
            return 0.0
        
        # Shannon diversity index adapted for revenue streams
        diversity = 0
        for percentage in revenue_mix.values():
            if percentage > 0:
                diversity -= percentage * math.log(percentage)
        
        # Normalize to 0-1 scale
        max_diversity = math.log(len(revenue_mix)) if len(revenue_mix) > 1 else 1
        return min(diversity / max_diversity, 1.0) if max_diversity > 0 else 0.0
    
    def _get_revenue_focus_recommendations(self, optimization_plan: List[Dict]) -> List[str]:
        """Get focused recommendations for revenue optimization"""
        recommendations = []
        
        high_priority = [item for item in optimization_plan if item["priority"] == "high"]
        if high_priority:
            recommendations.append(f"Priority focus: {high_priority[0]['stream'].replace('_', ' ').title()}")
        
        total_streams = len(optimization_plan)
        if total_streams > 3:
            recommendations.append("Consider focusing on 2-3 streams initially")
        
        passive_streams = [item for item in optimization_plan if item["stream"] in ["digital_products", "educational_content"]]
        if passive_streams:
            recommendations.append("Build passive income streams for long-term stability")
        
        return recommendations
    
    def _calculate_rate_position(self, current_rate: float, target_range: tuple) -> str:
        """Calculate position within target rate range"""
        if current_rate < target_range[0]:
            return "below_range"
        elif current_rate > target_range[1]:
            return "above_range"
        else:
            position = (current_rate - target_range[0]) / (target_range[1] - target_range[0])
            if position < 0.33:
                return "lower_third"
            elif position < 0.67:
                return "middle_third"
            else:
                return "upper_third"
    
    def _assess_market_position(self, hourly_rate: float, stage: BusinessStage) -> str:
        """Assess market position based on rate"""
        market_benchmarks = {
            BusinessStage.STARTING: {"median": 60, "75th": 75, "90th": 90},
            BusinessStage.GROWING: {"median": 85, "75th": 110, "90th": 135},
            BusinessStage.SCALING: {"median": 125, "75th": 160, "90th": 200},
            BusinessStage.EMPIRE: {"median": 200, "75th": 300, "90th": 450}
        }
        
        benchmarks = market_benchmarks[stage]
        
        if hourly_rate >= benchmarks["90th"]:
            return "top_10_percent"
        elif hourly_rate >= benchmarks["75th"]:
            return "top_25_percent"
        elif hourly_rate >= benchmarks["median"]:
            return "above_median"
        else:
            return "below_median"
    
    def _create_pricing_packages(self, stage: BusinessStage, target_hourly: float) -> List[Dict]:
        """Create tiered pricing packages"""
        packages = []
        
        # Basic package (80% of target hourly)
        basic_hourly = target_hourly * 0.8
        packages.append({
            "name": "Essential",
            "hourly_rate": basic_hourly,
            "project_minimum": basic_hourly * 20,
            "included": ["Core deliverables", "2 rounds of revisions", "Email support"]
        })
        
        # Standard package (target hourly)
        packages.append({
            "name": "Professional",
            "hourly_rate": target_hourly,
            "project_minimum": target_hourly * 30,
            "included": ["Core + enhanced deliverables", "3 rounds of revisions", "Priority support", "Strategy session"]
        })
        
        # Premium package (120% of target hourly)
        premium_hourly = target_hourly * 1.2
        packages.append({
            "name": "Premium",
            "hourly_rate": premium_hourly,
            "project_minimum": premium_hourly * 40,
            "included": ["Full service offering", "Unlimited revisions", "24/7 support", "Ongoing consultation"]
        })
        
        return packages
    
    def _calculate_forecast_confidence(self, metrics: BusinessMetrics, opportunities: List[OptimizationOpportunity]) -> float:
        """Calculate confidence level in revenue forecast"""
        confidence_factors = []
        
        # Portfolio quality factor
        confidence_factors.append(metrics.portfolio_quality_score)
        
        # Market position factor
        confidence_factors.append(metrics.market_position_percentile / 100)
        
        # Opportunity feasibility factor
        high_priority_count = len([op for op in opportunities if op.priority <= 2])
        feasibility_score = min(high_priority_count / 3, 1.0)  # 3+ high-priority opportunities = max confidence
        confidence_factors.append(feasibility_score)
        
        # Experience/specialization factor
        confidence_factors.append(metrics.specialization_score)
        
        return sum(confidence_factors) / len(confidence_factors)