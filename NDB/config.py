import json
import os
from datetime import datetime

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "company": {
                "name": "Red Sea Airlines",
                "logo_path": "assets/red_sea_logo.png",
                "theme": {
                    "primary": "#C8102E",
                    "secondary": "#003366",
                    "accent": "#FFD700",
                    "background": "#F5F5F5"
                }
            },
            "alerts": {
                "advance_days": 13,
                "enable_notifications": True,
                "enable_sounds": True,
                "check_interval_hours": 1
            },
            "database": {
                "path": "database/fms_updates.db",
                "backup_days": 7
            },
            "updates": {
                "upload_folder": "uploads",
                "allowed_extensions": [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".txt"]
            },
            "cycle_duration_days": 28
        }
        self.load_config()
    
    def load_config(self):
        """تحميل الإعدادات من الملف"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # تحديث الإعدادات القديمة
                self.config = self.update_config(self.config, self.default_config)
            except:
                self.config = self.default_config.copy()
        else:
            self.config = self.default_config.copy()
            self.save_config()
    
    def update_config(self, old_config, default_config):
        """تحديث الإعدادات القديمة"""
        for key in default_config:
            if key not in old_config:
                old_config[key] = default_config[key]
            elif isinstance(default_config[key], dict) and isinstance(old_config[key], dict):
                old_config[key] = self.update_config(old_config[key], default_config[key])
        return old_config
    
    def save_config(self):
        """حفظ الإعدادات في الملف"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def get(self, key_path, default=None):
        """الحصول على قيمة إعداد"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """تعيين قيمة إعداد"""
        keys = key_path.split('.')
        config_ref = self.config
        
        for i, key in enumerate(keys[:-1]):
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        config_ref[keys[-1]] = value
        self.save_config()
    
    def get_theme_colors(self):
        """الحصول على ألوان الثيم"""
        return self.get("company.theme", self.default_config["company"]["theme"])
    
    def get_alert_days(self):
        """الحصول على عدد أيام التنبيه المسبق"""
        return self.get("alerts.advance_days", 13)