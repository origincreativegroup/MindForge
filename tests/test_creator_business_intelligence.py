import sys
from pathlib import Path
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "apps"))

from backend.services.creator_business_intelligence import (
    CreatorBusinessIntelligence,
    OpportunityLead,
    CreatorInsight,
    PortfolioOptimizer,
    MarketIntelligence
)
from backend.services.models import Project, ProjectStatus, Skill, Client


def create_mock_db():
    """Create a mock database session with sample data"""
    db = Mock()
    
    # Create mock skills with proper name attributes
    skill1 = Mock()
    skill1.name = "UI Design"
    skill2 = Mock()
    skill2.name = "Mobile Design"
    skill3 = Mock()
    skill3.name = "Web Design"
    skill4 = Mock()
    skill4.name = "Data Visualization"
    
    # Create mock projects
    project1 = Mock(spec=Project)
    project1.id = 1
    project1.title = "Mobile App Design"
    project1.client_id = 1
    project1.status = ProjectStatus.shipped
    project1.disciplines = ["Mobile Design", "UI/UX"]
    project1.skills = [skill1, skill2]
    project1.assets = [Mock(), Mock()]  # Mock assets
    project1.case_study = Mock()
    
    project2 = Mock(spec=Project)
    project2.id = 2
    project2.title = "Web Dashboard"
    project2.client_id = 1
    project2.status = ProjectStatus.in_progress
    project2.disciplines = ["Web Design", "Dashboard"]
    project2.skills = [skill3, skill4]
    project2.assets = [Mock()]
    project2.case_study = None
    
    # Configure query mock
    query_mock = Mock()
    query_mock.filter.return_value.all.return_value = [project1, project2]
    db.query.return_value = query_mock
    
    return db


def test_creator_business_intelligence_init():
    """Test CreatorBusinessIntelligence initialization"""
    db = create_mock_db()
    
    # Test with no OpenAI client
    with patch('openai.api_key', None):
        service = CreatorBusinessIntelligence(db)
        assert service.db == db
        assert service.openai_client is None


def test_opportunity_lead_creation():
    """Test OpportunityLead dataclass creation"""
    lead = OpportunityLead(
        title="Test Project",
        company="Test Company",
        source="upwork",
        url="https://test.com",
        description="Test description",
        estimated_budget=5000.0,
        match_score=0.85,
        skills_required=["UI Design", "Mobile"],
        deadline=datetime.now() + timedelta(days=30),
        posted_date=datetime.now(),
        competition_level="medium"
    )
    
    assert lead.title == "Test Project"
    assert lead.match_score == 0.85
    assert "UI Design" in lead.skills_required


def test_creator_insight_creation():
    """Test CreatorInsight dataclass creation"""
    insight = CreatorInsight(
        type="rate_optimization",
        title="Increase Your Rates",
        description="Market analysis suggests you can increase rates by 20%",
        action_items=["Research competitors", "Update portfolio"],
        potential_impact="$2000 additional monthly revenue",
        priority=1
    )
    
    assert insight.type == "rate_optimization"
    assert insight.priority == 1
    assert len(insight.action_items) == 2


async def test_analyze_creator_portfolio():
    """Test portfolio analysis functionality"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    result = await service.analyze_creator_portfolio(1)
    
    assert "portfolio_gaps" in result
    assert "market_positioning" in result
    assert "rate_optimization" in result
    assert "niche_opportunities" in result
    assert "conversion_potential" in result
    assert "overall_score" in result
    assert "next_actions" in result
    
    # Test with no projects
    query_mock = Mock()
    query_mock.filter.return_value.all.return_value = []
    db.query.return_value = query_mock
    
    result = await service.analyze_creator_portfolio(999)
    assert "error" in result


async def test_find_opportunities():
    """Test opportunity finding functionality"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    opportunities = await service.find_opportunities(1, limit=10)
    
    assert isinstance(opportunities, list)
    assert len(opportunities) <= 10
    
    # Check that opportunities are sorted by match score
    if len(opportunities) > 1:
        assert opportunities[0].match_score >= opportunities[1].match_score


async def test_generate_proposal():
    """Test proposal generation"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    opportunity = OpportunityLead(
        title="Test Project",
        company="Test Company",
        source="upwork",
        url="https://test.com",
        description="Need UI designer",
        estimated_budget=5000.0,
        match_score=0.9,
        skills_required=["UI Design"],
        deadline=datetime.now() + timedelta(days=30),
        posted_date=datetime.now(),
        competition_level="medium"
    )
    
    proposal = await service.generate_proposal(1, opportunity)
    
    assert isinstance(proposal, str)
    assert len(proposal) > 0
    assert "Test Company" in proposal


async def test_optimize_portfolio_for_conversion():
    """Test portfolio conversion optimization"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    result = await service.optimize_portfolio_for_conversion(1)
    
    assert "current_metrics" in result
    assert "optimization_opportunities" in result
    assert "recommended_changes" in result
    assert "projected_impact" in result
    
    # Check metrics structure
    metrics = result["current_metrics"]
    assert "view_to_inquiry_rate" in metrics
    assert "inquiry_to_project_rate" in metrics
    assert "average_project_value" in metrics


async def test_track_market_trends():
    """Test market trend tracking"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    skills = ["UI Design", "Mobile Design"]
    result = await service.track_market_trends(skills)
    
    assert "skill_demand" in result
    assert "rate_trends" in result
    assert "emerging_opportunities" in result
    assert "competition_analysis" in result
    assert "market_forecast" in result
    
    # Check skill-specific data
    for skill in skills:
        assert skill in result["skill_demand"]
        assert skill in result["rate_trends"]


async def test_portfolio_gaps_analysis():
    """Test portfolio gap analysis"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    # Create mock projects with limited disciplines
    projects = [
        Mock(disciplines=["Mobile Design"]),
        Mock(disciplines=["Web Design"])
    ]
    
    result = await service._analyze_portfolio_gaps(projects)
    
    assert "identified_gaps" in result
    assert "portfolio_completeness" in result
    assert "priority_additions" in result
    
    gaps = result["identified_gaps"]
    assert isinstance(gaps, list)
    
    # Should identify missing high-value categories
    gap_categories = [gap["category"] for gap in gaps]
    assert "saas_dashboard" in gap_categories or "e_commerce" in gap_categories


async def test_market_positioning_calculation():
    """Test market positioning calculation"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    # Create mock skills
    skill1 = Mock()
    skill1.name = "UI Design"
    skill2 = Mock()
    skill2.name = "Mobile Design"
    skill3 = Mock()
    skill3.name = "Web Design"
    skill4 = Mock()
    skill4.name = "Branding"
    
    projects = [
        Mock(disciplines=["UI Design", "Mobile Design"], skills=[skill1, skill2]),
        Mock(disciplines=["Web Design", "Branding"], skills=[skill3, skill4])
    ]
    
    result = await service._calculate_market_positioning(projects)
    
    assert "quality_score" in result
    assert "portfolio_diversity" in result
    assert "market_percentile" in result
    assert "competitive_advantages" in result
    assert "positioning_recommendations" in result
    
    assert isinstance(result["quality_score"], (int, float))
    assert isinstance(result["portfolio_diversity"], int)
    assert 0 <= result["market_percentile"] <= 100


async def test_rate_optimization_suggestions():
    """Test rate optimization functionality"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    # Create mock skills
    skill1 = Mock()
    skill1.name = "UI Design"
    
    projects = [Mock(disciplines=["UI Design"], skills=[skill1])]
    result = await service._suggest_rate_optimization(projects)
    
    assert "current_indicators" in result
    assert "market_analysis" in result
    assert "recommendations" in result
    assert "justification_points" in result
    
    recommendations = result["recommendations"]
    assert "suggested_hourly_rate" in recommendations
    assert "suggested_project_minimum" in recommendations


async def test_niche_opportunity_identification():
    """Test niche opportunity identification"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    # Create mock skills
    skill1 = Mock()
    skill1.name = "UI Design"
    
    projects = [Mock(disciplines=["UI Design", "SaaS"], skills=[skill1])]
    result = await service._identify_niche_opportunities(projects)
    
    assert "current_specializations" in result
    assert "emerging_opportunities" in result
    assert "recommended_focus" in result
    
    opportunities = result["emerging_opportunities"]
    assert isinstance(opportunities, list)


def test_portfolio_optimizer():
    """Test PortfolioOptimizer class"""
    optimizer = PortfolioOptimizer()
    
    # Test conversion factors
    assert "case_study_completeness" in optimizer.conversion_factors
    assert "visual_quality" in optimizer.conversion_factors
    
    # Test with mock project
    project = Mock(spec=Project)
    project.case_study = Mock()
    project.assets = [Mock(), Mock()]
    
    result = asyncio.run(optimizer.analyze_project_conversion_potential(project))
    
    assert "current_score" in result
    assert "potential_score" in result
    assert "improvement_potential" in result
    assert "improvements" in result


async def test_market_intelligence():
    """Test MarketIntelligence class"""
    market_intel = MarketIntelligence()
    
    # Test market rates
    skills = ["UI Design", "UX Design"]
    rates = await market_intel.get_market_rates(skills)
    
    assert "hourly_median" in rates
    assert "hourly_75th_percentile" in rates
    assert "project_minimum" in rates
    assert "retainer_monthly" in rates
    
    # Test competition analysis
    competition = await market_intel.analyze_competition(skills)
    
    assert "total_competitors" in competition
    assert "skills_saturation" in competition
    assert "opportunity_gaps" in competition


def test_creator_profile_retrieval():
    """Test creator profile retrieval"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    profile = service._get_creator_profile(1)
    
    assert "name" in profile
    assert "skills" in profile
    assert "experience_years" in profile
    assert "hourly_rate" in profile


def test_skill_extraction():
    """Test skill extraction from projects"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    # Create proper mock skills with name attribute
    skill1 = Mock()
    skill1.name = "UI Design"
    skill2 = Mock()
    skill2.name = "Branding"
    skill3 = Mock()
    skill3.name = "Web Design"
    
    projects = [
        Mock(skills=[skill1, skill2], disciplines=["Mobile"]),
        Mock(skills=[skill3], disciplines=["E-commerce"])
    ]
    
    skills = service._extract_skills_from_projects(projects)
    
    assert isinstance(skills, list)
    assert "UI Design" in skills
    assert "Mobile" in skills


def test_niche_skill_matching():
    """Test niche skill matching logic"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    # Create proper mock skills
    ui_skill = Mock()
    ui_skill.name = "UI Design"
    brand_skill = Mock()
    brand_skill.name = "Brand Design"
    
    projects = [Mock(skills=[ui_skill], disciplines=["Web Design"])]
    
    # Test SaaS matching
    assert service._creator_skills_match_niche(projects, "SaaS Dashboard Design")
    
    # Test brand matching  
    projects_with_brand = [Mock(skills=[brand_skill], disciplines=["Branding"])]
    assert service._creator_skills_match_niche(projects_with_brand, "Sustainable Brand Design")


async def test_emerging_trends_identification():
    """Test emerging trends identification"""
    db = create_mock_db()
    service = CreatorBusinessIntelligence(db)
    
    skills = ["UI Design", "Mobile Design"]
    trends = await service._identify_emerging_trends(skills)
    
    assert isinstance(trends, list)
    for trend in trends:
        assert "trend" in trend
        assert "relevance_score" in trend
        assert "opportunity" in trend
        assert "market_size" in trend


def run_async_test(coro):
    """Helper function to run async tests"""
    return asyncio.run(coro)


def test_all():
    """Run all tests"""
    print("Testing CreatorBusinessIntelligence service...")
    
    # Sync tests
    test_creator_business_intelligence_init()
    print("✓ Initialization test passed")
    
    test_opportunity_lead_creation()
    print("✓ OpportunityLead creation test passed")
    
    test_creator_insight_creation()
    print("✓ CreatorInsight creation test passed")
    
    test_portfolio_optimizer()
    print("✓ PortfolioOptimizer test passed")
    
    test_creator_profile_retrieval()
    print("✓ Creator profile retrieval test passed")
    
    test_skill_extraction()
    print("✓ Skill extraction test passed")
    
    test_niche_skill_matching()
    print("✓ Niche skill matching test passed")
    
    # Async tests
    run_async_test(test_analyze_creator_portfolio())
    print("✓ Portfolio analysis test passed")
    
    run_async_test(test_find_opportunities())
    print("✓ Find opportunities test passed")
    
    run_async_test(test_generate_proposal())
    print("✓ Proposal generation test passed")
    
    run_async_test(test_optimize_portfolio_for_conversion())
    print("✓ Portfolio conversion optimization test passed")
    
    run_async_test(test_track_market_trends())
    print("✓ Market trends tracking test passed")
    
    run_async_test(test_portfolio_gaps_analysis())
    print("✓ Portfolio gaps analysis test passed")
    
    run_async_test(test_market_positioning_calculation())
    print("✓ Market positioning calculation test passed")
    
    run_async_test(test_rate_optimization_suggestions())
    print("✓ Rate optimization suggestions test passed")
    
    run_async_test(test_niche_opportunity_identification())
    print("✓ Niche opportunity identification test passed")
    
    run_async_test(test_market_intelligence())
    print("✓ Market intelligence test passed")
    
    run_async_test(test_emerging_trends_identification())
    print("✓ Emerging trends identification test passed")
    
    print("\nAll tests passed! ✅")


if __name__ == "__main__":
    test_all()