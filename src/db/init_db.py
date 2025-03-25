
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import engine, Base, async_session
from src.db.models import Project, Agent, Analysis
from src.core.config import settings

async def create_tables() -> None:
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")

async def init_db() -> None:
    """Initialize database with tables and seed data if needed"""
    await create_tables()
    
    # Optionally add seed data for development
    if settings.POSTGRES_DB == "qualagents_dev":
        await seed_dev_data()

async def seed_dev_data() -> None:
    """Add seed data for development environment"""
    async with async_session() as session:
        # Check if we already have data
        project_count = await session.execute("SELECT COUNT(*) FROM projects")
        if project_count.scalar_one() > 0:
            print("⏩ Development data already exists")
            return
        
        # Add a sample project
        sample_project = Project(
            name="Sample Interview Analysis",
            description="Example project for analyzing interview transcripts",
        )
        session.add(sample_project)
        
        # Add a sample agent
        sample_agent = Agent(
            name="Thematic Analyzer",
            description="Agent that performs thematic analysis on qualitative data",
            model="gpt-4o",
            configuration={
                "agent_type": "thematic_analysis",
                "system_prompt": "You are a qualitative research expert. Analyze the provided data and identify key themes.",
                "temperature": 0.7
            }
        )
        session.add(sample_agent)
        
        await session.commit()
        print("✅ Added development seed data")

if __name__ == "__main__":
    asyncio.run(init_db())
