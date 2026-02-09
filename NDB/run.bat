@echo off
chcp 65001 >nul
echo ============================================
echo Red Sea Airlines FMS Manager
echo ============================================
echo.

:: التحقق من تثبيت Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

:: إنشاء بيئة افتراضية (اختياري)
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: تنشيط البيئة الافتراضية
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: تثبيت المتطلبات الأساسية
echo Installing basic requirements...
pip install pandas pillow --quiet

:: تثبيت win10toast لنظام Windows
echo Installing Windows notifications support...
pip install win10toast --quiet

:: إنشاء المجلدات
if not exist "assets" mkdir assets
if not exist "database" mkdir database
if not exist "uploads" mkdir uploads
if not exist "backups" mkdir backups

:: إنشاء لوجو مؤقت
if not exist "assets\red_sea_logo.png" (
    echo Creating temporary logo...
    python create_logo.py
)

:: تشغيل البرنامج
echo Starting FMS Manager...
echo.
python run.py

pause