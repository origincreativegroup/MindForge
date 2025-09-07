# backend/services/creator_business_intelligence.py

import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import openai
from sqlalchemy.orm import Session

from .models import Project, Skill, Client, Asset, ProjectStatus
from ..schemas import ProjectStatus as ProjectStatusEnum


@dataclass
class OpportunityLead:
    """Represents a potential work opportunity for a creator"""
    title: str
    company: str
    source: str  # upwork, linkedin, twitter, etc.
    url: str
    description: str
    estimated_budget: Optional[float]
    match_score: float
    skills_required: List[str]
    deadline: Optional[datetime]
    posted_date: datetime
    competition_level: str  # low, medium, high


@dataclass
class CreatorInsight:
    """AI-generated insight for creator business development"""
    type: str
    title: str
    description: str
    action_items: List[str]
    potential_impact: str
    priority: int  # 1-5, 1 being highest


class CreatorBusinessIntelligence:
    """AI-powered business intelligence system for individual creators"""

    def __init__(self, db: Session):
        self.db = db
        try:
            self.openai_client = openai.Client() if hasattr(openai, 'api_key') and openai.api_key else None
        except:
            self.openai_client = None

    async def analyze_creator_portfolio(self, creator_id: int) -> Dict[str, Any]:
        """Comprehensive analysis of creator's portfolio for business optimization"""
        
        # Get creator's projects (using existing Project model)
        projects = self.db.query(Project).filter(
            Project.client_id == creator_id  # Assuming creator_id maps to client_id for now
        ).all()
        
        if not projects:
            return {"error": "No projects found for analysis"}
        
        # Parallel analysis tasks
        analysis_tasks = [
            self._analyze_portfolio_gaps(projects),
            self._calculate_market_positioning(projects),
            self._suggest_rate_optimization(projects),
            self._identify_niche_opportunities(projects),
            self._assess_portfolio_conversion_potential(projects)
        ]
        
        results = await asyncio.gather(*analysis_tasks)
        
        return {
            "portfolio_gaps": results[0],
            "market_positioning": results[1],
            "rate_optimization": results[2],
            "niche_opportunities": results[3],
            "conversion_potential": results[4],
            "overall_score": self._calculate_portfolio_score(results),
            "next_actions": self._generate_action_plan(results)
        }

    async def find_opportunities(self, creator_id: int, limit: int = 20) -> List[OpportunityLead]:
        """Actively search for work opportunities matching creator's skills"""
        
        creator_profile = self._get_creator_profile(creator_id)
        opportunities = []
        
        # Search multiple sources in parallel
        search_tasks = [
            self._search_upwork(creator_profile),
            self._search_freelancer_com(creator_profile),
            self._search_linkedin_jobs(creator_profile),
            self._search_twitter_mentions(creator_profile),
            self._search_angel_list(creator_profile),
            self._search_reddit_freelance(creator_profile)
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine and rank opportunities
        for result in results:
            if isinstance(result, list):
                opportunities.extend(result)
        
        # Sort by match score and filter
        opportunities.sort(key=lambda x: x.match_score, reverse=True)
        return opportunities[:limit]

    async def generate_proposal(self, creator_id: int, opportunity: OpportunityLead) -> str:
        """Generate customized proposal for a specific opportunity"""
        
        creator_profile = self._get_creator_profile(creator_id)
        relevant_projects = self._get_relevant_projects(creator_id, opportunity.skills_required)
        
        if not self.openai_client:
            return self._generate_template_proposal(creator_profile, opportunity, relevant_projects)
        
        prompt = self._build_proposal_prompt(creator_profile, opportunity, relevant_projects)
        
        try:
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert freelance proposal writer who helps creators win high-value projects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"AI proposal generation failed: {e}")
            return self._generate_template_proposal(creator_profile, opportunity, relevant_projects)

    async def optimize_portfolio_for_conversion(self, creator_id: int) -> Dict[str, Any]:
        """Analyze and optimize portfolio for maximum client conversion"""
        
        projects = self._get_creator_projects(creator_id)
        portfolio_analytics = self._get_portfolio_analytics(creator_id)
        
        # Analyze conversion funnel
        conversion_analysis = {
            "current_metrics": {
                "view_to_inquiry_rate": portfolio_analytics.get("view_to_inquiry_rate", 0.05),
                "inquiry_to_project_rate": portfolio_analytics.get("inquiry_to_project_rate", 0.25),
                "average_project_value": portfolio_analytics.get("avg_project_value", 5000)
            },
            "optimization_opportunities": [],
            "recommended_changes": [],
            "projected_impact": {}
        }
        
        # Analyze project presentation
        for project in projects:
            project_analysis = await self._analyze_project_conversion_potential(project)
            if project_analysis["improvement_potential"] > 0.2:
                conversion_analysis["optimization_opportunities"].append({
                    "project_id": project.id,
                    "project_name": project.title,
                    "current_score": project_analysis["current_score"],
                    "potential_score": project_analysis["potential_score"],
                    "improvements": project_analysis["improvements"]
                })
        
        # Generate specific recommendations
        conversion_analysis["recommended_changes"] = await self._generate_conversion_recommendations(
            projects, portfolio_analytics
        )
        
        return conversion_analysis

    async def track_market_trends(self, creator_skills: List[str]) -> Dict[str, Any]:
        """Track market trends relevant to creator's skills"""
        
        trend_data = {
            "skill_demand": {},
            "rate_trends": {},
            "emerging_opportunities": [],
            "competition_analysis": {},
            "market_forecast": {}
        }
        
        for skill in creator_skills:
            # Analyze demand trends
            demand_data = await self._analyze_skill_demand(skill)
            trend_data["skill_demand"][skill] = demand_data
            
            # Rate analysis
            rate_data = await self._analyze_market_rates(skill)
            trend_data["rate_trends"][skill] = rate_data
        
        # Identify emerging opportunities
        trend_data["emerging_opportunities"] = await self._identify_emerging_trends(creator_skills)
        
        return trend_data

    # Private helper methods

    async def _analyze_portfolio_gaps(self, projects: List[Project]) -> Dict[str, Any]:
        """Identify gaps in portfolio that limit earning potential"""
        
        # Analyze project types and identify missing high-value categories
        project_disciplines = []
        for project in projects:
            if project.disciplines:
                project_disciplines.extend(project.disciplines)
        
        discipline_counter = {}
        for discipline in project_disciplines:
            discipline_counter[discipline] = discipline_counter.get(discipline, 0) + 1
        
        # High-value categories that are missing or underrepresented
        high_value_categories = [
            "mobile_app_design", "saas_dashboard", "e_commerce", 
            "brand_identity", "web_application", "user_research"
        ]
        
        gaps = []
        for category in high_value_categories:
            if category not in discipline_counter:
                gaps.append({
                    "category": category,
                    "reason": "missing_entirely",
                    "market_value": self._get_category_market_value(category),
                    "recommendation": f"Add {category} project to increase portfolio value"
                })
            elif discipline_counter[category] < 2:
                gaps.append({
                    "category": category,
                    "reason": "underrepresented", 
                    "current_count": discipline_counter[category],
                    "recommendation": f"Add more {category} projects to establish expertise"
                })
        
        return {
            "identified_gaps": gaps,
            "portfolio_completeness": len(project_disciplines) / len(high_value_categories) if high_value_categories else 0,
            "priority_additions": gaps[:3]  # Top 3 priorities
        }

    async def _calculate_market_positioning(self, projects: List[Project]) -> Dict[str, Any]:
        """Calculate creator's position in the market"""
        
        # Analyze project quality scores (using mock data for now)
        quality_scores = [75 + (i * 5) % 20 for i, p in enumerate(projects)]  # Mock quality scores
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 70
        
        # Estimate market percentile based on quality and portfolio diversity
        all_disciplines = []
        for project in projects:
            if project.disciplines:
                all_disciplines.extend(project.disciplines)
        portfolio_diversity = len(set(all_disciplines))
        
        # Simple scoring algorithm (would be more sophisticated in production)
        market_percentile = min(95, (avg_quality * 0.7) + (portfolio_diversity * 5))
        
        return {
            "quality_score": avg_quality,
            "portfolio_diversity": portfolio_diversity,
            "market_percentile": market_percentile,
            "competitive_advantages": self._identify_competitive_advantages(projects),
            "positioning_recommendations": self._generate_positioning_advice(avg_quality, portfolio_diversity)
        }

    async def _suggest_rate_optimization(self, projects: List[Project]) -> Dict[str, Any]:
        """Analyze and suggest optimal pricing strategy"""
        
        # Calculate current portfolio value indicators (mock data)
        project_values = [5000 + (i * 1000) for i, p in enumerate(projects)]
        avg_project_value = sum(project_values) / len(project_values) if project_values else 5000
        
        # Market research for similar skill sets
        skill_set = self._extract_skills_from_projects(projects)
        market_rates = await self._research_market_rates(skill_set)
        
        # Calculate suggested rates
        suggested_hourly = market_rates.get("hourly_75th_percentile", 85)
        suggested_project_min = market_rates.get("project_minimum", 2500)
        
        return {
            "current_indicators": {
                "avg_project_value": avg_project_value,
                "estimated_hourly_equivalent": avg_project_value / 40  # Assuming 40 hours per project
            },
            "market_analysis": market_rates,
            "recommendations": {
                "suggested_hourly_rate": suggested_hourly,
                "suggested_project_minimum": suggested_project_min,
                "rate_increase_timeline": "Implement 15% increase over next 3 months"
            },
            "justification_points": [
                "Portfolio quality above 75th percentile",
                "Diverse skill set commands premium",
                "Strong case studies demonstrate ROI"
            ]
        }

    async def _identify_niche_opportunities(self, projects: List[Project]) -> Dict[str, Any]:
        """Identify profitable niche opportunities based on project history"""
        
        # Analyze project patterns to identify potential niches
        project_analysis = {}
        for project in projects:
            # Extract industry from client info (mock data)
            industry = "general"  # Would extract from project.client or project data
            if industry not in project_analysis:
                project_analysis[industry] = {
                    "project_count": 0,
                    "avg_value": 0,
                    "success_rate": 0,
                    "project_types": []
                }
            
            project_analysis[industry]["project_count"] += 1
            if project.disciplines:
                project_analysis[industry]["project_types"].extend(project.disciplines)
        
        # Identify underserved but profitable niches
        niche_opportunities = []
        
        # Example niches with high demand and lower competition
        emerging_niches = [
            {"name": "SaaS Onboarding Design", "market_size": "Growing", "competition": "Low"},
            {"name": "Sustainable Brand Design", "market_size": "Emerging", "competition": "Low"},
            {"name": "AI/ML Product Interfaces", "market_size": "Rapid Growth", "competition": "Medium"},
            {"name": "Remote Work Tools Design", "market_size": "Stable", "competition": "Medium"}
        ]
        
        for niche in emerging_niches:
            if self._creator_skills_match_niche(projects, niche["name"]):
                niche_opportunities.append({
                    **niche,
                    "fit_score": self._calculate_niche_fit(projects, niche["name"]),
                    "entry_strategy": self._suggest_niche_entry_strategy(projects, niche["name"])
                })
        
        return {
            "current_specializations": project_analysis,
            "emerging_opportunities": niche_opportunities,
            "recommended_focus": niche_opportunities[0] if niche_opportunities else None
        }

    async def _assess_portfolio_conversion_potential(self, projects: List[Project]) -> Dict[str, Any]:
        """Assess how well the portfolio converts visitors to clients"""
        
        total_conversion_score = 0
        project_scores = []
        
        for project in projects:
            score = 0.6  # Base score for having a project
            
            # Check for case study
            if hasattr(project, 'case_study') and project.case_study:
                score += 0.2
            
            # Check for assets (portfolio pieces)
            if project.assets:
                score += 0.15
            
            # Check for completed status
            if project.status == ProjectStatus.shipped:
                score += 0.05
            
            project_scores.append(score)
            total_conversion_score += score
        
        avg_conversion_score = total_conversion_score / len(projects) if projects else 0
        
        return {
            "overall_conversion_score": avg_conversion_score,
            "project_scores": project_scores,
            "improvement_recommendations": [
                "Add detailed case studies to top 3 projects",
                "Include client testimonials",
                "Show measurable results and ROI",
                "Add process documentation"
            ]
        }

    # Opportunity search methods
    async def _search_upwork(self, creator_profile: Dict) -> List[OpportunityLead]:
        """Search Upwork for relevant opportunities"""
        # Mock implementation for demonstration
        opportunities = [
            OpportunityLead(
                title="Mobile App UI Design for Fitness Startup",
                company="FitTech Inc",
                source="upwork",
                url="https://upwork.com/job/123",
                description="Looking for experienced mobile designer for iOS/Android fitness app",
                estimated_budget=8000.0,
                match_score=0.92,
                skills_required=["Mobile Design", "UI/UX", "Fitness Apps"],
                deadline=datetime.now() + timedelta(days=30),
                posted_date=datetime.now() - timedelta(days=2),
                competition_level="medium"
            ),
            OpportunityLead(
                title="SaaS Dashboard Redesign",
                company="DataFlow Solutions",
                source="upwork",
                url="https://upwork.com/job/124",
                description="Redesign existing dashboard for better UX and data visualization",
                estimated_budget=12000.0,
                match_score=0.88,
                skills_required=["Dashboard Design", "Data Visualization", "SaaS"],
                deadline=datetime.now() + timedelta(days=45),
                posted_date=datetime.now() - timedelta(days=1),
                competition_level="high"
            )
        ]
        
        return opportunities

    async def _search_freelancer_com(self, creator_profile: Dict) -> List[OpportunityLead]:
        """Search Freelancer.com for opportunities"""
        return []  # Mock implementation

    async def _search_linkedin_jobs(self, creator_profile: Dict) -> List[OpportunityLead]:
        """Search LinkedIn for freelance opportunities"""
        return []  # Mock implementation

    async def _search_twitter_mentions(self, creator_profile: Dict) -> List[OpportunityLead]:
        """Search Twitter for "looking for designer" type mentions"""
        return []  # Mock implementation

    async def _search_angel_list(self, creator_profile: Dict) -> List[OpportunityLead]:
        """Search AngelList for startup design opportunities"""
        return []  # Mock implementation

    async def _search_reddit_freelance(self, creator_profile: Dict) -> List[OpportunityLead]:
        """Search Reddit freelance communities"""
        return []  # Mock implementation

    def _get_creator_profile(self, creator_id: int) -> Dict[str, Any]:
        """Get creator profile data"""
        # Mock implementation - would fetch from database
        return {
            "name": "Alex Chen",
            "skills": ["UI Design", "Mobile Apps", "Branding"],
            "experience_years": 5,
            "specializations": ["Mobile UI", "SaaS Design"],
            "portfolio_url": "alexchen.design",
            "hourly_rate": 85
        }

    def _get_relevant_projects(self, creator_id: int, required_skills: List[str]) -> List[Project]:
        """Get projects relevant to the opportunity"""
        projects = self.db.query(Project).filter(
            Project.client_id == creator_id
        ).all()
        
        # Filter projects by skills (simplified implementation)
        relevant_projects = []
        for project in projects:
            if project.skills:
                project_skill_names = [str(skill.name) if hasattr(skill, 'name') else str(skill) for skill in project.skills]
                if any(skill.lower() in ' '.join(project_skill_names).lower() for skill in required_skills):
                    relevant_projects.append(project)
        
        return relevant_projects

    def _get_creator_projects(self, creator_id: int) -> List[Project]:
        """Get all projects for a creator"""
        return self.db.query(Project).filter(
            Project.client_id == creator_id
        ).all()

    def _get_portfolio_analytics(self, creator_id: int) -> Dict[str, Any]:
        """Get portfolio analytics data"""
        # Mock analytics data
        return {
            "view_to_inquiry_rate": 0.05,
            "inquiry_to_project_rate": 0.25,
            "avg_project_value": 7500,
            "total_views": 1250,
            "total_inquiries": 63,
            "total_projects": 16
        }

    def _build_proposal_prompt(self, creator_profile: Dict, opportunity: OpportunityLead, projects: List) -> str:
        """Build prompt for AI proposal generation"""
        
        return f"""
        Write a compelling freelance proposal for this opportunity:
        
        JOB: {opportunity.title} at {opportunity.company}
        DESCRIPTION: {opportunity.description}
        BUDGET: ${opportunity.estimated_budget}
        SKILLS NEEDED: {', '.join(opportunity.skills_required)}
        
        CREATOR PROFILE:
        Name: {creator_profile['name']}
        Experience: {creator_profile['experience_years']} years
        Skills: {', '.join(creator_profile['skills'])}
        Specializations: {', '.join(creator_profile.get('specializations', []))}
        Rate: ${creator_profile['hourly_rate']}/hour
        
        RELEVANT PROJECTS: {len(projects)} similar projects in portfolio
        
        Write a personalized, compelling proposal that:
        1. Shows clear understanding of their needs
        2. Highlights relevant experience and results
        3. Demonstrates value and ROI
        4. Includes a clear next step
        5. Is professional but friendly
        
        Keep it concise (under 200 words) and compelling.
        """

    def _generate_template_proposal(self, creator_profile: Dict, opportunity: OpportunityLead, projects: List) -> str:
        """Generate a template proposal when AI is not available"""
        
        return f"""
        Hi {opportunity.company} team,
        
        I'm excited about your {opportunity.title} project. With {creator_profile['experience_years']} years of experience in {', '.join(creator_profile['skills'])}, I've helped similar companies achieve great results.
        
        What makes me a great fit:
        • {len(projects)} relevant projects in my portfolio
        • Specialization in {', '.join(creator_profile.get('specializations', []))}
        • Track record of delivering on time and on budget
        
        I'd love to discuss how I can help bring your vision to life. My rate is ${creator_profile['hourly_rate']}/hour, and I'm available to start immediately.
        
        Best regards,
        {creator_profile['name']}
        Portfolio: {creator_profile.get('portfolio_url', 'Available upon request')}
        """

    # Additional helper methods
    def _calculate_portfolio_score(self, analysis_results: List) -> float:
        """Calculate overall portfolio score from analysis results"""
        # Simple scoring based on analysis results
        portfolio_gaps = analysis_results[0]
        market_positioning = analysis_results[1]
        
        # Score based on portfolio completeness and market positioning
        completeness_score = portfolio_gaps.get("portfolio_completeness", 0.5)
        positioning_score = market_positioning.get("market_percentile", 50) / 100
        
        return (completeness_score * 0.4) + (positioning_score * 0.6)

    def _generate_action_plan(self, analysis_results: List) -> List[str]:
        """Generate actionable recommendations"""
        actions = []
        
        # Add actions based on gaps
        portfolio_gaps = analysis_results[0]
        if portfolio_gaps.get("priority_additions"):
            for gap in portfolio_gaps["priority_additions"]:
                actions.append(gap.get("recommendation", "Improve portfolio diversity"))
        
        # Add rate optimization action
        rate_optimization = analysis_results[2]
        if rate_optimization.get("recommendations", {}).get("suggested_hourly_rate"):
            suggested_rate = rate_optimization["recommendations"]["suggested_hourly_rate"]
            actions.append(f"Increase hourly rate to ${suggested_rate} based on market analysis")
        
        # Add conversion optimization
        conversion_potential = analysis_results[4]
        if conversion_potential.get("improvement_recommendations"):
            actions.extend(conversion_potential["improvement_recommendations"][:2])
        
        return actions[:5]  # Limit to top 5 actions

    def _get_category_market_value(self, category: str) -> float:
        """Get market value for a project category"""
        market_values = {
            "mobile_app_design": 8500,
            "saas_dashboard": 12000,
            "e_commerce": 9500,
            "brand_identity": 7500,
            "web_application": 10000,
            "user_research": 6500
        }
        return market_values.get(category, 5000)

    def _identify_competitive_advantages(self, projects: List[Project]) -> List[str]:
        """Identify competitive advantages from project portfolio"""
        advantages = []
        
        # Check for diverse skill set
        all_skills = []
        for project in projects:
            if project.skills:
                all_skills.extend([str(skill.name) if hasattr(skill, 'name') else str(skill) for skill in project.skills])
        
        unique_skills = set(all_skills)
        if len(unique_skills) > 8:
            advantages.append("Diverse skill set across multiple disciplines")
        
        # Check for project complexity
        if len(projects) > 10:
            advantages.append("Extensive portfolio with proven track record")
        
        # Check for case studies
        case_study_count = sum(1 for p in projects if hasattr(p, 'case_study') and p.case_study)
        if case_study_count > 3:
            advantages.append("Strong case study documentation")
        
        return advantages

    def _generate_positioning_advice(self, avg_quality: float, portfolio_diversity: int) -> List[str]:
        """Generate positioning advice based on quality and diversity"""
        advice = []
        
        if avg_quality > 80:
            advice.append("Position as premium designer with high-quality deliverables")
        elif avg_quality > 70:
            advice.append("Emphasize value and reliability in positioning")
        else:
            advice.append("Focus on improving project quality before premium positioning")
        
        if portfolio_diversity > 5:
            advice.append("Leverage diverse skill set as competitive advantage")
        else:
            advice.append("Consider specializing in 2-3 core areas for stronger positioning")
        
        return advice

    def _extract_skills_from_projects(self, projects: List[Project]) -> List[str]:
        """Extract all skills from project portfolio"""
        all_skills = []
        for project in projects:
            if project.skills:
                all_skills.extend([str(skill.name) if hasattr(skill, 'name') else str(skill) for skill in project.skills])
            if project.disciplines:
                all_skills.extend([str(discipline) for discipline in project.disciplines])
        
        return list(set(all_skills))

    async def _research_market_rates(self, skill_set: List[str]) -> Dict[str, float]:
        """Research market rates for given skill set"""
        # Mock market research data
        base_rates = {
            "UI Design": 75,
            "UX Design": 85, 
            "Mobile Design": 90,
            "Web Design": 70,
            "Branding": 80,
            "Illustration": 65,
            "Dashboard Design": 95,
            "Data Visualization": 90
        }
        
        # Calculate weighted average based on skills
        total_rate = sum(base_rates.get(skill, 70) for skill in skill_set)
        avg_rate = total_rate / len(skill_set) if skill_set else 70
        
        return {
            "hourly_median": avg_rate,
            "hourly_75th_percentile": avg_rate * 1.25,
            "hourly_90th_percentile": avg_rate * 1.5,
            "project_minimum": avg_rate * 30,  # ~30 hours minimum
            "retainer_monthly": avg_rate * 40   # ~40 hours per month
        }

    def _creator_skills_match_niche(self, projects: List[Project], niche_name: str) -> bool:
        """Check if creator's skills match a specific niche"""
        all_skills = self._extract_skills_from_projects(projects)
        all_skills_lower = [str(skill).lower() for skill in all_skills if skill]  # Convert to string first
        niche_lower = niche_name.lower()
        
        # Simple matching logic
        if "saas" in niche_lower and any("web" in skill or "ui" in skill for skill in all_skills_lower):
            return True
        if "brand" in niche_lower and any("brand" in skill or "identity" in skill for skill in all_skills_lower):
            return True
        if "ai" in niche_lower or "ml" in niche_lower:
            return any("interface" in skill or "ui" in skill for skill in all_skills_lower)
        if "remote" in niche_lower:
            return any("web" in skill or "app" in skill for skill in all_skills_lower)
        
        return False

    def _calculate_niche_fit(self, projects: List[Project], niche_name: str) -> float:
        """Calculate how well creator fits a specific niche"""
        if self._creator_skills_match_niche(projects, niche_name):
            return 0.8
        return 0.3

    def _suggest_niche_entry_strategy(self, projects: List[Project], niche_name: str) -> str:
        """Suggest strategy for entering a specific niche"""
        strategies = {
            "SaaS Onboarding Design": "Create 2-3 onboarding flow case studies, specialize in user activation metrics",
            "Sustainable Brand Design": "Develop eco-friendly design principles, partner with sustainable businesses",
            "AI/ML Product Interfaces": "Study AI/ML concepts, create interfaces for data visualization and model interaction",
            "Remote Work Tools Design": "Focus on collaboration and productivity tools, understand remote work pain points"
        }
        return strategies.get(niche_name, "Research the niche deeply and create targeted portfolio pieces")

    async def _analyze_project_conversion_potential(self, project: Project) -> Dict[str, Any]:
        """Analyze how well a project converts viewers to clients"""
        current_score = 0.5  # Base score
        improvements = []
        
        # Check for case study
        if not (hasattr(project, 'case_study') and project.case_study):
            improvements.append("Add complete case study with problem, solution, and results")
        else:
            current_score += 0.25
        
        # Check for assets
        if not project.assets:
            improvements.append("Add visual portfolio pieces and process documentation")
        else:
            current_score += 0.15
        
        # Check if project is completed
        if project.status != ProjectStatus.shipped:
            improvements.append("Document project outcomes and results")
        else:
            current_score += 0.1
        
        potential_score = min(1.0, current_score + (len(improvements) * 0.15))
        
        return {
            "current_score": current_score,
            "potential_score": potential_score,
            "improvement_potential": potential_score - current_score,
            "improvements": improvements
        }

    async def _generate_conversion_recommendations(self, projects: List[Project], portfolio_analytics: Dict) -> List[str]:
        """Generate specific recommendations for portfolio conversion"""
        recommendations = []
        
        # Check conversion rates
        inquiry_rate = portfolio_analytics.get("inquiry_to_project_rate", 0)
        if inquiry_rate < 0.2:
            recommendations.append("Improve project presentation and case study quality")
        
        view_rate = portfolio_analytics.get("view_to_inquiry_rate", 0)
        if view_rate < 0.03:
            recommendations.append("Optimize portfolio for better visitor engagement")
        
        # Check project documentation
        case_study_count = sum(1 for p in projects if hasattr(p, 'case_study') and p.case_study)
        if case_study_count < len(projects) * 0.5:
            recommendations.append("Add case studies to at least 50% of portfolio projects")
        
        return recommendations

    async def _analyze_skill_demand(self, skill: str) -> Dict[str, Any]:
        """Analyze market demand for a specific skill"""
        # Mock demand analysis
        demand_levels = {
            "UI Design": {"demand_level": "High", "growth_rate": "12%", "job_postings": 1250},
            "UX Design": {"demand_level": "Very High", "growth_rate": "18%", "job_postings": 1850},
            "Mobile Design": {"demand_level": "High", "growth_rate": "15%", "job_postings": 980},
            "Web Design": {"demand_level": "Medium", "growth_rate": "8%", "job_postings": 2100},
            "Branding": {"demand_level": "Medium", "growth_rate": "6%", "job_postings": 750}
        }
        
        return demand_levels.get(skill, {
            "demand_level": "Medium", 
            "growth_rate": "10%", 
            "job_postings": 500
        })

    async def _analyze_market_rates(self, skill: str) -> Dict[str, Any]:
        """Analyze market rates for a specific skill"""
        # Mock rate analysis
        rate_data = {
            "UI Design": {"median_hourly": 75, "range_low": 45, "range_high": 120, "trend": "stable"},
            "UX Design": {"median_hourly": 85, "range_low": 55, "range_high": 150, "trend": "increasing"},
            "Mobile Design": {"median_hourly": 90, "range_low": 60, "range_high": 140, "trend": "increasing"},
            "Web Design": {"median_hourly": 70, "range_low": 40, "range_high": 110, "trend": "stable"},
            "Branding": {"median_hourly": 80, "range_low": 50, "range_high": 130, "trend": "stable"}
        }
        
        return rate_data.get(skill, {
            "median_hourly": 75, 
            "range_low": 45, 
            "range_high": 120, 
            "trend": "stable"
        })

    async def _identify_emerging_trends(self, creator_skills: List[str]) -> List[Dict[str, Any]]:
        """Identify emerging market trends relevant to creator's skills"""
        all_trends = [
            {
                "trend": "AI-Assisted Design Tools",
                "relevance_score": 0.9,
                "opportunity": "Learn AI tools integration, offer AI-enhanced design services",
                "market_size": "Growing rapidly"
            },
            {
                "trend": "Sustainable Design Practices",
                "relevance_score": 0.7,
                "opportunity": "Specialize in eco-friendly design solutions",
                "market_size": "Emerging"
            },
            {
                "trend": "Voice UI Design",
                "relevance_score": 0.6,
                "opportunity": "Expand into voice interface design",
                "market_size": "Niche but growing"
            },
            {
                "trend": "Micro-Interactions and Animations",
                "relevance_score": 0.8,
                "opportunity": "Add motion design skills to service offering",
                "market_size": "Steady demand"
            }
        ]
        
        # Filter trends based on creator's skills
        relevant_trends = []
        for trend in all_trends:
            if any(skill.lower() in ["ui", "ux", "design", "web", "mobile"] for skill in creator_skills):
                relevant_trends.append(trend)
        
        return relevant_trends


# Additional supporting classes

class PortfolioOptimizer:
    """Specialized class for portfolio optimization"""

    def __init__(self):
        self.conversion_factors = {
            "case_study_completeness": 0.25,
            "visual_quality": 0.20,
            "results_documentation": 0.20,
            "client_testimonials": 0.15,
            "process_transparency": 0.10,
            "technical_skills_demo": 0.10
        }

    async def analyze_project_conversion_potential(self, project: Project) -> Dict[str, Any]:
        """Analyze how well a project converts viewers to clients"""
        
        current_score = 0.0
        improvements = []
        
        # Check case study completeness
        if not (hasattr(project, 'case_study') and project.case_study):
            improvements.append("Add complete case study with problem, solution, and results")
        else:
            current_score += self.conversion_factors["case_study_completeness"]
        
        # Check for client testimonials (mock check)
        if not hasattr(project, 'testimonial'):
            improvements.append("Add client testimonial or feedback")
        else:
            current_score += self.conversion_factors["client_testimonials"]
        
        # Check for measurable results
        if not (hasattr(project, 'case_study') and project.case_study and 
                getattr(project.case_study, 'metrics', None)):
            improvements.append("Document quantifiable results (metrics, ROI, improvements)")
        else:
            current_score += self.conversion_factors["results_documentation"]
        
        # Check visual quality (based on assets)
        if project.assets and len(project.assets) > 0:
            current_score += self.conversion_factors["visual_quality"]
        else:
            improvements.append("Add high-quality visual assets")
        
        potential_score = current_score + (len(improvements) * 0.1)
        
        return {
            "current_score": current_score,
            "potential_score": min(1.0, potential_score),
            "improvement_potential": min(1.0, potential_score) - current_score,
            "improvements": improvements
        }


class MarketIntelligence:
    """Market research and intelligence gathering"""

    async def get_market_rates(self, skills: List[str], location: str = "US") -> Dict[str, float]:
        """Get current market rates for specific skills"""
        
        # Mock market data (would integrate with real APIs in production)
        base_rates = {
            "UI Design": 75,
            "UX Design": 85, 
            "Mobile Design": 90,
            "Web Design": 70,
            "Branding": 80,
            "Illustration": 65,
            "Dashboard Design": 95,
            "Data Visualization": 90
        }
        
        # Calculate weighted average based on skills
        total_rate = sum(base_rates.get(skill, 70) for skill in skills)
        avg_rate = total_rate / len(skills) if skills else 70
        
        return {
            "hourly_median": avg_rate,
            "hourly_75th_percentile": avg_rate * 1.25,
            "hourly_90th_percentile": avg_rate * 1.5,
            "project_minimum": avg_rate * 30,  # ~30 hours minimum
            "retainer_monthly": avg_rate * 40   # ~40 hours per month
        }

    async def analyze_competition(self, creator_skills: List[str]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        
        return {
            "total_competitors": 15000,  # Mock data
            "top_10_percent_threshold": 95,
            "skills_saturation": {
                "UI Design": "High",
                "Mobile Design": "Medium", 
                "Branding": "Medium",
                "UX Design": "High",
                "Web Design": "Very High"
            },
            "opportunity_gaps": [
                "AI/ML interface design",
                "Sustainable design consulting",
                "Remote work tool UX",
                "Voice interface design"
            ],
            "competitive_advantages": [
                "Specialized niche expertise",
                "Strong case study documentation",
                "Proven ROI metrics",
                "Cross-disciplinary skills"
            ]
        }