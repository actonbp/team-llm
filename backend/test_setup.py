"""
Test script to verify backend setup
"""
import asyncio
from app.db.database import engine, Base
from app.models import *  # Import all models to register them


async def test_database_setup():
    """Test database connection and table creation"""
    print("Testing database setup...")
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Database tables created successfully")
        
        # Test connection
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            print("✓ Database connection successful")
            
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False
    
    return True


async def main():
    """Run all tests"""
    print("Team-LLM Backend Setup Test\n")
    
    # Test database
    db_ok = await test_database_setup()
    
    print("\nSetup test complete!")
    print(f"Database: {'✓ OK' if db_ok else '✗ Failed'}")


if __name__ == "__main__":
    asyncio.run(main())