import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# إضافة مسار المجلد الحالي لاستيراد الملفات الأخرى
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui import MainApplication
from database import DatabaseManager
from scheduler import AlertScheduler
from notifications import NotificationManager

class FMSNavDataManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Red Sea Airlines - FMS Nav Data Manager")
        self.root.geometry("1200x700")
        
        # مركز النافذة على الشاشة
        self.center_window()
        
        # تهيئة المكونات
        self.db = DatabaseManager()
        self.notifier = NotificationManager()
        self.scheduler = AlertScheduler(self.db, self.notifier)
        
        # إنشاء واجهة المستخدم
        self.app = MainApplication(self.root, self.db, self.notifier, self.scheduler)
        
        # إضافة حقل لتحديد التاريخ أو الوقت
        self.date_entry = ttk.Entry(self.root)
        self.date_entry.pack(pady=10)
        self.date_entry_label = ttk.Label(self.root, text="أدخل التاريخ أو الوقت:")
        self.date_entry_label.pack(pady=5)
        
        # بدء المراقبة التلقائية
        self.start_monitoring()
        
    def center_window(self):
        """لتحريك النافذة إلى منتصف الشاشة"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def start_monitoring(self):
        """بدء مراقبة التواريخ والتنبيهات"""
        self.scheduler.start()
        self.check_current_cycle()
        
    def check_current_cycle(self):
        """التحقق من الدورة الحالية والقادمة وحالة التسجيل"""
        
        # 1. تحديث الحالات أوتوماتيكياً بناءً على التاريخ
        # هذه الخطوة مهمة لضمان أن الدورة الحالية تأخذ حالة ACTIVE والقديمة EXPIRED
        self.db.auto_update_statuses_by_date()
        
        # 2. جلب بيانات الدورة الحالية (ACTIVE)
        # نحتاج دالة في قاعدة البيانات تجلب تفاصيل الدورة الفعالة حالياً
        active_cycle_data = self.db.get_active_cycle_data() 
        
        # 3. جلب بيانات الدورة القادمة (UPCOMING) لحساب العداد
        upcoming_cycle_data, days_remaining = self.db.get_upcoming_cycle_data()

        # 4. فحص: هل الدورة الحالية (Active) تم تسجيل تحديثها من قبل المهندس؟
        is_recorded = True
        if active_cycle_data:
            # نفترض أن active_cycle_data قاموس أو صف يحتوي على رقم الدورة
            cycle_number = active_cycle_data.get('cycle_number') if isinstance(active_cycle_data, dict) else active_cycle_data[0]
            is_recorded = self.db.check_if_update_recorded(cycle_number)

        # 5. تحديث الواجهة لعرض المعلومات
        # سنمرر الدورتين (الحالية والقادمة) للواجهة
        self.app.update_dashboard_display(active_cycle_data, upcoming_cycle_data, days_remaining, is_recorded)
    def run(self):
        """تشغيل التطبيق"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """عند إغلاق النافذة"""
        self.scheduler.stop()
        self.root.destroy()

if __name__ == "__main__":
    app = FMSNavDataManager()
    app.run()
