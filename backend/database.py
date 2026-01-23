"""
Database configuration and models for DevSecOps Assessment - MSSQL/Azure SQL
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
import pyodbc
import urllib.parse

load_dotenv()

# MSSQL Database Configuration
SQL_SERVER = os.getenv("SQL_SERVER", "smartexpensemanager.database.windows.net")
SQL_DATABASE = os.getenv("SQL_DATABASE", "ExpenseManager")
SQL_USERNAME = os.getenv("SQL_USERNAME", "ExpenseManagerAdmin")
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "Admin@123")

# Create connection string for Azure SQL Database
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};"
    f"PWD={SQL_PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

# SQLAlchemy connection URL
params = urllib.parse.quote_plus(connection_string)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"


def check_database_connection():
    """Check if we can connect to the MSSQL database"""
    try:
        # Test connection to Azure SQL Database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if we're connected
        cursor.execute("SELECT DB_NAME()")
        result = cursor.fetchone()
        if result is None:
            print("❌ Failed to retrieve database name")
            cursor.close()
            conn.close()
            return False
        
        db_name = result[0]
        
        print(f"✅ Connected to database: {db_name}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except pyodbc.Error as e:
        print(f"❌ Error connecting to database: {e}")
        print("\nPlease ensure:")
        print("  1. Azure SQL Server is accessible")
        print("  2. Firewall rules allow your IP")
        print("  3. Credentials are correct")
        print("  4. ODBC Driver 17 for SQL Server is installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


# Create engine with Azure SQL specific settings
# Note: Database connection is NOT checked at import time to prevent blocking startup
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Database Models
class UserEmail(Base):
    """Store user emails for assessment results"""
    __tablename__ = "user_emails"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    report_viewed = Column(Boolean, default=False, nullable=False)
    viewed_at = Column(DateTime, nullable=True)
    
    # Platform selections
    repository_platform = Column(String(100), nullable=True)
    cicd_platform = Column(String(100), nullable=True)
    deployment_platform = Column(String(100), nullable=True)


class AssessmentRecord(Base):
    """Store assessment results"""
    __tablename__ = "assessment_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False, index=True)
    tool = Column(String(100), nullable=False)
    final_score = Column(Integer, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Platform selections
    repository_platform = Column(String(100), nullable=True)
    cicd_platform = Column(String(100), nullable=True)
    deployment_platform = Column(String(100), nullable=True)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create all tables
def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print(" Database tables created successfully!")
        
        # Verify tables were created
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND TABLE_NAME IN ('user_emails', 'assessment_records')
        """)
        
        tables = cursor.fetchall()
        if tables:
            print(f" Tables found: {[table[0] for table in tables]}")
        else:
            print(" Tables may not have been created. Check permissions.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("Initializing DevSecOps Assessment Database (MSSQL)")
    print("=" * 50)
    print()
    init_db()
