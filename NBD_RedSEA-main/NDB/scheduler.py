import threading
import time
from datetime import datetime, timedelta

class AlertScheduler:
    def __init__(self, db, notifier):
        self.db = db
        self.notifier = notifier
        self.running = False
        self.thread = None
        self.check_interval = 3600  # التحقق كل ساعة
    
    def start(self):
        """بدء جدولة المهام"""
        self.running = True
        self.thread = threading.Thread(target=self.monitor_cycles, daemon=True)
        self.thread.start()
    
    def stop(self):
        """إيقاف جدولة المهام"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def monitor_cycles(self):
        """مراقبة CYCLES وإرسال التنبيهات"""
        while self.running:
            try:
                current_cycle = self.db.get_current_cycle()
                if current_cycle:
                    days_remaining = self.db.get_days_remaining(current_cycle['cycle_number'])
                    
                    if days_remaining <= 13:
                        # إرسال تنبيه NEW CYCLE
                        self.send_new_cycle_alert(current_cycle, days_remaining)
                    
                    if days_remaining <= 3:
                        # تنبيه عاجل
                        self.send_urgent_alert(current_cycle, days_remaining)
                
                # انتظار الفاصل الزمني
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Error in monitor_cycles: {e}")
                time.sleep(60)  # انتظار دقيقة عند حدوث خطأ
    
    def send_new_cycle_alert(self, cycle, days_remaining):
        """إرسال تنبيه NEW CYCLE"""
        message = f"NEW CYCLE Alert!\n"
        message += f"Cycle {cycle['cycle_number']} has {days_remaining} days remaining\n"
        message += f"Effective until: {cycle['effective_date']}"
        
        self.notifier.send_notification("FMS Update Alert", message)
    
    def send_urgent_alert(self, cycle, days_remaining):
        """إرسال تنبيه عاجل"""
        message = f"URGENT: FMS Cycle Expiring Soon!\n"
        message += f"Only {days_remaining} days remaining for Cycle {cycle['cycle_number']}"
        
        self.notifier.send_notification("URGENT FMS Alert", message, urgent=True)