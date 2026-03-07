import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

# ================= إعدادات الإيميل =================
# إيميل البوت (المرسل)
SENDER_EMAIL = "abdallahtarboo2005@gmail.com"
SENDER_PASSWORD = "eytp vogu pzow ilfr" 

# اسم ملف الإيميلات
EMAILS_FILE = "emails.txt"

# ================= جدول المواعيد =================
CYCLES_DATA = [
    ('2501', '2025-01-23'), ('2502', '2025-02-20'), ('2503', '2025-03-20'),
    ('2504', '2025-04-17'), ('2505', '2025-05-15'), ('2506', '2025-06-12'),
    ('2507', '2025-07-10'), ('2508', '2025-08-07'), ('2509', '2025-09-04'),
    ('2510', '2025-10-02'), ('2511', '2025-10-30'), ('2512', '2025-11-27'),
    ('2513', '2025-12-25'), ('2601', '2026-01-22'), ('2602', '2026-02-19'),
    ('2603', '2026-03-19'), ('2604', '2026-04-16'), ('2605', '2026-05-14'),
    ('2606', '2026-06-11'), ('2607', '2026-07-09'), ('2608', '2026-08-06'),
    ('2609', '2026-09-03'), ('2610', '2026-10-01'), ('2611', '2026-10-29'),
    ('2612', '2026-11-26'), ('2613', '2026-12-24')
]

def get_recipients():
    """قراءة الإيميلات من ملف خارجي"""
    email_list = []
    # التأكد من مسار الملف الصحيح على السيرفر
    file_path = os.path.join(os.path.dirname(__file__), EMAILS_FILE)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # قراءة السطور وتنظيف المسافات الزائدة
            lines = f.readlines()
            for line in lines:
                email = line.strip()
                if email and '@' in email: # تأكد إنه إيميل ومش سطر فاضي
                    email_list.append(email)
        return email_list
    except FileNotFoundError:
        print(f"⚠️ Warning: Could not find {EMAILS_FILE}")
        return []

def send_email_alert(recipient_email, cycle_number, days_remaining, effective_date):
    """دالة إرسال الإيميل لشخص واحد"""
    subject = f"🚨 FMS Alert: Cycle {cycle_number} ({days_remaining} Days Left)"
    
    body = f"""
    Red Sea Airlines - FMS Update Reminder
    --------------------------------------
    
    Target Cycle: {cycle_number}
    Effective Date: {effective_date}
    
    ⚠️ DAYS REMAINING: {days_remaining}
    
    Please confirm update status.
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, recipient_email, text)
        server.quit()
        print(f"✅ Sent to: {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send to {recipient_email}: {str(e)}")
        return False

def check_cycles():
    """فحص المواعيد"""
    print(f"--- Starting Check at {datetime.now()} ---")
    today = datetime.now().date()
    
    # 1. تحديد الدورة القادمة
    upcoming_cycles = []
    for cycle_num, eff_date_str in CYCLES_DATA:
        eff_date = datetime.strptime(eff_date_str, '%Y-%m-%d').date()
        if eff_date > today:
            upcoming_cycles.append((cycle_num, eff_date))
    
    if not upcoming_cycles:
        print("No upcoming cycles.")
        return

    next_cycle_num, next_cycle_date = upcoming_cycles[0]
    days_remaining = (next_cycle_date - today).days
    
    print(f"Cycle: {next_cycle_num}, Days Left: {days_remaining}")

    # 2. قرار الإرسال
    if 0 <= days_remaining <= 13:
        print("⚡ Alert Condition Met! Sending emails...")
        
        # 3. جلب قائمة المهندسين
        recipients = get_recipients()
        
        if not recipients:
            print("❌ No emails found in emails.txt!")
            return

        # 4. التكرار (Loop) عشان يبعت لكل واحد
        count = 0
        for email in recipients:
            success = send_email_alert(email, next_cycle_num, days_remaining, next_cycle_date)
            if success:
                count += 1
        
        print(f"--- Finished. Sent {count} emails. ---")
    else:
        print("No alerts needed today.")

if __name__ == "__main__":
    check_cycles()