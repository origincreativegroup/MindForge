#!/usr/bin/env python3
"""
Demo script for Creator Business Intelligence Service

This script demonstrates the main functionality of the creator business intelligence system.
"""

import sys
import asyncio
from pathlib import Path
from unittest.mock import Mock

# Add the apps directory to the path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "apps"))

from backend.services.creator_business_intelligence import (
    CreatorBusinessIntelligence,
    OpportunityLead,
    PortfolioOptimizer,
    MarketIntelligence
)
from backend.services.models import Project, ProjectStatus


def create_demo_db():
    """Create a mock database with realistic demo data"""
    db = Mock()
    
    # Create realistic mock skills
    skills = {
        "ui_design": Mock(name="UI Design"),
        "ux_design": Mock(name="UX Design"),
        "mobile_design": Mock(name="Mobile Design"),
        "web_design": Mock(name="Web Design"),
        "branding": Mock(name="Branding"),
        "data_viz": Mock(name="Data Visualization")
    }
    
    # Create demo projects
    projects = [
        Mock(
            id=1,
            title="E-commerce Mobile App",
            client_id=1,
            status=ProjectStatus.shipped,
            disciplines=["Mobile Design", "E-commerce", "UI/UX"],
            skills=[skills["ui_design"], skills["mobile_design"]],
            assets=[Mock(), Mock(), Mock()],
            case_study=Mock()
        ),
        Mock(
            id=2,
            title="SaaS Dashboard Redesign",
            client_id=1,
            status=ProjectStatus.shipped,
            disciplines=["Web Design", "Dashboard", "SaaS"],
            skills=[skills["web_design"], skills["data_viz"]],
            assets=[Mock(), Mock()],
            case_study=Mock()
        ),
        Mock(
            id=3,
            title="Startup Brand Identity",
            client_id=1,
            status=ProjectStatus.shipped,
            disciplines=["Branding", "Logo Design"],
            skills=[skills["branding"]],
            assets=[Mock()],
            case_study=None
        ),
        Mock(
            id=4,
            title="Banking App UX Research",
            client_id=1,
            status=ProjectStatus.in_progress,
            disciplines=["UX Research", "Mobile"],
            skills=[skills["ux_design"]],
            assets=[],
            case_study=None
        )
    ]
    
    # Configure query mock
    query_mock = Mock()
    query_mock.filter.return_value.all.return_value = projects
    db.query.return_value = query_mock
    
    return db


async def demo_portfolio_analysis():
    """Demonstrate portfolio analysis functionality"""
    print("\n🎯 PORTFOLIO ANALYSIS DEMO")
    print("=" * 50)
    
    db = create_demo_db()
    service = CreatorBusinessIntelligence(db)
    
    # Analyze portfolio
    analysis = await service.analyze_creator_portfolio(creator_id=1)
    
    print(f"Overall Portfolio Score: {analysis['overall_score']:.2f}")
    print(f"Portfolio Completeness: {analysis['portfolio_gaps']['portfolio_completeness']:.1%}")
    print(f"Market Percentile: {analysis['market_positioning']['market_percentile']:.0f}th")
    
    print("\n📈 TOP RECOMMENDATIONS:")
    for i, action in enumerate(analysis['next_actions'][:3], 1):
        print(f"{i}. {action}")
    
    print("\n🎯 PORTFOLIO GAPS:")
    for gap in analysis['portfolio_gaps']['priority_additions']:
        print(f"• {gap['category']}: {gap['recommendation']}")


async def demo_opportunity_finder():
    """Demonstrate opportunity finding functionality"""
    print("\n💼 OPPORTUNITY FINDER DEMO")
    print("=" * 50)
    
    db = create_demo_db()
    service = CreatorBusinessIntelligence(db)
    
    # Find opportunities
    opportunities = await service.find_opportunities(creator_id=1, limit=5)
    
    print(f"Found {len(opportunities)} opportunities:")
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp.title}")
        print(f"   Company: {opp.company}")
        print(f"   Budget: ${opp.estimated_budget:,.0f}")
        print(f"   Match Score: {opp.match_score:.1%}")
        print(f"   Skills: {', '.join(opp.skills_required)}")
        print(f"   Competition: {opp.competition_level}")


async def demo_proposal_generation():
    """Demonstrate AI proposal generation"""
    print("\n✍️  PROPOSAL GENERATION DEMO")
    print("=" * 50)
    
    db = create_demo_db()
    service = CreatorBusinessIntelligence(db)
    
    # Create sample opportunity
    opportunity = OpportunityLead(
        title="Mobile Banking App Redesign",
        company="FinTech Solutions Inc",
        source="upwork",
        url="https://upwork.com/job/example",
        description="Looking for an experienced mobile designer to redesign our banking app for better user experience and modern design.",
        estimated_budget=15000.0,
        match_score=0.94,
        skills_required=["Mobile Design", "UI/UX", "Banking Apps"],
        deadline=None,
        posted_date=None,
        competition_level="high"
    )
    
    # Generate proposal
    proposal = await service.generate_proposal(creator_id=1, opportunity=opportunity)
    
    print("Generated Proposal:")
    print("-" * 30)
    print(proposal)


async def demo_market_trends():
    """Demonstrate market trend analysis"""
    print("\n📊 MARKET TRENDS DEMO")
    print("=" * 50)
    
    db = create_demo_db()
    service = CreatorBusinessIntelligence(db)
    
    # Analyze market trends
    skills = ["UI Design", "Mobile Design", "UX Design"]
    trends = await service.track_market_trends(skills)
    
    print("SKILL DEMAND ANALYSIS:")
    for skill, data in trends["skill_demand"].items():
        print(f"• {skill}: {data['demand_level']} demand, {data['growth_rate']} growth")
    
    print("\nRATE TRENDS:")
    for skill, data in trends["rate_trends"].items():
        print(f"• {skill}: ${data['median_hourly']}/hr median, {data['trend']} trend")
    
    print("\nEMERGING OPPORTUNITIES:")
    for opportunity in trends["emerging_opportunities"]:
        print(f"• {opportunity['trend']} (Score: {opportunity['relevance_score']:.1f})")


async def demo_portfolio_optimization():
    """Demonstrate portfolio optimization"""
    print("\n🔧 PORTFOLIO OPTIMIZATION DEMO")
    print("=" * 50)
    
    db = create_demo_db()
    service = CreatorBusinessIntelligence(db)
    
    # Optimize portfolio
    optimization = await service.optimize_portfolio_for_conversion(creator_id=1)
    
    print("CURRENT CONVERSION METRICS:")
    metrics = optimization["current_metrics"]
    print(f"• View to Inquiry Rate: {metrics['view_to_inquiry_rate']:.1%}")
    print(f"• Inquiry to Project Rate: {metrics['inquiry_to_project_rate']:.1%}")
    print(f"• Average Project Value: ${metrics['average_project_value']:,.0f}")
    
    print("\nOPTIMIZATION OPPORTUNITIES:")
    for opp in optimization["optimization_opportunities"]:
        print(f"• {opp['project_name']}: {len(opp['improvements'])} improvements available")
    
    print("\nRECOMMENDED CHANGES:")
    for change in optimization["recommended_changes"]:
        print(f"• {change}")


async def demo_supporting_classes():
    """Demonstrate supporting classes"""
    print("\n🛠️  SUPPORTING CLASSES DEMO")
    print("=" * 50)
    
    # Portfolio Optimizer
    print("Portfolio Optimizer Features:")
    optimizer = PortfolioOptimizer()
    print(f"• Conversion factors: {len(optimizer.conversion_factors)} metrics tracked")
    
    # Market Intelligence
    print("\nMarket Intelligence Features:")
    market_intel = MarketIntelligence()
    
    # Demo rate analysis
    rates = await market_intel.get_market_rates(["UI Design", "UX Design"])
    print(f"• Market rate analysis: ${rates['hourly_median']:.0f}/hr median")
    
    competition = await market_intel.analyze_competition(["UI Design"])
    print(f"• Competition analysis: {competition['total_competitors']:,} competitors tracked")


async def main():
    """Run the complete demo"""
    print("🚀 CREATOR BUSINESS INTELLIGENCE SERVICE DEMO")
    print("=" * 60)
    print("This demo showcases the AI-powered business intelligence")
    print("system for creative professionals and freelancers.")
    
    # Run all demos
    await demo_portfolio_analysis()
    await demo_opportunity_finder()
    await demo_proposal_generation()
    await demo_market_trends()
    await demo_portfolio_optimization()
    await demo_supporting_classes()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed! The Creator Business Intelligence service")
    print("   provides comprehensive business insights for creators to:")
    print("   • Optimize their portfolio and pricing")
    print("   • Find new work opportunities")
    print("   • Generate winning proposals")
    print("   • Track market trends")
    print("   • Improve conversion rates")


if __name__ == "__main__":
    asyncio.run(main())