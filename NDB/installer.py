import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

class Installer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Red Sea Airlines FMS Manager - Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.center_window()
        self.create_widgets()
    
    def center_window(self):
        """تحريك النافذة لمنتصف الشاشة"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """إنشاء واجهة المثبت"""
        # العنوان
        title_frame = ttk.Frame(self.root, padding=20)
        title_frame.pack(fill='x')
        
        ttk.Label(
            title_frame,
            text="Red Sea Airlines FMS Manager",
            font=('Arial', 16, 'bold'),
            foreground='#C8102E'
        ).pack()
        
        ttk.Label(
            title_frame,
            text="Installation Wizard",
            font=('Arial', 12)
        ).pack(pady=5)
        
        # معلومات التثبيت
        info_frame = ttk.LabelFrame(self.root, text="Installation Information", padding=15)
        info_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        info_text = """This will install Red Sea Airlines FMS Navigation Data Manager.

Features:
• FMS Cycle Tracking and Alerts
• Automatic Windows Notifications
• Update Registration System
• Complete History Logging

Requirements:
• Windows 10/11
• Python 3.8 or higher
• 100MB free disk space"""
        
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')
        
        # مسار التثبيت
        path_frame = ttk.Frame(self.root)
        path_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(path_frame, text="Installation Path:").pack(side='left', padx=5)
        
        self.install_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "RedSeaFMS"))
        path_entry = ttk.Entry(path_frame, textvariable=self.install_path, width=40)
        path_entry.pack(side='left', padx=5)
        
        ttk.Button(
            path_frame,
            text="Browse",
            command=self.browse_path
        ).pack(side='left', padx=5)
        
        # شريط التقدم
        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress.pack(padx=20, pady=10)
        
        self.status_label = ttk.Label(self.root, text="Ready to install")
        self.status_label.pack(pady=5)
        
        # أزرار التحكم
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text="Install",
            command=self.start_installation,
            style='RedSea.TButton'
        ).pack(side='left', padx=10)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.root.destroy
        ).pack(side='left', padx=10)
    
    def browse_path(self):
        """فتح نافذة اختيار المسار"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Installation Folder")
        if path:
            self.install_path.set(path)
    
    def start_installation(self):
        """بدء عملية التثبيت"""
        install_dir = self.install_path.get()
        
        if not install_dir:
            messagebox.showerror("Error", "Please select an installation path")
            return
        
        # تحديث الواجهة
        self.status_label.config(text="Starting installation...")
        self.progress['value'] = 10
        self.root.update()
        
        try:
            # 1. إنشاء المجلدات
            self.status_label.config(text="Creating folders...")
            self.create_folders(install_dir)
            self.progress['value'] = 20
            
            # 2. نسخ الملفات
            self.status_label.config(text="Copying files...")
            self.copy_files(install_dir)
            self.progress['value'] = 40
            
            # 3. إنشاء لوجو مؤقت
            self.status_label.config(text="Creating logo...")
            from create_logo import create_temporary_logo
            create_temporary_logo()
            self.progress['value'] = 50
            
            # 4. تثبيت المتطلبات
            self.status_label.config(text="Installing dependencies...")
            self.install_dependencies(install_dir)
            self.progress['value'] = 80
            
            # 5. إنشاء اختصار
            self.status_label.config(text="Creating shortcuts...")
            self.create_shortcuts(install_dir)
            self.progress['value'] = 100
            
            # إكمال التثبيت
            self.status_label.config(text="Installation complete!")
            
            messagebox.showinfo(
                "Installation Complete",
                f"Red Sea Airlines FMS Manager has been installed successfully!\n\n"
                f"Location: {install_dir}\n\n"
                f"Run 'run.bat' to start the application."
            )
            
            # فتح مجلد التثبيت
            if messagebox.askyesno("Open Folder", "Open installation folder?"):
                os.startfile(install_dir)
            
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Installation Failed", f"Error during installation:\n{str(e)}")
            self.status_label.config(text="Installation failed")
    
    def create_folders(self, install_dir):
        """إنشاء مجلدات التثبيت"""
        folders = [
            install_dir,
            os.path.join(install_dir, "database"),
            os.path.join(install_dir, "uploads"),
            os.path.join(install_dir, "backups"),
            os.path.join(install_dir, "assets")
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    def copy_files(self, install_dir):
        """نسخ ملفات البرنامج"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        files_to_copy = [
            'main.py', 'database.py', 'gui.py', 'scheduler.py',
            'notifications.py', 'config.py', 'data_processor.py',
            'utils.py', 'settings_gui.py', 'create_logo.py',
            'requirements.txt', 'run.bat', 'README.md'
        ]
        
        for file in files_to_copy:
            source = os.path.join(current_dir, file)
            destination = os.path.join(install_dir, file)
            
            if os.path.exists(source):
                import shutil
                shutil.copy2(source, destination)
    
    def install_dependencies(self, install_dir):
        """تثبيت متطلبات Python"""
        requirements_file = os.path.join(install_dir, "requirements.txt")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "-r", requirements_file])
        except:
            # محاولة بديلة
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install",
                                     "pandas", "pillow", "win10toast"])
            except Exception as e:
                print(f"Warning: Failed to install some dependencies: {e}")
    
    def create_shortcuts(self, install_dir):
        """إنشاء اختصارات"""
        # إنشاء ملف تشغيل
        run_script = os.path.join(install_dir, "start_fms.bat")
        with open(run_script, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'cd /d "{install_dir}"\n')
            f.write(f'python main.py\n')
            f.write(f'pause\n')
        
        # محاولة إنشاء اختصار على سطح المكتب
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "Red Sea FMS Manager.lnk")
            
            import winshell
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = run_script
            shortcut.WorkingDirectory = install_dir
            shortcut.IconLocation = os.path.join(install_dir, "assets", "red_sea_logo.png")
            shortcut.save()
        except:
            pass  # تجاهل فشل إنشاء الاختصار

def main():
    installer = Installer()
    installer.root.mainloop()

if __name__ == "__main__":
    main()