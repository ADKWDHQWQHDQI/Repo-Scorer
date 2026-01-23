"""
Migration script to add email click tracking columns to user_emails table
Run this script to update your existing database with the new tracking columns.
"""
import pyodbc
import os
from dotenv import load_dotenv

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


def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '{table_name}' 
        AND COLUMN_NAME = '{column_name}'
    """)
    result = cursor.fetchone()
    return result[0] > 0


def migrate_database():
    """Add click tracking columns to user_emails table"""
    try:
        print("=" * 60)
        print("Email Click Tracking Migration")
        print("=" * 60)
        print()
        
        # Connect to database
        print(f"Connecting to database: {SQL_DATABASE}...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print("✅ Connected successfully")
        print()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'user_emails'
        """)
        if cursor.fetchone()[0] == 0:
            print("⚠️  user_emails table does not exist. Please run init_db() first.")
            cursor.close()
            conn.close()
            return
        
        print("📊 Checking existing columns...")
        
        # Check and add report_viewed column
        if check_column_exists(cursor, 'user_emails', 'report_viewed'):
            print("ℹ️  Column 'report_viewed' already exists, skipping...")
        else:
            print("Adding column 'report_viewed'...")
            cursor.execute("""
                ALTER TABLE user_emails 
                ADD report_viewed BIT NOT NULL DEFAULT 0
            """)
            conn.commit()
            print("✅ Added column 'report_viewed'")
        
        # Check and add viewed_at column
        if check_column_exists(cursor, 'user_emails', 'viewed_at'):
            print("ℹ️  Column 'viewed_at' already exists, skipping...")
        else:
            print("Adding column 'viewed_at'...")
            cursor.execute("""
                ALTER TABLE user_emails 
                ADD viewed_at DATETIME NULL
            """)
            conn.commit()
            print("✅ Added column 'viewed_at'")
        
        print()
        print("=" * 60)
        print("Migration completed successfully! 🎉")
        print("=" * 60)
        print()
        print("New features enabled:")
        print("  • Track when users click 'View Report' in emails")
        print("  • Record timestamp of report views")
        print("  • Data stored in user_emails table")
        print()
        
        # Show updated schema
        print("Updated table schema:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'user_emails'
            ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        print("\n  user_emails table:")
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"    - {col[0]}: {col[1]} ({nullable})")
        
        cursor.close()
        conn.close()
        
    except pyodbc.Error as e:
        print(f"❌ Database error: {e}")
        print("\nPlease ensure:")
        print("  1. Azure SQL Server is accessible")
        print("  2. Firewall rules allow your IP")
        print("  3. Credentials are correct in .env file")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    migrate_database()
