import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "apps"))
sys.path.append(str(project_root / "packages"))

from backend.services.project_questioner import CaseyProjectQuestioner
from backend.services.models import CreativeProject, ProjectQuestion, ProjectType, QuestionType
from backend.schemas import ProjectQuestionCreate


def test_casey_project_questioner_initialization():
    """Test that CaseyProjectQuestioner initializes correctly"""
    questioner = CaseyProjectQuestioner()
    assert questioner.question_templates is not None
    assert questioner.follow_up_logic is not None
    assert len(questioner.question_templates) == 7  # 7 project types (added logo_design and ui_design from master)


def test_get_base_questions_for_website_mockup():
    """Test that base questions are returned for website mockup projects"""
    questioner = CaseyProjectQuestioner()
    base_questions = questioner._get_base_questions_for_type(ProjectType.website_mockup)
    
    assert len(base_questions) == 3
    assert any("website" in q["question"].lower() for q in base_questions)
    assert any("goal" in q["question"].lower() for q in base_questions)
    assert any("device" in q["question"].lower() for q in base_questions)


def test_get_base_questions_for_social_media():
    """Test that base questions are returned for social media projects"""
    questioner = CaseyProjectQuestioner()
    base_questions = questioner._get_base_questions_for_type(ProjectType.social_media)
    
    assert len(base_questions) == 3
    assert any("platform" in q["question"].lower() for q in base_questions)
    assert any("content" in q["question"].lower() for q in base_questions)
    assert any("message" in q["question"].lower() for q in base_questions)


def test_generate_text_based_questions():
    """Test generation of questions based on extracted text"""
    questioner = CaseyProjectQuestioner()
    
    # Create a mock project with text
    project = type('MockProject', (), {
        'id': 1,
        'extracted_text': 'This is a very long text that should trigger a readability question because it has more than 100 characters and therefore should be considered text-heavy content.',
        'dimensions': None,
        'color_palette': None
    })()
    
    text_questions = questioner._generate_text_based_questions(project)
    assert len(text_questions) == 1
    assert "readability" in text_questions[0]["question"].lower()
    assert text_questions[0]["type"] == QuestionType.boolean


def test_generate_dimension_based_questions_square():
    """Test generation of questions based on square dimensions"""
    questioner = CaseyProjectQuestioner()
    
    # Create a mock project with square dimensions
    project = type('MockProject', (), {
        'id': 1,
        'project_type': ProjectType.social_media,
        'extracted_text': None,
        'dimensions': {'width': 1080, 'height': 1080},
        'color_palette': None
    })()
    
    dimension_questions = questioner._generate_dimension_based_questions(project)
    assert len(dimension_questions) == 1
    assert "square" in dimension_questions[0]["question"].lower()
    assert "instagram" in dimension_questions[0]["question"].lower()


def test_generate_dimension_based_questions_landscape():
    """Test generation of questions based on landscape dimensions"""
    questioner = CaseyProjectQuestioner()
    
    # Create a mock project with landscape dimensions
    project = type('MockProject', (), {
        'id': 1,
        'project_type': ProjectType.social_media,
        'extracted_text': None,
        'dimensions': {'width': 1200, 'height': 630},
        'color_palette': None
    })()
    
    dimension_questions = questioner._generate_dimension_based_questions(project)
    assert len(dimension_questions) == 1
    assert "landscape" in dimension_questions[0]["question"].lower()
    assert "facebook" in dimension_questions[0]["question"].lower()


def test_generate_color_based_questions():
    """Test generation of questions based on color palette"""
    questioner = CaseyProjectQuestioner()
    
    # Create a mock project with many colors
    project = type('MockProject', (), {
        'id': 1,
        'extracted_text': None,
        'dimensions': None,
        'color_palette': ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500']
    })()
    
    color_questions = questioner._generate_color_based_questions(project)
    assert len(color_questions) == 1
    assert "colors" in color_questions[0]["question"].lower()
    assert color_questions[0]["type"] == QuestionType.choice


def test_prioritize_questions():
    """Test that questions are prioritized correctly"""
    questioner = CaseyProjectQuestioner()
    
    # Create a mock project
    project = type('MockProject', (), {'id': 1})()
    
    # Create test questions with different priorities
    test_questions = [
        {"question": "Low priority", "type": QuestionType.text, "priority": 3},
        {"question": "High priority", "type": QuestionType.text, "priority": 1},
        {"question": "Medium priority", "type": QuestionType.text, "priority": 2}
    ]
    
    prioritized = questioner._prioritize_questions(test_questions, project)
    
    assert len(prioritized) == 3
    assert prioritized[0].priority == 1
    assert prioritized[1].priority == 2
    assert prioritized[2].priority == 3
    assert "High priority" in prioritized[0].question


def test_generate_question_context():
    """Test generation of question context"""
    questioner = CaseyProjectQuestioner()
    
    # Create mock objects
    project = type('MockProject', (), {
        'project_type': ProjectType.website_mockup
    })()
    
    question = type('MockQuestion', (), {
        'question': "What type of website is this mockup for?"
    })()
    
    context = questioner._generate_question_context(question, project)
    assert "Understanding the website type" in context
    assert "design feedback" in context


def test_predict_follow_ups():
    """Test prediction of follow-up questions"""
    questioner = CaseyProjectQuestioner()
    
    # Create mock objects
    project = type('MockProject', (), {})()
    
    # Test website-related question
    website_question = type('MockQuestion', (), {
        'question': "What type of website is this mockup for?"
    })()
    
    follow_ups = questioner._predict_follow_ups(website_question, project)
    assert follow_ups is not None
    assert len(follow_ups) == 2
    assert any("audience" in q.lower() for q in follow_ups)
    assert any("brand" in q.lower() for q in follow_ups)
    
    # Test platform-related question
    platform_question = type('MockQuestion', (), {
        'question': "Which platform is this designed for?"
    })()
    
    follow_ups = questioner._predict_follow_ups(platform_question, project)
    assert follow_ups is not None
    assert len(follow_ups) == 2
    assert any("goal" in q.lower() for q in follow_ups)
    assert any("colors" in q.lower() for q in follow_ups)


def test_all_project_types_have_templates():
    """Test that all project types have question templates"""
    questioner = CaseyProjectQuestioner()
    
    for project_type in ProjectType:
        templates = questioner._get_base_questions_for_type(project_type)
        assert len(templates) > 0, f"No templates found for {project_type}"
        
        # Verify each template has required fields
        for template in templates:
            assert "question" in template
            assert "type" in template
            assert "priority" in template
            assert "context" in template