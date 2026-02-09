import os
import shutil
from datetime import datetime, timedelta
import hashlib

class Utilities:
    @staticmethod
    def format_date(date_str, format_from='%Y-%m-%d', format_to='%d/%m/%Y'):
        """تنسيق التاريخ"""
        try:
            date_obj = datetime.strptime(date_str, format_from)
            return date_obj.strftime(format_to)
        except:
            return date_str
    
    @staticmethod
    def calculate_working_days(start_date, end_date):
        """حساب أيام العمل"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # من الإثنين إلى الجمعة
                days += 1
            current += timedelta(days=1)
        
        return days
    
    @staticmethod
    def backup_database(source_path, backup_folder="backups"):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        if not os.path.exists(source_path):
            return False
        
        os.makedirs(backup_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"fms_backup_{timestamp}.db"
        backup_path = os.path.join(backup_folder, backup_name)
        
        try:
            shutil.copy2(source_path, backup_path)
            
            # حذف النسخ القديمة (أقدم من 30 يوم)
            cutoff_date = datetime.now() - timedelta(days=30)
            for file in os.listdir(backup_folder):
                file_path = os.path.join(backup_folder, file)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
            
            return backup_path
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    @staticmethod
    def validate_file_extension(filename, allowed_extensions):
        """التحقق من امتداد الملف"""
        _, ext = os.path.splitext(filename)
        return ext.lower() in allowed_extensions
    
    @staticmethod
    def calculate_file_hash(filepath):
        """حساب بصمة الملف"""
        try:
            with open(filepath, 'rb') as f:
                file_hash = hashlib.md5()
                chunk = f.read(8192)
                while chunk:
                    file_hash.update(chunk)
                    chunk = f.read(8192)
                return file_hash.hexdigest()
        except:
            return None
    
    @staticmethod
    def get_file_size(filepath):
        """الحصول على حجم الملف"""
        try:
            size_bytes = os.path.getsize(filepath)
            
            # تحويل إلى وحدات مناسبة
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            
            return f"{size_bytes:.2f} TB"
        except:
            return "Unknown"