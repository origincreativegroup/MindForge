"""
Example usage of the MindForge Reporting Service

This file demonstrates how to use the reporting service in your FastAPI application.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional

# Your existing imports
from backend.db import get_db  # Assuming you have a database session dependency
from backend.services.reporting import (
    ReportConfig, 
    ProjectReportGenerator, 
    ExportUtilities
)

app = FastAPI()

# Example endpoint for generating project reports
@app.post("/api/projects/{project_id}/reports")
async def generate_project_report(
    project_id: int,
    export_format: str = "pdf",
    include_analytics: bool = True,
    include_insights: bool = True,
    include_recommendations: bool = True,
    include_comments: bool = True,
    include_activity: bool = True,
    template_style: str = "professional",
    db: Session = Depends(get_db)
):
    """
    Generate a comprehensive project report.
    
    - **project_id**: The ID of the project to report on
    - **export_format**: pdf, html, json, or csv
    - **include_analytics**: Include analysis scores and metrics
    - **include_insights**: Include AI-generated insights
    - **include_recommendations**: Include improvement recommendations
    - **include_comments**: Include team comments and feedback
    - **include_activity**: Include project activity log
    - **template_style**: professional, creative, or minimal
    """
    
    # Create report configuration
    config = ReportConfig(
        include_analytics=include_analytics,
        include_insights=include_insights,
        include_recommendations=include_recommendations,
        include_comments=include_comments,
        include_activity=include_activity,
        export_format=export_format,
        template_style=template_style
    )
    
    # Generate report
    try:
        generator = ProjectReportGenerator(db)
        report_data = await generator.generate_project_report(project_id, config)
        
        # Return appropriate response based on format
        if export_format in ["pdf", "csv"]:
            # Binary or text download
            content = report_data["content"]
            if export_format == "pdf":
                # PDF is base64 encoded
                import base64
                content = base64.b64decode(content)
            
            return Response(
                content=content,
                media_type=report_data["content_type"],
                headers={
                    "Content-Disposition": f"attachment; filename={report_data['filename']}"
                }
            )
        else:
            # JSON or HTML - return as response
            return {
                "filename": report_data["filename"],
                "content_type": report_data["content_type"],
                "size": report_data["size"],
                "content": report_data["content"]
            }
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/api/analytics/team")
async def get_team_analytics(
    time_range: str = "30d",
    team_members: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get team analytics and productivity metrics.
    
    - **time_range**: 7d, 30d, or 90d
    - **team_members**: Comma-separated list of team member IDs (optional)
    """
    
    try:
        generator = ProjectReportGenerator(db)
        
        # Parse team members if provided
        team_member_ids = None
        if team_members:
            team_member_ids = [int(id.strip()) for id in team_members.split(",")]
        
        analytics = await generator.generate_team_analytics_report(
            time_range=time_range,
            team_members=team_member_ids
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")


@app.get("/api/projects/{project_id}/insights/export")
async def export_project_insights(
    project_id: int,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """
    Export project insights in JSON or CSV format.
    
    - **project_id**: The ID of the project
    - **format**: json or csv
    """
    
    try:
        generator = ProjectReportGenerator(db)
        insights_data = await generator.export_project_insights(project_id, format)
        
        if format == "csv":
            filename = f"project_{project_id}_insights.csv"
            return Response(
                content=insights_data,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return Response(
                content=insights_data,
                media_type="application/json"
            )
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight export failed: {str(e)}")


@app.get("/api/projects/{project_id}/casey-summary")
async def get_casey_project_summary(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get Casey's narrative summary of a project.
    
    - **project_id**: The ID of the project
    """
    
    try:
        generator = ProjectReportGenerator(db)
        project_data = await generator._collect_project_data(project_id)
        
        if not project_data:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        from backend.services.reporting import CaseyReportNarrator
        summary = CaseyReportNarrator.generate_project_summary(project_data)
        
        return {
            "project_id": project_id,
            "summary": summary,
            "analysis_score": project_data["analysis"].get("overall_score", 0),
            "generated_at": project_data["generated_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


if __name__ == "__main__":
    print("🎨 MindForge Reporting Service Example")
    print("=====================================")
    print()
    print("Available endpoints:")
    print("• POST /api/projects/{id}/reports - Generate comprehensive project reports")
    print("• GET  /api/analytics/team - Get team analytics and productivity metrics") 
    print("• GET  /api/projects/{id}/insights/export - Export project insights")
    print("• GET  /api/projects/{id}/casey-summary - Get Casey's narrative summary")
    print()
    print("Example usage:")
    print("curl -X POST 'http://localhost:8000/api/projects/1/reports?export_format=pdf'")
    print("curl 'http://localhost:8000/api/analytics/team?time_range=30d'")
    print("curl 'http://localhost:8000/api/projects/1/casey-summary'")
    print()
    print("Run with: uvicorn example_usage:app --reload")