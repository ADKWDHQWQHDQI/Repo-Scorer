"""
Quick script to check data in user_emails table
"""
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

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

def check_data():
    """Check data in user_emails table"""
    try:
        print("=" * 80)
        print("USER EMAILS TABLE DATA")
        print("=" * 80)
        print()
        
        # Connect to database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM user_emails")
        total = cursor.fetchone()[0]
        print(f"📊 Total records: {total}")
        print()
        
        if total == 0:
            print("ℹ️  No records found in user_emails table")
            cursor.close()
            conn.close()
            return
        
        # Get all records
        cursor.execute("""
            SELECT 
                id, 
                email, 
                created_at, 
                is_active, 
                report_viewed, 
                viewed_at,
                repository_platform,
                cicd_platform,
                deployment_platform
            FROM user_emails 
            ORDER BY created_at DESC
        """)
        
        records = cursor.fetchall()
        
        # Display records
        print("📧 Email Records:")
        print("-" * 80)
        for record in records:
            print(f"\n🆔 ID: {record[0]}")
            print(f"   Email: {record[1]}")
            print(f"   Created: {record[2]}")
            print(f"   Active: {'✅ Yes' if record[3] else '❌ No'}")
            print(f"   Report Viewed: {'✅ Yes' if record[4] else '❌ No'}")
            print(f"   Viewed At: {record[5] if record[5] else 'Not viewed yet'}")
            print(f"   Repository Platform: {record[6] if record[6] else 'N/A'}")
            print(f"   CI/CD Platform: {record[7] if record[7] else 'N/A'}")
            print(f"   Deployment Platform: {record[8] if record[8] else 'N/A'}")
            print("-" * 80)
        
        # Show click statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CAST(report_viewed AS INT)) as clicked,
                (SUM(CAST(report_viewed AS INT)) * 100.0 / COUNT(*)) as click_rate
            FROM user_emails
        """)
        stats = cursor.fetchone()
        
        print("\n📈 Click Statistics:")
        print(f"   Total Emails Sent: {stats[0]}")
        print(f"   Reports Viewed: {stats[1]}")
        print(f"   Click Rate: {stats[2]:.1f}%")
        
        cursor.close()
        conn.close()
        
    except pyodbc.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    check_data()
