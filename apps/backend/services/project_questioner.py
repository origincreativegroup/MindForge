"""Casey Project Questioner service for creative projects."""

from typing import List, Optional
from ..schemas import ProjectQuestionCreate, CaseyQuestionResponse
from .models import CreativeProject, ProjectQuestion


class CaseyProjectQuestioner:
    """Service for generating and managing project questions from Casey."""
    
    def __init__(self):
        self.question_templates = {
            "website_mockup": [
                {"question": "What's the primary goal of this website?", "question_type": "goal"},
                {"question": "Who is your target audience?", "question_type": "audience"},
                {"question": "What actions do you want users to take?", "question_type": "actions"},
                {"question": "Do you have any brand guidelines I should follow?", "question_type": "branding"},
            ],
            "social_media": [
                {"question": "Which social media platform is this for?", "question_type": "platform"},
                {"question": "What's the key message you want to convey?", "question_type": "message"},
                {"question": "What tone should this have (professional, fun, serious)?", "question_type": "tone"},
                {"question": "Is this part of a larger campaign?", "question_type": "campaign"},
            ],
            "print_graphic": [
                {"question": "What's the intended print size and format?", "question_type": "format"},
                {"question": "What's the primary purpose of this piece?", "question_type": "purpose"},
                {"question": "Are there any specific color requirements?", "question_type": "colors"},
                {"question": "Do you have printing specifications or constraints?", "question_type": "printing"},
            ],
            "logo_design": [
                {"question": "What does your company/brand represent?", "question_type": "brand_identity"},
                {"question": "Do you have any color preferences or restrictions?", "question_type": "colors"},
                {"question": "Where will this logo be used primarily?", "question_type": "usage"},
                {"question": "Are there any symbols or elements that must be included?", "question_type": "elements"},
            ],
            "ui_design": [
                {"question": "What device/platform is this interface for?", "question_type": "platform"},
                {"question": "What's the main user flow or task?", "question_type": "user_flow"},
                {"question": "Do you have existing design systems to follow?", "question_type": "design_system"},
                {"question": "What accessibility requirements should I consider?", "question_type": "accessibility"},
            ],
            "branding": [
                {"question": "What values and personality should the brand convey?", "question_type": "brand_values"},
                {"question": "Who are your main competitors?", "question_type": "competition"},
                {"question": "What makes your brand unique?", "question_type": "differentiation"},
                {"question": "What's your target market demographic?", "question_type": "demographics"},
            ]
        }
    
    def generate_initial_questions(self, project: CreativeProject) -> List[ProjectQuestionCreate]:
        """Generate initial questions based on project type."""
        project_type = project.project_type.value if hasattr(project.project_type, 'value') else str(project.project_type)
        templates = self.question_templates.get(project_type, self.question_templates["website_mockup"])
        
        questions = []
        for template in templates[:3]:  # Start with 3 questions
            question = ProjectQuestionCreate(
                project_id=project.id,
                question=template["question"],
                question_type=template["question_type"]
            )
            questions.append(question)
        
        return questions
    
    def generate_follow_up_questions(self, project: CreativeProject, answered_question: ProjectQuestion) -> List[ProjectQuestionCreate]:
        """Generate follow-up questions based on answered question."""
        follow_ups = []
        
        # Generate contextual follow-ups based on the question type
        if answered_question.question_type == "goal":
            follow_ups.append(ProjectQuestionCreate(
                project_id=project.id,
                question="How will you measure if this goal is achieved?",
                question_type="metrics"
            ))
        elif answered_question.question_type == "audience":
            follow_ups.append(ProjectQuestionCreate(
                project_id=project.id,
                question="What specific pain points does your audience have?",
                question_type="pain_points"
            ))
        elif answered_question.question_type == "branding":
            follow_ups.append(ProjectQuestionCreate(
                project_id=project.id,
                question="Are there any brands whose style you admire?",
                question_type="inspiration"
            ))
        
        return follow_ups
    
    def get_next_question_for_casey(self, project: CreativeProject) -> Optional[CaseyQuestionResponse]:
        """Get the next unanswered question for Casey to ask."""
        # In a real implementation, this would query the database
        # For now, return a sample question
        return CaseyQuestionResponse(
            question="I'd love to learn more about your vision for this project. What specific feedback are you looking for?",
            question_type="feedback_request",
            context=f"Based on your {project.project_type.value if hasattr(project.project_type, 'value') else str(project.project_type)} project"
        )