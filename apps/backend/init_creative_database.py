#!/usr/bin/env python3
"""
Creative Projects Database initialization script for MindForge
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mindforge_creative.db")

def create_tables():
    """Create all necessary tables for creative projects"""
    
    engine = create_engine(DATABASE_URL)
    
    # Creative projects tables
    with engine.connect() as conn:
        # Main projects table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS creative_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                project_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'uploaded',
                description TEXT,
                original_filename VARCHAR(500),
                file_path VARCHAR(1000),
                file_size INTEGER,
                mime_type VARCHAR(100),
                metadata JSON DEFAULT '{}',
                extracted_text TEXT,
                color_palette JSON,
                dimensions JSON,
                tags JSON DEFAULT '[]',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Project questions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                question_type VARCHAR(50),
                options JSON,
                answer TEXT,
                is_answered INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                answered_at DATETIME,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id)
            )
        """))
        
        # Project insights table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                insight_type VARCHAR(100),
                title VARCHAR(255),
                description TEXT,
                score REAL,
                data JSON DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id)
            )
        """))
        
        # Team members table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(100),
                avatar_url VARCHAR(500),
                is_active INTEGER DEFAULT 1,
                permissions JSON DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Project shares table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                shared_by INTEGER NOT NULL,
                shared_with INTEGER,
                share_token VARCHAR(255) UNIQUE NOT NULL,
                permissions JSON DEFAULT '{"view": true, "comment": false, "edit": false}',
                expires_at DATETIME,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id),
                FOREIGN KEY (shared_by) REFERENCES team_members (id),
                FOREIGN KEY (shared_with) REFERENCES team_members (id)
            )
        """))
        
        # Project comments table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                comment_type VARCHAR(50) DEFAULT 'general',
                metadata JSON DEFAULT '{}',
                is_resolved INTEGER DEFAULT 0,
                resolved_by INTEGER,
                resolved_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id),
                FOREIGN KEY (author_id) REFERENCES team_members (id),
                FOREIGN KEY (resolved_by) REFERENCES team_members (id)
            )
        """))
        
        # Project activity table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                activity_type VARCHAR(100) NOT NULL,
                description TEXT,
                metadata JSON DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id),
                FOREIGN KEY (user_id) REFERENCES team_members (id)
            )
        """))
        
        conn.commit()
    
    print("✅ Creative projects database tables created successfully!")

def create_sample_data():
    """Create sample data for testing"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Create a sample team member
        conn.execute(text("""
            INSERT OR IGNORE INTO team_members (id, name, email, role)
            VALUES (1, 'Casey AI', 'casey@mindforge.ai', 'ai_assistant')
        """))
        
        # Create a sample user
        conn.execute(text("""
            INSERT OR IGNORE INTO team_members (id, name, email, role) 
            VALUES (2, 'Demo User', 'demo@example.com', 'designer')
        """))
        
        conn.commit()
    
    print("✅ Sample data created!")

if __name__ == "__main__":
    print("🎨 Initializing MindForge Creative Projects Database…")
    create_tables()
    create_sample_data()
    print("🎉 Creative projects database setup complete!")
