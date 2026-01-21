import logging
from datetime import datetime

# إعداد السجل
logging.basicConfig(
    filename='fms_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NotificationManager:
    def __init__(self):
        self.toaster = None
        self.setup_notifications()
    
    def setup_notifications(self):
        """إعداد نظام الإشعارات"""
        try:
            from win10toast import ToastNotifier
            self.toaster = ToastNotifier()
            logging.info("Windows notifications enabled")
        except ImportError:
            self.toaster = None
            logging.warning("win10toast not installed. Windows notifications disabled.")
    
    def send_notification(self, title, message, urgent=False):
        """إرسال إشعار"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"{title}: {message}"
        
        # 1. تسجيل في ملف السجل
        self.log_notification(title, message)
        
        # 2. إرسال إشعار Windows (إذا كان مدعومًا)
        if self.toaster:
            try:
                duration = 10 if urgent else 5
                self.toaster.show_toast(
                    title,
                    message,
                    duration=duration,
                    threaded=True
                )
                logging.info(f"Windows notification sent: {title}")
            except Exception as e:
                logging.error(f"Failed to send Windows notification: {e}")
        
        # 3. طباعة في الكونسول (للتسجيل)
        print(f"[{timestamp}] {full_message}")
        
        # 4. تشغيل صوت تنبيه (إذا كان Windows)
        if urgent:
            self.play_alert_sound()
    
    def log_notification(self, title, message):
        """تسجيل الإشعار في ملف السجل"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {title}: {message}\n"
        
        try:
            with open('notification_log.txt', 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logging.error(f"Failed to write to log file: {e}")
    
    def play_alert_sound(self):
        """تشغيل صوت تنبيه"""
        try:
            import winsound
            winsound.Beep(1000, 500)  # صوت عالي للتنبيه العاجل
        except ImportError:
            # إذا لم يكن winsound متاحًا
            print("\a")  # صوت تنبيه نظامي بسيط
        except Exception as e:
            logging.error(f"Failed to play alert sound: {e}")
    
    def send_windows_notification_alternative(self, title, message):
        """طريقة بديلة لإرسال إشعارات Windows"""
        try:
            # استخدام نظام الإشعارات المدمج في Windows
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0)
            return True
        except:
            return False