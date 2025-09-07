import json
from typing import List, Dict, Any, Optional, Tuple
from ..schemas import ProjectQuestionCreate, CaseyQuestionResponse
from .models import CreativeProject, ProjectQuestion, ProjectType, QuestionType


class CaseyProjectQuestioner:
    """Casey's intelligent system for asking relevant questions about creative projects"""

    def __init__(self):
        self.question_templates = self._initialize_question_templates()
        self.follow_up_logic = self._initialize_follow_up_logic()

    def generate_initial_questions(self, project: CreativeProject) -> List[ProjectQuestionCreate]:
        """Generate the first set of questions based on project type and uploaded file"""
        questions = []
        base_questions = self._get_base_questions_for_type(project.project_type)
        
        # Add context-aware questions based on file analysis
        if project.extracted_text:
            questions.extend(self._generate_text_based_questions(project))
        
        if project.dimensions:
            questions.extend(self._generate_dimension_based_questions(project))
            
        if project.color_palette:
            questions.extend(self._generate_color_based_questions(project))
        
        # Combine and prioritize
        all_questions = base_questions + questions
        return self._prioritize_questions(all_questions, project)

    def generate_follow_up_questions(self, project: CreativeProject, 
                                   answered_question: ProjectQuestion) -> List[ProjectQuestionCreate]:
        """Generate follow-up questions based on the user's answer"""
        follow_ups = []
        
        # Check if this answer triggers follow-up questions
        if answered_question.question_type == QuestionType.choice:
            follow_ups = self._get_choice_follow_ups(answered_question, project)
        elif answered_question.question_type == QuestionType.text:
            follow_ups = self._get_text_follow_ups(answered_question, project)
        
        return self._prioritize_questions(follow_ups, project)

    def get_next_question_for_casey(self, project: CreativeProject) -> Optional[CaseyQuestionResponse]:
        """Get the next question Casey should ask the user"""
        unanswered_questions = [q for q in project.questions if not q.is_answered]
        
        if not unanswered_questions:
            # Generate new questions if needed
            new_questions = self._generate_contextual_questions(project)
            if new_questions:
                return self._format_casey_response(new_questions[0], project)
            return None
        
        # Get highest priority unanswered question
        next_question = min(unanswered_questions, key=lambda q: q.priority)
        return self._format_casey_response(next_question, project)

    def _initialize_question_templates(self) -> Dict[ProjectType, List[Dict]]:
        """Initialize question templates for each project type"""
        return {
            ProjectType.website_mockup: [
                {
                    "question": "What type of website is this mockup for?",
                    "type": QuestionType.choice,
                    "options": ["Landing Page", "E-commerce", "Portfolio", "Corporate", "Blog", "SaaS", "Other"],
                    "priority": 1,
                    "context": "Understanding the website type helps me provide better design feedback"
                },
                {
                    "question": "What's the primary goal for visitors on this page?",
                    "type": QuestionType.text,
                    "priority": 1,
                    "context": "Knowing the conversion goal helps evaluate the design's effectiveness"
                },
                {
                    "question": "What device is this primarily designed for?",
                    "type": QuestionType.choice,
                    "options": ["Desktop", "Mobile", "Tablet", "Responsive (All devices)"],
                    "priority": 2,
                    "context": "Device targeting affects layout and interaction design choices"
                }
            ],
            ProjectType.social_media: [
                {
                    "question": "Which platform is this designed for?",
                    "type": QuestionType.choice,
                    "options": ["Instagram", "Facebook", "Twitter", "LinkedIn", "TikTok", "YouTube", "Pinterest", "Other"],
                    "priority": 1,
                    "context": "Each platform has different requirements and best practices"
                },
                {
                    "question": "What type of social media content is this?",
                    "type": QuestionType.choice,
                    "options": ["Feed Post", "Story", "Ad", "Cover Photo", "Profile Picture", "Carousel", "Video Thumbnail"],
                    "priority": 1,
                    "context": "Content type determines optimal dimensions and design approach"
                },
                {
                    "question": "What's the main message or call-to-action?",
                    "type": QuestionType.text,
                    "priority": 2,
                    "context": "Understanding the message helps evaluate clarity and visual hierarchy"
                }
            ],
            ProjectType.print_graphic: [
                {
                    "question": "What type of print material is this?",
                    "type": QuestionType.choice,
                    "options": ["Flyer", "Brochure", "Poster", "Business Card", "Banner", "Magazine Ad", "Book Cover", "Other"],
                    "priority": 1,
                    "context": "Print type affects design requirements and technical specifications"
                },
                {
                    "question": "What's the intended print size?",
                    "type": QuestionType.choice,
                    "options": ["A4 (8.3×11.7\")", "Letter (8.5×11\")", "Tabloid (11×17\")", "Business Card", "Custom Size"],
                    "priority": 1,
                    "context": "Print size affects readability, layout, and production requirements"
                },
                {
                    "question": "Is this going to a professional printer?",
                    "type": QuestionType.boolean,
                    "priority": 2,
                    "context": "Professional printing requires specific technical considerations like bleed and color profiles"
                }
            ],
            ProjectType.video: [
                {
                    "question": "What type of video content is this?",
                    "type": QuestionType.choice,
                    "options": ["Commercial/Ad", "Explainer", "Social Media", "Presentation", "Music Video", "Documentary", "Other"],
                    "priority": 1,
                    "context": "Video type determines pacing, style, and technical requirements"
                },
                {
                    "question": "What's the target duration for this video?",
                    "type": QuestionType.choice,
                    "options": ["Under 30 seconds", "30-60 seconds", "1-3 minutes", "3-10 minutes", "10+ minutes"],
                    "priority": 1,
                    "context": "Duration affects pacing and how much information can be effectively conveyed"
                },
                {
                    "question": "Where will this video be primarily shown?",
                    "type": QuestionType.choice,
                    "options": ["Social Media", "Website", "Presentation", "TV/Broadcast", "Cinema", "Internal Use"],
                    "priority": 2,
                    "context": "Distribution platform affects format, resolution, and design choices"
                }
            ],
            ProjectType.logo_design: [
                {
                    "question": "What type of business or organization is this logo for?",
                    "type": QuestionType.text,
                    "priority": 1,
                    "context": "Business type affects design approach and visual style appropriateness"
                },
                {
                    "question": "What style are you aiming for?",
                    "type": QuestionType.choice,
                    "options": ["Modern/Minimalist", "Classic/Traditional", "Creative/Artistic", "Corporate/Professional", "Playful/Fun", "Luxurious/Premium"],
                    "priority": 1,
                    "context": "Logo style should align with brand personality and target audience"
                },
                {
                    "question": "Do you have any color preferences or restrictions?",
                    "type": QuestionType.text,
                    "priority": 2,
                    "context": "Color choices affect brand perception and practical applications"
                }
            ],
            ProjectType.ui_design: [
                {
                    "question": "What type of application or interface is this?",
                    "type": QuestionType.choice,
                    "options": ["Mobile App", "Web App", "Desktop Software", "Dashboard", "E-commerce", "SaaS Platform", "Other"],
                    "priority": 1,
                    "context": "Interface type determines design patterns and user expectations"
                },
                {
                    "question": "Who are the primary users?",
                    "type": QuestionType.choice,
                    "options": ["General Public", "Business Professionals", "Developers", "Designers", "Students", "Elderly", "Children"],
                    "priority": 1,
                    "context": "User demographics affect usability requirements and design choices"
                },
                {
                    "question": "What's the main task users need to accomplish?",
                    "type": QuestionType.text,
                    "priority": 2,
                    "context": "Primary task affects information hierarchy and interaction design"
                }
            ],
            ProjectType.branding: [
                {
                    "question": "What type of branding element is this?",
                    "type": QuestionType.choice,
                    "options": ["Logo", "Brand Guidelines", "Business Card", "Letterhead", "Brand Kit", "Style Guide", "Other"],
                    "priority": 1,
                    "context": "Brand element type determines evaluation criteria and best practices"
                },
                {
                    "question": "What industry or sector is this brand for?",
                    "type": QuestionType.text,
                    "priority": 1,
                    "context": "Industry context helps evaluate appropriateness and market fit"
                },
                {
                    "question": "What's the brand personality you're aiming for?",
                    "type": QuestionType.choice,
                    "options": ["Professional", "Creative", "Friendly", "Luxurious", "Playful", "Trustworthy", "Innovative", "Traditional"],
                    "priority": 2,
                    "context": "Brand personality guides design choices and visual language"
                }
            ]
        }

    def _initialize_follow_up_logic(self) -> Dict[str, Dict]:
        """Initialize follow-up question logic"""
        return {
            "website_type": {
                "E-commerce": [
                    {
                        "question": "What products or services are being sold?",
                        "type": QuestionType.text,
                        "priority": 1,
                        "context": "Product type affects layout and feature requirements"
                    }
                ],
                "SaaS": [
                    {
                        "question": "What's the main feature or benefit being highlighted?",
                        "type": QuestionType.text,
                        "priority": 1,
                        "context": "Feature focus helps evaluate message clarity and positioning"
                    }
                ]
            },
            "social_platform": {
                "Instagram": [
                    {
                        "question": "Is this for the main feed or Instagram Stories?",
                        "type": QuestionType.choice,
                        "options": ["Main Feed", "Stories", "Reels", "IGTV"],
                        "priority": 1,
                        "context": "Instagram format affects optimal dimensions and design approach"
                    }
                ]
            }
        }

    def _get_base_questions_for_type(self, project_type: ProjectType) -> List[Dict]:
        """Get base questions for a project type"""
        return self.question_templates.get(project_type, [])

    def _generate_text_based_questions(self, project: CreativeProject) -> List[Dict]:
        """Generate questions based on extracted text content"""
        questions = []
        
        if project.extracted_text and len(project.extracted_text) > 100:
            questions.append({
                "question": "I found quite a bit of text in your design. Is readability a primary concern?",
                "type": QuestionType.boolean,
                "priority": 2,
                "context": "Text-heavy designs need careful typography and hierarchy consideration"
            })
        
        return questions

    def _generate_dimension_based_questions(self, project: CreativeProject) -> List[Dict]:
        """Generate questions based on file dimensions"""
        questions = []
        dimensions = project.dimensions
        
        if dimensions:
            aspect_ratio = dimensions.get("width", 1) / dimensions.get("height", 1)
            
            if project.project_type == ProjectType.social_media:
                if 0.9 <= aspect_ratio <= 1.1:  # Square
                    questions.append({
                        "question": "This looks like a square format - is it for Instagram feed posts?",
                        "type": QuestionType.boolean,
                        "priority": 2,
                        "context": "Square format is optimal for Instagram feed posts"
                    })
                elif aspect_ratio > 1.5:  # Landscape
                    questions.append({
                        "question": "This landscape format works well for Facebook - is that the target platform?",
                        "type": QuestionType.boolean,
                        "priority": 2,
                        "context": "Landscape format is common for Facebook and LinkedIn posts"
                    })
        
        return questions

    def _generate_color_based_questions(self, project: CreativeProject) -> List[Dict]:
        """Generate questions based on color palette"""
        questions = []
        
        if project.color_palette and len(project.color_palette) > 5:
            questions.append({
                "question": "I notice you're using many colors. Is this intentional for the brand, or should we focus on a more limited palette?",
                "type": QuestionType.choice,
                "options": ["Intentional - brand uses many colors", "Prefer limited palette", "Not sure"],
                "priority": 3,
                "context": "Too many colors can dilute brand impact and reduce visual cohesion"
            })
        
        return questions

    def _prioritize_questions(self, questions: List[Dict], project: CreativeProject) -> List[ProjectQuestionCreate]:
        """Convert question dicts to ProjectQuestionCreate objects and prioritize"""
        question_objects = []
        
        for q in questions:
            question_objects.append(ProjectQuestionCreate(
                project_id=project.id,
                question=q["question"],
                question_type=q["type"],
                options=q.get("options"),
                priority=q.get("priority", 2)
            ))
        
        # Sort by priority (1 = highest)
        question_objects.sort(key=lambda q: q.priority)
        return question_objects

    def _format_casey_response(self, question: ProjectQuestion, project: CreativeProject) -> CaseyQuestionResponse:
        """Format a question for Casey's response"""
        # Generate context based on project analysis
        context = self._generate_question_context(question, project)
        
        return CaseyQuestionResponse(
            question_id=question.id,
            question=question.question,
            question_type=question.question_type,
            options=question.options,
            context=context,
            priority=question.priority,
            follow_up_questions=self._predict_follow_ups(question, project)
        )

    def _generate_question_context(self, question: ProjectQuestion, project: CreativeProject) -> str:
        """Generate contextual explanation for why Casey is asking this question"""
        base_contexts = {
            "What type of website is this mockup for?": 
                "Understanding the website type helps me provide better design feedback and suggestions that align with your industry standards.",
            "Which platform is this designed for?": 
                "Each social media platform has different requirements, optimal dimensions, and user behaviors that affect design success.",
            "What type of print material is this?": 
                "Different print materials have unique requirements for typography, layout, and technical specifications."
        }
        
        return base_contexts.get(question.question, 
            f"This information helps me provide more targeted feedback for your {project.project_type.value} project.")

    def _predict_follow_ups(self, question: ProjectQuestion, project: CreativeProject) -> Optional[List[str]]:
        """Predict what follow-up questions might come based on the answer"""
        if "website" in question.question.lower():
            return ["What's the target audience for this website?", "Do you have brand guidelines to follow?"]
        elif "platform" in question.question.lower():
            return ["What's the main goal of this post?", "Do you have specific brand colors to use?"]
        return None

    def _generate_contextual_questions(self, project: CreativeProject) -> List[ProjectQuestionCreate]:
        """Generate additional questions based on current project state"""
        questions = []
        answered_count = len([q for q in project.questions if q.is_answered])
        
        # After getting basic info, ask more specific questions
        if answered_count >= 2 and project.project_type == ProjectType.website_mockup:
            questions.append({
                "question": "Are there any specific accessibility requirements I should consider?",
                "type": QuestionType.boolean,
                "priority": 3,
                "context": "Accessibility is crucial for inclusive design and legal compliance"
            })
        
        return self._prioritize_questions(questions, project)

    def _get_choice_follow_ups(self, answered_question: ProjectQuestion, project: CreativeProject) -> List[Dict]:
        """Get follow-up questions based on choice answers"""
        follow_ups = []
        answer = answered_question.answer
        
        # Implementation would check the follow_up_logic dictionary
        # and generate appropriate questions based on the answer
        
        return follow_ups

    def _get_text_follow_ups(self, answered_question: ProjectQuestion, project: CreativeProject) -> List[Dict]:
        """Get follow-up questions based on text answers"""
        follow_ups = []
        
        # Analyze text answer and generate relevant follow-ups
        # This could use NLP to understand the context better
        
        return follow_ups
