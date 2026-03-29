#!/usr/bin/env python3
"""
Red Sea Airlines FMS Manager - Main Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """التحقق من تثبيت المتطلبات"""
    required_packages = ['pandas', 'PIL']
    
    # win10toast مطلوب فقط لنظام Windows
    if sys.platform == 'win32':
        required_packages.append('win10toast')
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """تثبيت المتطلبات المفقودة"""
    print("Installing required packages...")
    try:
        # تثبيت المتطلبات الأساسية أولاً
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "pillow"])
        
        # تثبيت win10toast فقط لنظام Windows
        if sys.platform == 'win32':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "win10toast"])
        
        return True
    except Exception as e:
        print(f"Failed to install dependencies: {e}")
        print("\nPlease install manually:")
        print("pip install pandas pillow")
        if sys.platform == 'win32':
            print("pip install win10toast")
        return False

def create_minimal_requirements():
    """إنشاء ملف متطلبات أدنى"""
    with open('minimal_requirements.txt', 'w') as f:
        f.write("pandas>=1.5.0\n")
        f.write("pillow>=9.0.0\n")
        if sys.platform == 'win32':
            f.write("win10toast>=0.9\n")

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("Red Sea Airlines FMS Navigation Data Manager")
    print("=" * 50)
    
    # إنشاء ملف متطلبات أدنى
    create_minimal_requirements()
    
    # التحقق من الملفات المطلوبة
    required_files = ['main.py', 'database.py', 'gui.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: Required file '{file}' not found!")
            print("Please make sure all files are in the same directory.")
            input("Press Enter to exit...")
            return
    
    # التحقق من المتطلبات
    missing = check_dependencies()
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        response = input("Install missing packages? (y/n): ")
        if response.lower() == 'y':
            if not install_dependencies():
                print("\nYou can still run the application without some features.")
                print("Notifications will be limited.")
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    return
        else:
            print("\nSome features may not work without required packages.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return
    
    # إنشاء المجلدات المطلوبة
    folders = ['database', 'uploads', 'backups', 'assets']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # إنشاء لوجو مؤقت إذا لم يكن موجودًا
    if not os.path.exists("assets/red_sea_logo.png"):
        print("\nCreating temporary logo...")
        try:
            from create_logo import create_temporary_logo
            create_temporary_logo()
        except Exception as e:
            print(f"Could not create logo: {e}")
            print("Using text logo instead.")
    
    # تشغيل التطبيق الرئيسي
    print("\nStarting FMS Manager...")
    print("-" * 50)
    
    try:
        from main import FMSNavDataManager
        app = FMSNavDataManager()
        app.run()
    except ImportError as e:
        print(f"\nImport Error: {e}")
        print("\nTrying alternative startup...")
        alternative_startup()
    except Exception as e:
        print(f"\nError starting application: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

def alternative_startup():
    """بدء تشغيل بديل بدون واجهة رسومية كاملة"""
    try:
        print("\nStarting in simplified mode...")
        
        # استيراد المكونات الأساسية فقط
        import sqlite3
        from datetime import datetime
        
        # إنشاء قاعدة بيانات بسيطة
        db_path = "database/fms_updates.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # إنشاء جداول أساسية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycles (
                cycle_number TEXT PRIMARY KEY,
                effective_date TEXT,
                status TEXT
            )
        ''')
        
        # إضافة بعض البيانات الاختبارية
        test_cycles = [
            ('2501', '2025-01-23', 'active'),
            ('2502', '2025-02-20', 'upcoming'),
        ]
        
        for cycle in test_cycles:
            cursor.execute('''
                INSERT OR REPLACE INTO cycles VALUES (?, ?, ?)
            ''', cycle)
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("FMS Manager - Command Line Interface")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Check current cycle")
            print("2. View all cycles")
            print("3. Exit")
            
            choice = input("\nEnter choice (1-3): ")
            
            if choice == '1':
                check_current_cycle()
            elif choice == '2':
                view_all_cycles()
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid choice!")
    
    except Exception as e:
        print(f"Error in alternative startup: {e}")
        input("\nPress Enter to exit...")

def check_current_cycle():
    """التحقق من CYCLE الحالي"""
    import sqlite3
    from datetime import datetime
    
    conn = sqlite3.connect("database/fms_updates.db")
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT * FROM cycles 
        WHERE effective_date <= ? 
        ORDER BY effective_date DESC 
        LIMIT 1
    ''', (today,))
    
    cycle = cursor.fetchone()
    
    if cycle:
        print(f"\nCurrent Cycle: {cycle[0]}")
        print(f"Effective Date: {cycle[1]}")
        print(f"Status: {cycle[2]}")
        
        # حساب الأيام المتبقية
        effective_date = datetime.strptime(cycle[1], '%Y-%m-%d')
        next_cycle_date = effective_date.replace(day=effective_date.day + 28)
        days_remaining = (next_cycle_date - datetime.now()).days
        
        print(f"Days Remaining: {max(0, days_remaining)}")
        
        if days_remaining <= 13:
            print("⚠️  NEW CYCLE ALERT: Yes (13 days or less remaining)")
        else:
            print("NEW CYCLE ALERT: No")
    else:
        print("\nNo current cycle found!")
    
    conn.close()

def view_all_cycles():
    """عرض جميع CYCLES"""
    import sqlite3
    
    conn = sqlite3.connect("database/fms_updates.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM cycles ORDER BY effective_date')
    cycles = cursor.fetchall()
    
    print("\n" + "="*60)
    print(f"{'Cycle':<10} {'Effective Date':<15} {'Status':<10}")
    print("="*60)
    
    for cycle in cycles:
        print(f"{cycle[0]:<10} {cycle[1]:<15} {cycle[2]:<10}")
    
    conn.close()

if __name__ == "__main__":
    main()