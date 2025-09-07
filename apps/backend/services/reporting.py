import json
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import base64
from dataclasses import dataclass

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..services.models import CreativeProject, ProjectQuestion, ProjectInsight, ProjectComment, ProjectActivity
from ..schemas import ProjectType
from .collaboration import CollaborationService
from .advanced_analyzer import AdvancedCreativeAnalyzer

@dataclass
class ReportConfig:
    """Configuration for report generation"""
    include_analytics: bool = True
    include_insights: bool = True
    include_recommendations: bool = True
    include_comments: bool = True
    include_activity: bool = True
    include_visuals: bool = True
    export_format: str = "pdf"  # pdf, html, json, csv
    template_style: str = "professional"  # professional, creative, minimal

class ProjectReportGenerator:
    """Generate comprehensive reports for creative projects"""

    def __init__(self, db: Session):
        self.db = db
        self.collaboration_service = CollaborationService(db)
        self.analyzer = AdvancedCreativeAnalyzer()

    async def generate_project_report(self, project_id: int, config: ReportConfig) -> Dict[str, Any]:
        """Generate a comprehensive project report"""
        
        # Gather project data
        project_data = await self._collect_project_data(project_id)
        
        if not project_data:
            raise ValueError(f"Project {project_id} not found")
        
        # Generate report based on format
        if config.export_format == "pdf":
            return await self._generate_pdf_report(project_data, config)
        elif config.export_format == "html":
            return await self._generate_html_report(project_data, config)
        elif config.export_format == "json":
            return await self._generate_json_report(project_data, config)
        elif config.export_format == "csv":
            return await self._generate_csv_report(project_data, config)
        else:
            raise ValueError(f"Unsupported export format: {config.export_format}")

    async def generate_team_analytics_report(self, time_range: str = "30d", 
                                           team_members: List[int] = None) -> Dict[str, Any]:
        """Generate team analytics and productivity report"""
        
        # Calculate date range
        end_date = datetime.utcnow()
        if time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_range == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Collect analytics data
        analytics_data = await self._collect_team_analytics(start_date, end_date, team_members)
        
        # Generate visualizations
        if MATPLOTLIB_AVAILABLE:
            visualizations = await self._generate_analytics_charts(analytics_data)
            analytics_data["visualizations"] = visualizations
        
        return analytics_data

    async def export_project_insights(self, project_id: int, format: str = "json") -> Union[str, bytes]:
        """Export project insights in various formats"""
        
        project = self.db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get insights
        insights = self.db.query(ProjectInsight).filter(ProjectInsight.project_id == project_id).all()
        
        insights_data = []
        for insight in insights:
            insights_data.append({
                "id": insight.id,
                "type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "score": insight.score,
                "data": insight.data,
                "created_at": insight.created_at.isoformat()
            })
        
        if format == "json":
            return json.dumps({
                "project": {
                    "id": project.id,
                    "name": project.title,  # Use title as name for compatibility
                    "type": project.project_type,
                    "created_at": project.created_at.isoformat()
                },
                "insights": insights_data,
                "export_date": datetime.utcnow().isoformat()
            }, indent=2)
        
        elif format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Insight ID", "Type", "Title", "Description", 
                "Score", "Created Date", "Data"
            ])
            
            # Write insights
            for insight_data in insights_data:
                writer.writerow([
                    insight_data["id"],
                    insight_data["type"],
                    insight_data["title"],
                    insight_data["description"],
                    insight_data["score"],
                    insight_data["created_at"],
                    json.dumps(insight_data["data"])
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def _collect_project_data(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Collect comprehensive project data for reporting"""
        
        project = self.db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
        if not project:
            return None
        
        # Get related data
        questions = self.db.query(ProjectQuestion).filter(ProjectQuestion.project_id == project_id).all()
        insights = self.db.query(ProjectInsight).filter(ProjectInsight.project_id == project_id).all()
        comments = await self.collaboration_service.get_project_comments(project_id)
        activities = await self.collaboration_service.get_project_activity(project_id)
        
        # Run comprehensive analysis if not already done
        try:
            analysis_result = await self.analyzer.comprehensive_project_audit(project)
        except Exception as e:
            print(f"Analysis failed: {e}")
            analysis_result = {"overall_score": 0.5, "insights": [], "recommendations": []}
        
        return {
            "project": project,
            "questions": questions,
            "insights": insights,
            "comments": comments,
            "activities": activities,
            "analysis": analysis_result,
            "generated_at": datetime.utcnow()
        }

    async def _generate_pdf_report(self, project_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate PDF report"""
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation")
        
        project = project_data["project"]
        analysis = project_data["analysis"]
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30
        )
        project_name = getattr(project, 'name', None) or getattr(project, 'title', 'Unknown Project')
        story.append(Paragraph(f"Creative Project Report: {project_name}", title_style))
        story.append(Spacer(1, 20))
        
        # Project Overview
        story.append(Paragraph("Project Overview", styles['Heading2']))
        overview_data = [
            ["Project Name", project_name],
            ["Type", project.project_type.replace('_', ' ').title()],
            ["Status", project.status.name.replace('_', ' ').title()],
            ["Created", project.created_at.strftime("%Y-%m-%d")],
            ["Overall Score", f"{analysis.get('overall_score', 0):.1%}"]
        ]
        
        overview_table = Table(overview_data, colWidths=[2*inch, 3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # Analysis Results
        if config.include_analytics and analysis.get('category_scores'):
            story.append(Paragraph("Analysis Results", styles['Heading2']))
            
            score_data = [["Category", "Score"]]
            for category, score in analysis['category_scores'].items():
                score_data.append([category.replace('_', ' ').title(), f"{score:.1%}"])
            
            score_table = Table(score_data, colWidths=[3*inch, 2*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(score_table)
            story.append(Spacer(1, 20))
        
        # Key Insights
        if config.include_insights and analysis.get('detailed_insights'):
            story.append(Paragraph("Key Insights", styles['Heading2']))
            
            for insight in analysis['detailed_insights'][:5]:  # Top 5 insights
                insight_title = insight.get('title', 'Insight')
                insight_desc = insight.get('description', 'No description available')
                score = insight.get('score', 0)
                
                story.append(Paragraph(f"<b>{insight_title}</b> (Score: {score:.1%})", styles['Heading3']))
                story.append(Paragraph(insight_desc, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Recommendations
        if config.include_recommendations and analysis.get('recommendations'):
            story.append(Paragraph("Recommendations", styles['Heading2']))
            
            for i, rec in enumerate(analysis['recommendations'][:10], 1):
                rec_title = rec.get('title', 'Recommendation')
                rec_desc = rec.get('description', 'No description available')
                priority = rec.get('priority', 'medium')
                
                story.append(Paragraph(f"{i}. <b>{rec_title}</b> (Priority: {priority})", styles['Heading3']))
                story.append(Paragraph(rec_desc, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Comments Summary
        if config.include_comments and project_data["comments"]:
            story.append(Paragraph("Team Feedback", styles['Heading2']))
            
            total_comments = len(project_data["comments"])
            unresolved = len([c for c in project_data["comments"] if not c['is_resolved']])
            
            story.append(Paragraph(f"Total Comments: {total_comments} (Unresolved: {unresolved})", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Recent comments
            for comment in project_data["comments"][:3]:
                author = comment['author']['name']
                content = comment['content'][:200] + "..." if len(comment['content']) > 200 else comment['content']
                
                story.append(Paragraph(f"<b>{author}:</b> {content}", styles['Normal']))
                story.append(Spacer(1, 8))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return {
            "content": base64.b64encode(pdf_data).decode(),
            "filename": f"{project_name}_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            "content_type": "application/pdf",
            "size": len(pdf_data)
        }

    async def _generate_html_report(self, project_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate HTML report"""
        
        project = project_data["project"]
        analysis = project_data["analysis"]
        project_name = getattr(project, 'name', None) or getattr(project, 'title', 'Unknown Project')
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Project Report: {project_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; }}
                .section {{ margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; }}
                .score {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; }}
                .score.high {{ background: #10b981; }}
                .score.medium {{ background: #f59e0b; }}
                .score.low {{ background: #ef4444; }}
                .insight {{ margin: 15px 0; padding: 15px; background: #f9fafb; border-left: 4px solid #3b82f6; }}
                .recommendation {{ margin: 15px 0; padding: 15px; background: #fef3c7; border-left: 4px solid #f59e0b; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f4f4f4; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Creative Project Report</h1>
                <h2>{project_name}</h2>
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <div class="section">
                <h2>Project Overview</h2>
                <table>
                    <tr><td><strong>Project Type</strong></td><td>{project.project_type.replace('_', ' ').title()}</td></tr>
                    <tr><td><strong>Status</strong></td><td>{project.status.name.replace('_', ' ').title()}</td></tr>
                    <tr><td><strong>Created</strong></td><td>{project.created_at.strftime('%Y-%m-%d')}</td></tr>
                    <tr><td><strong>Overall Score</strong></td><td><span class="score {'high' if analysis.get('overall_score', 0) > 0.7 else 'medium' if analysis.get('overall_score', 0) > 0.5 else 'low'}">{analysis.get('overall_score', 0):.1%}</span></td></tr>
                </table>
            </div>
        """
        
        # Add analysis results
        if config.include_analytics and analysis.get('category_scores'):
            html_content += """
            <div class="section">
                <h2>Analysis Results</h2>
                <table>
                    <tr><th>Category</th><th>Score</th></tr>
            """
            for category, score in analysis['category_scores'].items():
                score_class = 'high' if score > 0.7 else 'medium' if score > 0.5 else 'low'
                html_content += f"""
                    <tr>
                        <td>{category.replace('_', ' ').title()}</td>
                        <td><span class="score {score_class}">{score:.1%}</span></td>
                    </tr>
                """
            html_content += "</table></div>"
        
        # Add insights
        if config.include_insights and analysis.get('detailed_insights'):
            html_content += '<div class="section"><h2>Key Insights</h2>'
            for insight in analysis['detailed_insights'][:5]:
                html_content += f"""
                <div class="insight">
                    <h3>{insight.get('title', 'Insight')}</h3>
                    <p>{insight.get('description', 'No description available')}</p>
                    <small>Score: {insight.get('score', 0):.1%}</small>
                </div>
                """
            html_content += '</div>'
        
        # Add recommendations
        if config.include_recommendations and analysis.get('recommendations'):
            html_content += '<div class="section"><h2>Recommendations</h2>'
            for i, rec in enumerate(analysis['recommendations'][:10], 1):
                html_content += f"""
                <div class="recommendation">
                    <h3>{i}. {rec.get('title', 'Recommendation')}</h3>
                    <p>{rec.get('description', 'No description available')}</p>
                    <small>Priority: {rec.get('priority', 'medium').title()}</small>
                </div>
                """
            html_content += '</div>'
        
        html_content += """
        </body>
        </html>
        """
        
        return {
            "content": html_content,
            "filename": f"{project_name}_report_{datetime.now().strftime('%Y%m%d')}.html",
            "content_type": "text/html",
            "size": len(html_content.encode())
        }

    async def _generate_json_report(self, project_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate JSON report"""
        
        project = project_data["project"]
        project_name = getattr(project, 'name', None) or getattr(project, 'title', 'Unknown Project')
        
        # Build JSON structure
        json_data = {
            "project": {
                "id": project.id,
                "name": project_name,
                "type": project.project_type,
                "status": project.status.name,
                "description": getattr(project, 'description', ''),
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "dimensions": getattr(project, 'dimensions', {}),
                "color_palette": getattr(project, 'color_palette', []),
                "tags": getattr(project, 'tags', [])
            },
            "report_config": {
                "generated_at": datetime.now().isoformat(),
                "include_analytics": config.include_analytics,
                "include_insights": config.include_insights,
                "include_recommendations": config.include_recommendations,
                "include_comments": config.include_comments,
                "include_activity": config.include_activity
            }
        }
        
        if config.include_analytics:
            json_data["analysis"] = project_data["analysis"]
        
        if config.include_insights:
            json_data["insights"] = [
                {
                    "id": insight.id,
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "score": insight.score,
                    "data": insight.data,
                    "created_at": insight.created_at.isoformat()
                }
                for insight in project_data["insights"]
            ]
        
        if config.include_comments:
            json_data["comments"] = project_data["comments"]
        
        if config.include_activity:
            json_data["activities"] = project_data["activities"]
        
        json_content = json.dumps(json_data, indent=2, default=str)
        
        return {
            "content": json_content,
            "filename": f"{project_name}_report_{datetime.now().strftime('%Y%m%d')}.json",
            "content_type": "application/json",
            "size": len(json_content.encode())
        }

    async def _generate_csv_report(self, project_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate CSV report (insights and analytics)"""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write project overview
        writer.writerow(["=== PROJECT OVERVIEW ==="])
        writer.writerow(["Field", "Value"])
        project = project_data["project"]
        project_name = getattr(project, 'name', None) or getattr(project, 'title', 'Unknown Project')
        writer.writerow(["Name", project_name])
        writer.writerow(["Type", project.project_type])
        writer.writerow(["Status", project.status.name])
        writer.writerow(["Created", project.created_at.strftime('%Y-%m-%d')])
        writer.writerow([])
        
        # Write analysis scores
        if config.include_analytics and project_data["analysis"].get('category_scores'):
            writer.writerow(["=== ANALYSIS SCORES ==="])
            writer.writerow(["Category", "Score"])
            for category, score in project_data["analysis"]['category_scores'].items():
                writer.writerow([category.replace('_', ' ').title(), f"{score:.3f}"])
            writer.writerow([])
        
        # Write insights
        if config.include_insights and project_data["insights"]:
            writer.writerow(["=== INSIGHTS ==="])
            writer.writerow(["Type", "Title", "Description", "Score", "Created"])
            for insight in project_data["insights"]:
                writer.writerow([
                    insight.insight_type,
                    insight.title,
                    insight.description,
                    insight.score,
                    insight.created_at.strftime('%Y-%m-%d')
                ])
            writer.writerow([])
        
        # Write comments summary
        if config.include_comments and project_data["comments"]:
            writer.writerow(["=== COMMENTS ==="])
            writer.writerow(["Author", "Type", "Content", "Resolved", "Created"])
            for comment in project_data["comments"]:
                writer.writerow([
                    comment['author']['name'],
                    comment['comment_type'],
                    comment['content'][:100] + "..." if len(comment['content']) > 100 else comment['content'],
                    "Yes" if comment['is_resolved'] else "No",
                    comment['created_at']
                ])
        
        csv_content = output.getvalue()
        output.close()
        
        return {
            "content": csv_content,
            "filename": f"{project_name}_report_{datetime.now().strftime('%Y%m%d')}.csv",
            "content_type": "text/csv",
            "size": len(csv_content.encode())
        }

    async def _collect_team_analytics(self, start_date: datetime, end_date: datetime, 
                                    team_members: List[int] = None) -> Dict[str, Any]:
        """Collect team analytics data"""
        
        # Base query for projects in date range
        base_query = self.db.query(CreativeProject).filter(
            CreativeProject.created_at.between(start_date, end_date)
        )
        
        # Project statistics
        total_projects = base_query.count()
        completed_projects = base_query.filter(CreativeProject.status == 'shipped').count()
        in_progress_projects = base_query.filter(CreativeProject.status == 'in_progress').count()
        
        # Project type distribution
        type_distribution = (
            self.db.query(CreativeProject.project_type, func.count(CreativeProject.id))
            .filter(CreativeProject.created_at.between(start_date, end_date))
            .group_by(CreativeProject.project_type)
            .all()
        )
        
        # Daily completion trend
        daily_completions = []
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            completed_count = (
                self.db.query(CreativeProject)
                .filter(
                    and_(
                        CreativeProject.updated_at.between(current_date, next_date),
                        CreativeProject.status == 'shipped'
                    )
                )
                .count()
            )
            
            daily_completions.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "completed": completed_count
            })
            
            current_date = next_date
        
        return {
            "summary": {
                "total_projects": total_projects,
                "completed_projects": completed_projects,
                "in_progress_projects": in_progress_projects,
                "completion_rate": completed_projects / total_projects if total_projects > 0 else 0,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            },
            "type_distribution": [
                {"type": ptype, "count": count} for ptype, count in type_distribution
            ],
            "daily_completions": daily_completions,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def _generate_analytics_charts(self, analytics_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate analytics visualization charts"""
        
        if not MATPLOTLIB_AVAILABLE:
            return {}
        
        charts = {}
        
        # Project type distribution pie chart
        if analytics_data.get("type_distribution"):
            fig, ax = plt.subplots(figsize=(8, 6))
            
            types = [item["type"].replace('_', ' ').title() for item in analytics_data["type_distribution"]]
            counts = [item["count"] for item in analytics_data["type_distribution"]]
            
            ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
            ax.set_title('Project Type Distribution')
            
            # Save to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            charts["type_distribution"] = f"data:image/png;base64,{chart_data}"
            
            plt.close()
        
        # Daily completions line chart
        if analytics_data.get("daily_completions"):
            fig, ax = plt.subplots(figsize=(12, 6))
            
            dates = [item["date"] for item in analytics_data["daily_completions"]]
            completions = [item["completed"] for item in analytics_data["daily_completions"]]
            
            ax.plot(dates[::3], completions[::3], marker='o')  # Every 3rd point for readability
            ax.set_title('Daily Project Completions')
            ax.set_xlabel('Date')
            ax.set_ylabel('Completed Projects')
            plt.xticks(rotation=45)
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            charts["daily_completions"] = f"data:image/png;base64,{chart_data}"
            
            plt.close()
        
        return charts


# Export utilities

class ExportUtilities:
    """Utility functions for exports"""

    @staticmethod
    def create_download_response(content: Union[str, bytes], filename: str, content_type: str):
        """Create a download response for FastAPI"""
        from fastapi.responses import Response
        
        if isinstance(content, str):
            content = content.encode()
        
        return Response(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for download"""
        import re
        
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove extra spaces and truncate
        filename = '_'.join(filename.split())
        filename = filename[:100]  # Limit length
        
        return filename


# Casey integration for reports

class CaseyReportNarrator:
    """Generate Casey-style narrative reports"""

    @staticmethod
    def generate_project_summary(project_data: Dict[str, Any]) -> str:
        """Generate Casey's narrative summary of the project"""
        
        project = project_data["project"]
        analysis = project_data["analysis"]
        project_name = getattr(project, 'name', None) or getattr(project, 'title', 'Unknown Project')
        
        summary = [
            f"🎨 **Project Analysis: {project_name}**\n",
            f"I've completed a comprehensive analysis of your {project.project_type.replace('_', ' ')} project. Here's what I found:\n"
        ]
        
        # Overall assessment
        overall_score = analysis.get('overall_score', 0.5)
        if overall_score > 0.8:
            summary.append("✨ **Excellent work!** Your project shows strong design principles and execution.")
        elif overall_score > 0.6:
            summary.append("👍 **Good foundation** with some areas for improvement.")
        else:
            summary.append("📈 **Significant potential** - let's focus on key improvements.")
        
        # Key strengths and areas for improvement
        insights = analysis.get('detailed_insights', [])
        high_scores = [i for i in insights if i.get('score', 0) > 0.8]
        low_scores = [i for i in insights if i.get('score', 0) < 0.6]
        
        if high_scores:
            summary.append(f"\n**Strengths** ({len(high_scores)} areas):")
            for insight in high_scores[:3]:
                summary.append(f"• {insight.get('title', 'Unknown')}")
        
        if low_scores:
            summary.append(f"\n**Improvement Opportunities** ({len(low_scores)} areas):")
            for insight in low_scores[:3]:
                summary.append(f"• {insight.get('title', 'Unknown')}")
        
        # Next steps
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            summary.append(f"\n**Recommended Next Steps:**")
            for rec in recommendations[:3]:
                summary.append(f"1. {rec.get('title', 'Unknown recommendation')}")
        
        summary.append(f"\n💬 **Want to discuss any of these insights?** Just ask me!")
        
        return "\n".join(summary)