import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="database/fms_updates.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.init_database()
        self.load_cycles_data()
    
    def _get_cursor(self):
        return self.conn.cursor()

    def init_database(self):
        cursor = self._get_cursor()
        try:
            # إصلاح الجدول إذا كان ناقصاً
            cursor.execute("PRAGMA table_info(cycles)")
            columns_info = cursor.fetchall()
            existing_columns = [info[1] for info in columns_info]
            required_columns = ['cycle_number', 'effective_date', 'status']
            
            if existing_columns and any(col not in existing_columns for col in required_columns):
                cursor.execute("DROP TABLE IF EXISTS cycles")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number TEXT UNIQUE,
                    effective_date TEXT,
                    status TEXT DEFAULT 'upcoming'
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number TEXT,
                    engineer_name TEXT,
                    update_date TEXT,
                    update_time TEXT,
                    file_path TEXT,
                    notes TEXT,
                    aircraft_reg TEXT,
                    installed_on_aircraft INTEGER DEFAULT 0,
                    actual_install_datetime TEXT
                )
            ''')
            self.conn.commit()
        finally:
            cursor.close()
    
    def load_cycles_data(self):
        cycles_data = [
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
        cursor = self._get_cursor()
        try:
            for cycle_num, eff_date in cycles_data:
                cursor.execute('''
                    INSERT OR IGNORE INTO cycles 
                    (cycle_number, effective_date, status)
                    VALUES (?, ?, 'upcoming')
                ''', (cycle_num, eff_date))
            self.conn.commit()
        finally:
            cursor.close()

    def auto_update_statuses_by_date(self):
        """تحديث الحالات بناءً على التاريخ فقط"""
        today = datetime.now().strftime('%Y-%m-%d')
        cursor = self._get_cursor()
        try:
            cursor.execute('''
                SELECT cycle_number, effective_date FROM cycles 
                WHERE effective_date <= ? 
                ORDER BY effective_date DESC 
                LIMIT 1
            ''', (today,))
            
            result = cursor.fetchone()
            
            if result:
                active_cycle_num = result[0]
                active_date = result[1]
                
                cursor.execute("UPDATE cycles SET status = 'active' WHERE cycle_number = ?", (active_cycle_num,))
                cursor.execute("UPDATE cycles SET status = 'expired' WHERE effective_date < ?", (active_date,))
                cursor.execute("UPDATE cycles SET status = 'upcoming' WHERE effective_date > ?", (active_date,))
                self.conn.commit()
        finally:
            cursor.close()

    # === (الدالة التي سببت المشكلة تمت إعادتها بشكل آمن) ===
    def update_cycle_status_after_install(self, cycle_number):
        """
        هذه الدالة تمنع حدوث الخطأ (Error) عند الحفظ.
        بدلاً من تغيير الحالة يدوياً، تقوم بتأكيد التواريخ فقط.
        """
        self.auto_update_statuses_by_date()
    # =======================================================

    def record_update(self, cycle_number, engineer_name, file_path, notes, aircraft_reg=None, update_datetime=None):
        # إذا لم يتم تمرير تاريخ ووقت، استخدم الوقت الحالي
        if update_datetime:
            try:
                # محاولة تحويل النص إلى datetime
                from datetime import datetime
                dt = datetime.strptime(update_datetime, '%Y-%m-%d %H:%M:%S')
                update_date = dt.strftime('%Y-%m-%d')
                update_time = dt.strftime('%H:%M:%S')
            except:
                # إذا فشل التحويل، استخدم الوقت الحالي
                current_time = datetime.now()
                update_date = current_time.strftime('%Y-%m-%d')
                update_time = current_time.strftime('%H:%M:%S')
        else:
            current_time = datetime.now()
            update_date = current_time.strftime('%Y-%m-%d')
            update_time = current_time.strftime('%H:%M:%S')
        
        cursor = self._get_cursor()
        try:
            cursor.execute('''
                INSERT INTO updates (cycle_number, engineer_name, update_date, update_time, file_path, notes, aircraft_reg)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cycle_number, engineer_name, update_date, update_time, file_path, notes, aircraft_reg))
            self.conn.commit()
            
            # نستدعي دالة الأمان عشان الـ GUI ميزعلش
            self.update_cycle_status_after_install(cycle_number)
            return cursor.lastrowid
        finally:
            cursor.close()

    def mark_update_installed_on_aircraft(self, update_id, actual_install_datetime=None):
        """تحديث حالة التحديث للإشارة إلى أنه تم تثبيته على الطيارة"""
        if not actual_install_datetime:
            actual_install_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = self._get_cursor()
        try:
            cursor.execute('''
                UPDATE updates 
                SET installed_on_aircraft = 1, actual_install_datetime = ?
                WHERE id = ?
            ''', (actual_install_datetime, update_id))
            self.conn.commit()
        finally:
            cursor.close()

    def get_all_cycles(self):
        self.auto_update_statuses_by_date()
        
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM cycles ORDER BY effective_date')
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            cursor.execute('SELECT cycle_number FROM updates')
            recorded_cycles = {row[0] for row in cursor.fetchall()}
            
            final_results = []
            
            for row in results:
                d = dict(zip(columns, row))
                d['is_recorded'] = d['cycle_number'] in recorded_cycles
                
                # إضافة حالة الانتظار للعرض فقط دون تغيير حالة الدورة الأصلية
                if not d['is_recorded']:
                    d['submission_status'] = "Waiting"
                else:
                    d['submission_status'] = "Done"
                
                d['co_routes_date'] = d['effective_date']
                d['honeywell_date'] = d['effective_date']
                d['shipping_date'] = d['effective_date']
                d['database_ship_date'] = d['effective_date']
                
                final_results.append(d)
                
            return final_results
        finally:
            cursor.close()

    def get_current_cycle(self):
        today = datetime.now().strftime('%Y-%m-%d')
        cursor = self._get_cursor()
        try:
            cursor.execute('''
                SELECT * FROM cycles 
                WHERE effective_date <= ? 
                ORDER BY effective_date DESC 
                LIMIT 1
            ''', (today,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
            return None
        finally:
            cursor.close()

    def get_dashboard_data(self):
        today = datetime.now().strftime('%Y-%m-%d')
        cursor = self._get_cursor()
        try:
            cursor.execute('''
                SELECT * FROM cycles 
                WHERE effective_date > ? 
                ORDER BY effective_date ASC 
                LIMIT 1
            ''', (today,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                cycle_dict = dict(zip(columns, result))
                eff_date = datetime.strptime(cycle_dict['effective_date'], '%Y-%m-%d')
                days_remaining = (eff_date - datetime.now()).days + 1
                return cycle_dict, days_remaining
            return None, None
        finally:
            cursor.close()

    def get_update_history(self):
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM updates ORDER BY update_date DESC, update_time DESC')
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in results]
        finally:
            cursor.close()
    # مثال لما يجب أن تكون عليه الدوال في database.py

    # ... (بعد دالة get_update_history مباشرة) ...

    def get_active_cycle_data(self):
        """جلب بيانات الدورة الفعالة حالياً"""
        cursor = self._get_cursor()
        try:
            # نبحث عن الدورة التي حالتها active (لاحظ الحروف صغيرة كما في دالة التحديث التلقائي)
            cursor.execute("SELECT * FROM cycles WHERE status = 'active' LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
            return None
        except Exception as e:
            print(f"Error getting active cycle: {e}")
            return None
        finally:
            cursor.close()

    def get_upcoming_cycle_data(self):
        """جلب الدورة القادمة وحساب الأيام المتبقية"""
        today = datetime.now().strftime('%Y-%m-%d')
        cursor = self._get_cursor()
        try:
            cursor.execute('''
                SELECT * FROM cycles 
                WHERE effective_date > ? 
                ORDER BY effective_date ASC 
                LIMIT 1
            ''', (today,))
            
            result = cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in cursor.description]
                cycle_data = dict(zip(columns, result))
                
                # حساب الأيام المتبقية
                eff_date = datetime.strptime(cycle_data['effective_date'], "%Y-%m-%d")
                current_date = datetime.now()
                # نضيف 1 لتقريب الأيام بشكل صحيح
                days_remaining = (eff_date - current_date).days + 1
                
                return cycle_data, days_remaining
            return None, 0
        except Exception as e:
            print(f"Error getting upcoming cycle: {e}")
            return None, 0
        finally:
            cursor.close()

    def get_days_remaining(self, cycle_number=None):
        """
        تم تعديلها لتقبل cycle_number لأن الـ Scheduler يرسلها.
        نقوم بتجاهل الرقم المرسل ونحسب الأيام للدورة القادمة فعلياً.
        """
        _, days = self.get_upcoming_cycle_data()
        return days

    def check_if_update_recorded(self, cycle_number):
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT id FROM updates WHERE cycle_number = ?', (cycle_number,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def get_aircraft_status(self, cycle_number=None):
        """
        جلب حالة الطيارات الأربع (SU-RSA, SU-RSB, SU-RSC, SU-RSD)
        إذا لم يتم تحديد دورة، نبحث عن الدورة الحالية
        """
        if cycle_number is None:
            active_cycle = self.get_active_cycle_data()
            if active_cycle:
                cycle_number = active_cycle['cycle_number']
            else:
                return {}
        
        aircraft_list = ['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
        aircraft_status = {}
        
        cursor = self._get_cursor()
        try:
            for aircraft in aircraft_list:
                cursor.execute('''
                    SELECT COUNT(*) FROM updates 
                    WHERE cycle_number = ? AND aircraft_reg = ?
                ''', (cycle_number, aircraft))
                
                result = cursor.fetchone()
                count = result[0] if result else 0
                
                # إذا كان هناك تسجيل = Updated، وإلا = Pending
                aircraft_status[aircraft] = 'Updated' if count > 0 else 'Pending'
            
            return aircraft_status
        finally:
            cursor.close()

    def get_aircraft_installation_status(self, cycle_number=None):
        """
        جلب حالة التثبيت الفعلي على الطيارات (installed_on_aircraft)
        يرجع قاموس بـ {aircraft: {'installed': bool, 'datetime': str}}
        """
        if cycle_number is None:
            active_cycle = self.get_active_cycle_data()
            if active_cycle:
                cycle_number = active_cycle['cycle_number']
            else:
                return {}
        
        aircraft_list = ['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
        installation_status = {}
        
        cursor = self._get_cursor()
        try:
            for aircraft in aircraft_list:
                cursor.execute('''
                    SELECT installed_on_aircraft, actual_install_datetime FROM updates 
                    WHERE cycle_number = ? AND aircraft_reg = ?
                    ORDER BY id DESC LIMIT 1
                ''', (cycle_number, aircraft))
                
                result = cursor.fetchone()
                if result:
                    is_installed = bool(result[0])
                    install_datetime = result[1] if result[1] else 'N/A'
                    installation_status[aircraft] = {
                        'installed': is_installed,
                        'datetime': install_datetime
                    }
                else:
                    installation_status[aircraft] = {
                        'installed': False,
                        'datetime': 'N/A'
                    }
            
            return installation_status
        finally:
            cursor.close()

    def get_aircraft_update_dates(self, cycle_number=None):
        """
        جلب تواريخ تحديثات المهندس والطيارات لكل طيارة
        يرجع قاموس بـ {aircraft: {'engineer_date': str, 'installation_date': str}}
        """
        if cycle_number is None:
            active_cycle = self.get_active_cycle_data()
            if active_cycle:
                cycle_number = active_cycle['cycle_number']
            else:
                return {}
        
        aircraft_list = ['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
        update_dates = {}
        
        cursor = self._get_cursor()
        try:
            for aircraft in aircraft_list:
                cursor.execute('''
                    SELECT update_date, update_time, actual_install_datetime 
                    FROM updates 
                    WHERE cycle_number = ? AND aircraft_reg = ?
                    ORDER BY id DESC LIMIT 1
                ''', (cycle_number, aircraft))
                
                result = cursor.fetchone()
                if result:
                    engineer_date = f"{result[0]} {result[1]}" if result[1] else result[0]
                    installation_date = result[2] if result[2] else 'N/A'
                    update_dates[aircraft] = {
                        'engineer_date': engineer_date,
                        'installation_date': installation_date
                    }
                else:
                    update_dates[aircraft] = {
                        'engineer_date': 'N/A',
                        'installation_date': 'N/A'
                    }
            
            return update_dates
        finally:
            cursor.close()
