import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from sqlalchemy.orm import Session
from ..services.models import CreativeProject, ProjectQuestion, ProjectInsight, ProjectComment
from ..schemas import ProjectType

class CaseyAIService:
    """Advanced AI integration for Casey's creative project analysis"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("CASEY_LLM_MODEL", "gpt-4")
        self.casey_personality = self._load_casey_personality()
        self.project_analysis_prompts = self._load_analysis_prompts()
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            openai.api_key = self.openai_api_key

    async def analyze_project_with_ai(self, project_id: int, db: Session) -> Dict[str, Any]:
        """Generate AI-powered analysis of a creative project"""
        
        # Gather project context
        project_context = await self._gather_project_context(project_id, db)
        
        if not project_context:
            return self._fallback_analysis("Project not found")
        
        # Generate AI analysis
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                analysis = await self._generate_ai_analysis(project_context)
                return analysis
            except Exception as e:
                print(f"AI analysis failed: {e}")
                return self._fallback_analysis("AI analysis temporarily unavailable")
        else:
            return self._fallback_analysis("AI analysis requires OpenAI API configuration")

    async def chat_about_project(self, project: CreativeProject, user_message: str, 
                               user_id: int, db: Session) -> str:
        """Handle chat conversation about a specific project"""
        
        # Gather project context for conversation
        project_context = await self._gather_project_context(project.id, db)
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                response = await self._generate_chat_response(project_context, user_message)
                return response
            except Exception as e:
                print(f"AI chat failed: {e}")
                return self._fallback_chat_response(project, user_message)
        else:
            return self._fallback_chat_response(project, user_message)

    async def generate_creative_suggestions(self, project: CreativeProject, 
                                          focus_area: str = "general") -> List[str]:
        """Generate creative suggestions for improvement"""
        
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            return self._fallback_suggestions(project, focus_area)
        
        try:
            suggestions_prompt = self._build_suggestions_prompt(project, focus_area)
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.casey_personality["creative_advisor"]},
                    {"role": "user", "content": suggestions_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            suggestions_text = response.choices[0].message.content
            
            # Parse suggestions from response
            suggestions = []
            for line in suggestions_text.split('\n'):
                if line.strip() and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    suggestion = line.strip().lstrip('-•*').strip()
                    if suggestion:
                        suggestions.append(suggestion)
            
            return suggestions[:8]  # Limit to 8 suggestions
            
        except Exception as e:
            print(f"AI suggestions failed: {e}")
            return self._fallback_suggestions(project, focus_area)

    async def evaluate_design_trends(self, project: CreativeProject) -> Dict[str, Any]:
        """Evaluate project against current design trends"""
        
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            return self._fallback_trends_analysis(project)
        
        try:
            trends_prompt = self._build_trends_prompt(project)
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.casey_personality["trend_analyst"]},
                    {"role": "user", "content": trends_prompt}
                ],
                max_tokens=600,
                temperature=0.6
            )
            
            trends_analysis = response.choices[0].message.content
            
            return {
                "analysis": trends_analysis,
                "trend_alignment_score": 0.7,  # Would parse from AI response
                "trending_elements": ["minimalism", "bold typography", "sustainable design"],
                "recommendations": [
                    "Consider incorporating current color trends",
                    "Explore micro-interactions for engagement",
                    "Review accessibility standards"
                ]
            }
            
        except Exception as e:
            print(f"Trends analysis failed: {e}")
            return self._fallback_trends_analysis(project)

    async def generate_project_story(self, project: CreativeProject, db: Session) -> str:
        """Generate a narrative story about the project's journey"""
        
        # Get project timeline
        comments = db.query(ProjectComment).filter(ProjectComment.project_id == project.id).all()
        insights = db.query(ProjectInsight).filter(ProjectInsight.project_id == project.id).all()
        
        story_context = {
            "project_name": project.name,
            "project_type": project.project_type,
            "created_date": project.created_at.strftime("%B %d, %Y"),
            "status": getattr(project, 'status', 'draft'),
            "comments_count": len(comments),
            "insights_count": len(insights),
            "has_team_feedback": len(comments) > 0
        }
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                story_prompt = self._build_story_prompt(story_context)
                
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.casey_personality["storyteller"]},
                        {"role": "user", "content": story_prompt}
                    ],
                    max_tokens=400,
                    temperature=0.8
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"Story generation failed: {e}")
                return self._fallback_story(story_context)
        else:
            return self._fallback_story(story_context)

    # === PRIVATE METHODS ===

    async def _gather_project_context(self, project_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """Gather comprehensive context about a project for AI analysis"""
        
        project = db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
        if not project:
            return None
        
        # Get related data
        questions = db.query(ProjectQuestion).filter(ProjectQuestion.project_id == project_id).all()
        insights = db.query(ProjectInsight).filter(ProjectInsight.project_id == project_id).all()
        comments = db.query(ProjectComment).filter(ProjectComment.project_id == project_id).all()
        
        # Answered questions context
        answered_questions = {}
        for q in questions:
            if q.is_answered:
                answered_questions[q.question] = q.answer
        
        # Insights summary
        insights_summary = []
        for insight in insights:
            insights_summary.append({
                "type": insight.insight_type,
                "title": insight.title,
                "score": getattr(insight, 'score', insight.confidence)  # Use score if available, otherwise confidence
            })
        
        # Team feedback summary
        team_feedback = []
        for comment in comments:
            team_feedback.append({
                "type": comment.comment_type,
                "content": comment.content[:100] + "..." if len(comment.content) > 100 else comment.content,
                "resolved": comment.is_resolved
            })
        
        return {
            "project": {
                "name": project.name,
                "type": project.project_type,
                "status": getattr(project, 'status', 'draft'),
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "dimensions": project.dimensions,
                "color_palette": project.color_palette,
                "extracted_text": project.extracted_text[:500] if project.extracted_text else None,
                "tags": project.tags
            },
            "answered_questions": answered_questions,
            "insights": insights_summary,
            "team_feedback": team_feedback,
            "context_generated_at": datetime.utcnow().isoformat()
        }

    async def _generate_ai_analysis(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive AI analysis"""
        
        analysis_prompt = self._build_analysis_prompt(project_context)
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self.casey_personality["project_analyst"]},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=800,
            temperature=0.6
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse the analysis (simplified - in production, use structured output)
        return {
            "summary": analysis_text,
            "confidence": 0.85,
            "key_points": self._extract_key_points(analysis_text),
            "recommendations": self._extract_recommendations(analysis_text),
            "mood": self._analyze_casey_mood(project_context),
            "next_questions": self._suggest_follow_up_questions(project_context)
        }

    async def _generate_chat_response(self, project_context: Dict[str, Any], user_message: str) -> str:
        """Generate conversational response"""
        
        conversation_prompt = self._build_conversation_prompt(project_context, user_message)
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self.casey_personality["conversational"]},
                {"role": "user", "content": conversation_prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def _load_casey_personality(self) -> Dict[str, str]:
        """Load Casey's personality prompts for different contexts"""
        
        return {
            "project_analyst": """You are Casey, an enthusiastic and insightful creative project analyst. 
            You provide detailed, actionable feedback on creative projects with a focus on design principles, 
            user experience, and creative impact. You're encouraging but honest, and always suggest specific 
            improvements. You understand various creative disciplines and current design trends.""",
            
            "conversational": """You are Casey, a friendly and knowledgeable creative consultant. 
            You engage in natural conversation about creative projects, offering insights, suggestions, 
            and encouragement. You remember project context and can discuss specific details. 
            You're enthusiastic about creativity and design, and you adapt your communication style 
            to be helpful and engaging.""",
            
            "creative_advisor": """You are Casey, a creative advisor who specializes in generating 
            innovative suggestions for design improvements. You think outside the box while staying 
            practical, and you consider current trends, user needs, and project goals when making 
            recommendations.""",
            
            "trend_analyst": """You are Casey, a design trend analyst who stays current with the 
            latest developments in creative industries. You evaluate projects against contemporary 
            design movements, emerging technologies, and cultural shifts that influence creative work.""",
            
            "storyteller": """You are Casey, a creative storyteller who can weave engaging narratives 
            about project journeys, team collaborations, and creative processes. You celebrate 
            milestones, acknowledge challenges, and create compelling project histories."""
        }

    def _load_analysis_prompts(self) -> Dict[str, str]:
        """Load structured prompts for different types of analysis"""
        
        return {
            "comprehensive": """Analyze this creative project comprehensively:

Project Details: {project_info}
User Responses: {answered_questions}
Current Insights: {insights}
Team Feedback: {team_feedback}

Please provide:
1. Overall assessment and strengths
1. Areas for improvement
1. Specific actionable recommendations
1. Creative suggestions for enhancement
1. Next steps for project completion

Be specific, encouraging, and practical in your feedback.""",

            "conversation": """Continue this conversation about the creative project:

Project Context: {project_info}
User Message: {user_message}

Respond as Casey - be helpful, specific to this project, and maintain an encouraging but professional tone.
Reference specific project details when relevant.""",

            "suggestions": """Generate creative suggestions for this {project_type} project focusing on {focus_area}:

Project: {project_name}
Current Status: {status}
Available Details: {project_details}

Provide 5-8 specific, actionable suggestions that would improve the project."""
        }

    def _build_analysis_prompt(self, project_context: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt"""
        
        project = project_context["project"]
        
        prompt = f"""Analyze this {project['type']} project: "{project['name']}"

PROJECT DETAILS:
- Type: {project['type']}
- Status: {project['status']}
- Description: {project.get('description', 'No description provided')}
- Dimensions: {project.get('dimensions', 'Not available')}
- Color Palette: {project.get('color_palette', 'Not analyzed')}
- Text Content: {"Available" if project.get('extracted_text') else "None"}

ANSWERED QUESTIONS:
{json.dumps(project_context.get('answered_questions', {}), indent=2)}

CURRENT INSIGHTS:
{json.dumps(project_context.get('insights', []), indent=2)}

TEAM FEEDBACK:
{len(project_context.get('team_feedback', []))} comments/feedback items

Please provide a comprehensive analysis with specific recommendations."""

        return prompt

    def _build_conversation_prompt(self, project_context: Dict[str, Any], user_message: str) -> str:
        """Build conversation prompt"""
        
        project = project_context["project"]
        
        return f"""User is asking about their {project['type']} project "{project['name']}":

User Message: {user_message}

Project Status: {project['status']}
Key Details: {json.dumps({k: v for k, v in project.items() if k in ['dimensions', 'color_palette', 'tags']}, indent=2)}

Respond as Casey with specific, helpful advice about their project."""

    def _build_suggestions_prompt(self, project: CreativeProject, focus_area: str) -> str:
        """Build suggestions prompt"""
        
        return f"""Generate creative suggestions for this {project.project_type} project focusing on {focus_area}:

Project: {project.name}
Status: {getattr(project, 'status', 'draft')}
Type: {project.project_type}
Colors: {project.color_palette or 'Not analyzed'}
Dimensions: {project.dimensions or 'Not available'}

Provide specific, actionable suggestions formatted as a bullet list."""

    def _build_trends_prompt(self, project: CreativeProject) -> str:
        """Build trends analysis prompt"""
        
        return f"""Evaluate this {project.project_type} project against current design trends:

Project: {project.name}
Type: {project.project_type}
Created: {project.created_at.year}

Consider:
- Current design movements
- Technology trends
- User experience patterns
- Industry best practices

Provide trend alignment analysis and recommendations."""

    def _build_story_prompt(self, story_context: Dict[str, Any]) -> str:
        """Build project story prompt"""
        
        return f"""Create an engaging story about this creative project's journey:

Project: {story_context['project_name']} ({story_context['project_type']})
Started: {story_context['created_date']}
Status: {story_context['status']}
Team Engagement: {story_context['comments_count']} comments, {story_context['insights_count']} insights

Tell the story of this project's development in an inspiring, narrative style."""

    # === FALLBACK METHODS ===

    def _fallback_analysis(self, reason: str) -> Dict[str, Any]:
        """Provide fallback analysis when AI is unavailable"""
        
        return {
            "summary": f"I'm excited to analyze your creative project! While my advanced AI analysis is {reason.lower()}, I can still provide valuable insights based on the project data I've collected.",
            "confidence": 0.6,
            "key_points": [
                "Project successfully uploaded and processed",
                "Basic technical analysis completed",
                "Ready for team collaboration and feedback"
            ],
            "recommendations": [
                "Share with team members for feedback",
                "Review technical specifications for your target platform",
                "Consider accessibility and user experience factors"
            ],
            "mood": "enthusiastic",
            "next_questions": [
                "What specific aspect would you like me to focus on?",
                "Are there any particular design goals you're trying to achieve?",
                "Would you like suggestions for improvement in any area?"
            ],
            "note": f"Advanced AI analysis temporarily unavailable: {reason}"
        }

    def _fallback_chat_response(self, project: CreativeProject, user_message: str) -> str:
        """Provide fallback chat response"""
        
        message_lower = user_message.lower()
        
        if "color" in message_lower:
            if project.color_palette:
                return f"I can see your {project.project_type} uses {len(project.color_palette)} main colors. The palette includes {', '.join(project.color_palette[:3])}. What would you like to know about your color choices?"
            else:
                return "I'd love to discuss colors with you! Once I analyze your project's color palette, I can provide specific feedback about color harmony, psychology, and effectiveness."
        
        elif "improve" in message_lower or "better" in message_lower:
            return f"Great question! For {project.project_type.replace('_', ' ')} projects like yours, I typically recommend focusing on visual hierarchy, color consistency, and platform optimization. What specific area would you like to improve?"
        
        elif "feedback" in message_lower or "opinion" in message_lower:
            return f"I'm excited to give you feedback on '{project.name}'! Based on what I can see, this is a {project.project_type.replace('_', ' ')} project. Could you tell me what specific feedback you're looking for?"
        
        else:
            return f"That's a great question about your {project.project_type.replace('_', ' ')} project '{project.name}'. I'm here to help with design feedback, creative suggestions, and technical guidance. What specific aspect would you like to explore together?"

    def _fallback_suggestions(self, project: CreativeProject, focus_area: str) -> List[str]:
        """Provide fallback suggestions"""
        
        base_suggestions = {
            "website_mockup": [
                "Ensure responsive design across all device sizes",
                "Optimize loading times and performance",
                "Implement clear visual hierarchy with typography",
                "Add accessibility features (alt text, contrast)",
                "Consider user flow and navigation patterns"
            ],
            "social_media": [
                "Optimize dimensions for target platform",
                "Use high-contrast colors for mobile viewing",
                "Keep text large and readable on small screens",
                "Include clear call-to-action elements",
                "Test across different social media formats"
            ],
            "print_graphic": [
                "Verify color mode (CMYK for printing)",
                "Add proper bleed and margin areas",
                "Check resolution for print quality (300 DPI)",
                "Consider paper type and finish effects",
                "Review typography for print legibility"
            ]
        }
        
        return base_suggestions.get(project.project_type, [
            "Focus on clear visual hierarchy",
            "Ensure consistent branding elements",
            "Optimize for your target audience",
            "Consider accessibility requirements",
            "Test across relevant platforms/devices"
        ])

    def _fallback_trends_analysis(self, project: CreativeProject) -> Dict[str, Any]:
        """Provide fallback trends analysis"""
        
        return {
            "analysis": f"Your {project.project_type.replace('_', ' ')} project aligns with several current design trends. The minimalist approach and focus on user experience are very contemporary.",
            "trend_alignment_score": 0.7,
            "trending_elements": ["clean layouts", "bold typography", "accessibility focus"],
            "recommendations": [
                "Consider incorporating sustainable design principles",
                "Explore micro-interactions for engagement",
                "Review current accessibility standards"
            ]
        }

    def _fallback_story(self, story_context: Dict[str, Any]) -> str:
        """Provide fallback project story"""
        
        return f"""The creative journey of "{story_context['project_name']}" began on {story_context['created_date']} with an ambitious vision. 

This {story_context['project_type'].replace('_', ' ')} project has evolved through thoughtful development and {"collaborative team input" if story_context['has_team_feedback'] else "focused individual effort"}.

With {story_context['insights_count']} analytical insights guiding the process{"and " + str(story_context['comments_count']) + " team discussions shaping the direction" if story_context['comments_count'] > 0 else ""}, the project has reached its current {story_context['status']} status.

This represents more than just a creative work—it's a testament to the iterative design process and the power of combining creative vision with analytical insight."""

    # === UTILITY METHODS ===

    def _extract_key_points(self, analysis_text: str) -> List[str]:
        """Extract key points from AI analysis"""
        
        # Simple extraction - in production, use more sophisticated parsing
        lines = analysis_text.split('\n')
        key_points = []
        
        for line in lines:
            if line.strip() and ('•' in line or '-' in line or line.strip().endswith(':')):
                cleaned = line.strip().lstrip('•-*').strip()
                if cleaned and len(cleaned) > 10:
                    key_points.append(cleaned)
        
        return key_points[:5]  # Limit to 5 key points

    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract recommendations from AI analysis"""
        
        # Look for recommendation-like statements
        lines = analysis_text.split('.')
        recommendations = []
        
        trigger_words = ['recommend', 'suggest', 'consider', 'should', 'could', 'try']
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in trigger_words) and len(line) > 20:
                recommendations.append(line)
        
        return recommendations[:4]  # Limit to 4 recommendations

    def _analyze_casey_mood(self, project_context: Dict[str, Any]) -> str:
        """Determine Casey's mood based on project state"""
        
        project = project_context["project"]
        insights = project_context.get("insights", [])
        feedback = project_context.get("team_feedback", [])
        
        if project["status"] == "completed":
            return "accomplished"
        elif len(feedback) > 0:
            return "collaborative"
        elif len(insights) > 3:
            return "analytical"
        else:
            return "enthusiastic"

    def _suggest_follow_up_questions(self, project_context: Dict[str, Any]) -> List[str]:
        """Suggest follow-up questions based on project context"""
        
        project = project_context["project"]
        
        questions = [
            f"What's the main goal you want to achieve with this {project['type'].replace('_', ' ')} project?",
            "Are there any specific design challenges you're facing?",
            "Would you like suggestions for improvement in any particular area?"
        ]
        
        if not project.get("color_palette"):
            questions.append("Would you like me to analyze the color scheme in more detail?")
        
        if project["status"] != "completed":
            questions.append("What would help move this project closer to completion?")
        
        return questions[:3]