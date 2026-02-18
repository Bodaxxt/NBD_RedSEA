import requests
import os
import threading

# ================= إعدادات حسابك (تم التحديث ببياناتك) =================
USERNAME = 'abdallah213'
TOKEN = '3bd492a3e59ae217d32a52211854fcb3e8fd57fe'
DOMAIN = "www.pythonanywhere.com"

# المسار على السيرفر (أين سيتم وضع الملف في PythonAnywhere)
REMOTE_PATH = f"/home/{USERNAME}/fms_updates.db" 

# المسار على جهازك (تأكد أن الملف في هذا المجلد أو عدل المسار)
LOCAL_DB_PATH = "database/fms_updates.db" 
# ===================================================================

def upload_db_to_server():
    """دالة لرفع قاعدة البيانات للسيرفر"""
    print("⏳ Cloud Sync: Starting upload to PythonAnywhere...")
    
    # 1. التأكد من مكان الملف المحلي
    local_path = ""
    if os.path.exists(LOCAL_DB_PATH):
        local_path = LOCAL_DB_PATH
    elif os.path.exists("fms_updates.db"):
        local_path = "fms_updates.db"
    else:
        print("❌ Cloud Sync Error: fms_updates.db not found locally!")
        return

    # 2. تجهيز الرابط والـ Headers
    url = f"https://{DOMAIN}/api/v0/user/{USERNAME}/files/path{REMOTE_PATH}"
    headers = {'Authorization': f'Token {TOKEN}'}

    try:
        # 3. فتح الملف ورفعه (POST)
        with open(local_path, "rb") as f:
            response = requests.post(
                url,
                headers=headers,
                files={"content": f}
            )

        if response.status_code in [200, 201]:
            print("✅ Cloud Sync Success: Database is now live on server.")
        else:
            print(f"❌ Cloud Sync Failed: {response.status_code}")
            print(f"Details: {response.content}")
            
    except Exception as e:
        print(f"❌ Cloud Sync Connection Error: {str(e)}")

def start_sync():
    """تشغيل الرفع في الخلفية عشان البرنامج ميهنجش"""
    thread = threading.Thread(target=upload_db_to_server)
    thread.start()

if __name__ == "__main__":
    # تجربة الرفع فوراً عند تشغيل هذا الملف يدوياً
    upload_db_to_server()