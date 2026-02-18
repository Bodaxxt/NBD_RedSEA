import tkinter as tk
from tkinter import ttk, messagebox
from config import Config

class SettingsWindow:
    def __init__(self, parent, config, on_save_callback=None):
        self.parent = parent
        self.config = config
        self.on_save = on_save_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Settings - Red Sea Airlines FMS Manager")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        self.center_window()
        self.create_widgets()
        
    def center_window(self):
        """تحريك النافذة لمنتصف الشاشة"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """إنشاء عناصر واجهة الإعدادات"""
        
        # دفتر التبويبات
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # تبويب الإشعارات
        alerts_frame = ttk.Frame(notebook)
        notebook.add(alerts_frame, text="Notifications")
        self.create_alerts_tab(alerts_frame)
        
        # تبويب المظهر
        appearance_frame = ttk.Frame(notebook)
        notebook.add(appearance_frame, text="Appearance")
        self.create_appearance_tab(appearance_frame)
        
        # تبويب قاعدة البيانات
        database_frame = ttk.Frame(notebook)
        notebook.add(database_frame, text="Database")
        self.create_database_tab(database_frame)
        
        # تبويب عام
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        self.create_general_tab(general_frame)
        
        # أزرار الحفظ والإلغاء
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            style='RedSea.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="Restore Defaults",
            command=self.restore_defaults
        ).pack(side='left', padx=5)
    
    def create_alerts_tab(self, parent):
        """إنشاء تبويب الإشعارات"""
        # متغيرات التتبع
        self.enable_notifications = tk.BooleanVar(value=self.config.get("alerts.enable_notifications", True))
        self.enable_sounds = tk.BooleanVar(value=self.config.get("alerts.enable_sounds", True))
        self.advance_days = tk.IntVar(value=self.config.get("alerts.advance_days", 13))
        self.check_interval = tk.IntVar(value=self.config.get("alerts.check_interval_hours", 1))
        
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        # الإشعارات
        ttk.Checkbutton(
            frame,
            text="Enable Windows Notifications",
            variable=self.enable_notifications
        ).pack(anchor='w', pady=5)
        
        ttk.Checkbutton(
            frame,
            text="Enable Alert Sounds",
            variable=self.enable_sounds
        ).pack(anchor='w', pady=5)
        
        # أيام التنبيه المسبق
        days_frame = ttk.Frame(frame)
        days_frame.pack(fill='x', pady=10)
        
        ttk.Label(days_frame, text="Advance Alert Days:").pack(side='left', padx=5)
        days_spinbox = ttk.Spinbox(
            days_frame,
            from_=1,
            to=30,
            textvariable=self.advance_days,
            width=10
        )
        days_spinbox.pack(side='left', padx=5)
        ttk.Label(days_frame, text="days before expiration").pack(side='left', padx=5)
        
        # فحص الفاصل الزمني
        interval_frame = ttk.Frame(frame)
        interval_frame.pack(fill='x', pady=10)
        
        ttk.Label(interval_frame, text="Check Interval:").pack(side='left', padx=5)
        interval_spinbox = ttk.Spinbox(
            interval_frame,
            from_=1,
            to=24,
            textvariable=self.check_interval,
            width=10
        )
        interval_spinbox.pack(side='left', padx=5)
        ttk.Label(interval_frame, text="hours").pack(side='left', padx=5)
        
        # معلومات
        info_label = ttk.Label(
            frame,
            text="Notifications will appear even when the program is closed.",
            font=('Arial', 9),
            foreground='gray'
        )
        info_label.pack(pady=20)
    
    def create_appearance_tab(self, parent):
        """إنشاء تبويب المظهر"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        # الألوان
        colors = self.config.get_theme_colors()
        
        ttk.Label(frame, text="Theme Colors", font=('Arial', 11, 'bold')).pack(anchor='w', pady=10)
        
        # عرض الألوان الحالية
        colors_frame = ttk.Frame(frame)
        colors_frame.pack(fill='x', pady=10)
        
        for i, (color_name, color_value) in enumerate(colors.items()):
            color_frame = ttk.Frame(colors_frame)
            color_frame.pack(fill='x', pady=5)
            
            ttk.Label(color_frame, text=color_name.title() + ":").pack(side='left', padx=5)
            
            # عرض اللون
            color_display = tk.Frame(color_frame, width=50, height=20, bg=color_value)
            color_display.pack(side='left', padx=5)
            
            ttk.Label(color_frame, text=color_value).pack(side='left', padx=5)
        
        # ملاحظة
        note_label = ttk.Label(
            frame,
            text="Note: Theme changes require restarting the application.",
            font=('Arial', 9),
            foreground='gray'
        )
        note_label.pack(pady=20)
    
    def create_database_tab(self, parent):
        """إنشاء تبويب قاعدة البيانات"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        # معلومات قاعدة البيانات
        db_info = [
            ("Database Path:", self.config.get("database.path", "database/fms_updates.db")),
            ("Backup Retention:", f"{self.config.get('database.backup_days', 7)} days"),
            ("Upload Folder:", self.config.get("updates.upload_folder", "uploads"))
        ]
        
        for label, value in db_info:
            item_frame = ttk.Frame(frame)
            item_frame.pack(fill='x', pady=5)
            
            ttk.Label(item_frame, text=label, width=20, anchor='w').pack(side='left')
            ttk.Label(item_frame, text=value).pack(side='left', padx=10)
        
        # أزرار إدارة قاعدة البيانات
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(
            buttons_frame,
            text="Create Backup Now",
            command=self.create_backup
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Export Data to CSV",
            command=self.export_data
        ).pack(side='left', padx=5)
    
    def create_general_tab(self, parent):
        """إنشاء تبويب الإعدادات العامة"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        # معلومات الشركة
        company_frame = ttk.LabelFrame(frame, text="Company Information", padding=10)
        company_frame.pack(fill='x', pady=10)
        
        ttk.Label(company_frame, text="Company Name:").pack(anchor='w', pady=5)
        self.company_name = ttk.Entry(company_frame, width=40)
        self.company_name.insert(0, self.config.get("company.name", "Red Sea Airlines"))
        self.company_name.pack(fill='x', pady=5)
        
        # دورة CYCLE
        cycle_frame = ttk.LabelFrame(frame, text="Cycle Settings", padding=10)
        cycle_frame.pack(fill='x', pady=10)
        
        ttk.Label(cycle_frame, text="Cycle Duration:").pack(anchor='w', pady=5)
        
        duration_frame = ttk.Frame(cycle_frame)
        duration_frame.pack(fill='x', pady=5)
        
        self.cycle_duration = tk.IntVar(value=self.config.get("cycle_duration_days", 28))
        ttk.Spinbox(
            duration_frame,
            from_=14,
            to=60,
            textvariable=self.cycle_duration,
            width=10
        ).pack(side='left', padx=5)
        ttk.Label(duration_frame, text="days").pack(side='left', padx=5)
    
    def save_settings(self):
        """حفظ الإعدادات"""
        try:
            # حفظ إعدادات الإشعارات
            self.config.set("alerts.enable_notifications", self.enable_notifications.get())
            self.config.set("alerts.enable_sounds", self.enable_sounds.get())
            self.config.set("alerts.advance_days", self.advance_days.get())
            self.config.set("alerts.check_interval_hours", self.check_interval.get())
            
            # حفظ الإعدادات العامة
            self.config.set("company.name", self.company_name.get())
            self.config.set("cycle_duration_days", self.cycle_duration.get())
            
            if self.on_save:
                self.on_save()
            
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save settings: {str(e)}")
    
    def restore_defaults(self):
        """استعادة الإعدادات الافتراضية"""
        if messagebox.askyesno("Restore Defaults", 
                             "Are you sure you want to restore all settings to defaults?"):
            self.config.config = self.config.default_config.copy()
            self.config.save_config()
            
            if self.on_save:
                self.on_save()
            
            messagebox.showinfo("Defaults Restored", "Settings have been restored to defaults.")
            self.window.destroy()
    
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        from utils import Utilities
        db_path = self.config.get("database.path", "database/fms_updates.db")
        
        if Utilities.backup_database(db_path):
            messagebox.showinfo("Backup Created", "Database backup created successfully!")
        else:
            messagebox.showerror("Backup Failed", "Failed to create database backup.")
    
    def export_data(self):
        """تصدير البيانات"""
        from data_processor import DataProcessor
        
        processor = DataProcessor()
        export_path = processor.export_to_csv()
        
        messagebox.showinfo("Export Complete", 
                          f"Data exported successfully to:\n{export_path}")