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
        error_count = 0
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
                
                # إعادة تعيين عداد الأخطاء عند النجاح
                error_count = 0
                
                # انتظار الفاصل الزمني
                time.sleep(self.check_interval)
                
            except Exception as e:
                error_count += 1
                # طباعة الخطأ فقط كل 5 محاولات فاشلة لتجنب الرسائل المكررة
                if error_count % 5 == 1:
                    print(f"⚠️  Error in monitor_cycles (attempt {error_count}): {str(e)}")
                
                # زيادة وقت الانتظار مع كل محاولة فاشلة
                wait_time = min(60 * error_count, 300)  # الحد الأقصى 5 دقائق
                time.sleep(wait_time)
    
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