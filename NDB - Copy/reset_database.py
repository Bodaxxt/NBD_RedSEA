#!/usr/bin/env python3
"""
🗑️ Reset Database Script
حذف جميع البيانات وإعادة تهيئة قاعدة البيانات
"""

import psycopg
from database import NEON_DB_URL

def reset_database():
    """حذف جميع الجداول وإعادة إنشاؤها من الصفر"""
    try:
        print("⚠️  WARNING: This will DELETE ALL DATA from the database!")
        confirm = input("Are you sure? Type 'YES' to confirm: ")
        
        if confirm != "YES":
            print("❌ Operation cancelled.")
            return
        
        print("🔄 Connecting to database...")
        conn = psycopg.connect(NEON_DB_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # حذف جميع الجداول
        print("🗑️  Dropping all tables...")
        cursor.execute("""
            DROP TABLE IF EXISTS notifications CASCADE;
            DROP TABLE IF EXISTS engineers CASCADE;
            DROP TABLE IF EXISTS updates CASCADE;
            DROP TABLE IF EXISTS cycles CASCADE;
        """)
        print("✅ Tables dropped!")
        
        # إعادة الاتصال
        cursor.close()
        conn.close()
        
        # إعادة تهيئة قاعدة البيانات
        print("🔄 Re-initializing database...")
        from database import DatabaseManager
        db = DatabaseManager()
        print("✅ Database reinitialized successfully!")
        
        print("\n✨ All done! Start fresh with a clean database.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    reset_database()
