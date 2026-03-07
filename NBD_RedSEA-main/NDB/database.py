import sqlite3
import psycopg2
import os
from datetime import datetime

# ================= رابط قاعدة بيانات Neon (المصدر الرئيسي) =================
NEON_DB_URL = "postgresql://neondb_owner:npg_F4HVGvQlMP1i@ep-polished-butterfly-aifcwwrz-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

class DatabaseManager:
    def __init__(self, db_path="database/fms_updates.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.init_database()       # تجهيز الداتا بيز المحلية
        self.init_neon_database()  # التأكد إن جداول نيون جاهزة
        self.load_cycles_data()
        self.pull_from_neon()      # <--- سحب أحدث بيانات من نيون عند فتح البرنامج
    
    def _get_cursor(self):
        return self.conn.cursor()

    # =====================================================================
    # قسم المزامنة مع NEON DB
    # =====================================================================
    def init_neon_database(self):
        """التأكد من وجود جدول التحديثات في Neon DB"""
        try:
            conn = psycopg2.connect(NEON_DB_URL)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS updates (
                    id SERIAL PRIMARY KEY,
                    cycle_number VARCHAR(10),
                    engineer_name VARCHAR(100),
                    update_date VARCHAR(20),
                    update_time VARCHAR(20),
                    file_path TEXT,
                    notes TEXT,
                    aircraft_reg VARCHAR(20),
                    installed_on_aircraft INTEGER DEFAULT 0,
                    actual_install_datetime VARCHAR(50)
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Neon DB Init Warning: {e}")

    def pull_from_neon(self):
        """سحب البيانات من Neon وتحديث النسخة المحلية (عشان المهندس يشوف شغل زمايله)"""
        try:
            # 1. جلب البيانات من Neon
            neon_conn = psycopg2.connect(NEON_DB_URL)
            neon_cursor = neon_conn.cursor()
            neon_cursor.execute('SELECT cycle_number, engineer_name, update_date, update_time, file_path, notes, aircraft_reg, installed_on_aircraft, actual_install_datetime FROM updates')
            rows = neon_cursor.fetchall()
            neon_conn.close()

            # 2. تحديث الداتا بيز المحلية
            local_cursor = self._get_cursor()
            local_cursor.execute("DELETE FROM updates") # مسح القديم
            
            for row in rows:
                local_cursor.execute('''
                    INSERT INTO updates (cycle_number, engineer_name, update_date, update_time, file_path, notes, aircraft_reg, installed_on_aircraft, actual_install_datetime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', row)
            
            self.conn.commit()
            local_cursor.close()
            print("✅ Data successfully synced from Neon DB to Local!")
        except Exception as e:
            print(f"❌ Failed to pull from Neon DB: {e}")

    # =====================================================================
    # باقي الدوال (تم دمج الحفظ المزدوج فيها)
    # =====================================================================

    def get_cycle_date_range(self, cycle_number):
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT effective_date FROM cycles WHERE cycle_number = ?", (cycle_number,))
            res_start = cursor.fetchone()
            
            if not res_start:
                return None, None
            
            start_str = res_start[0]
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            
            cursor.execute("SELECT effective_date FROM cycles WHERE effective_date > ? ORDER BY effective_date ASC LIMIT 1", (start_str,))
            res_end = cursor.fetchone()
            
            if res_end:
                next_cycle_start_str = res_end[0]
                end_date = datetime.strptime(next_cycle_start_str, '%Y-%m-%d')
            else:
                from datetime import timedelta
                end_date = start_date + timedelta(days=28)
                
            return start_date, end_date
        except Exception as e:
            return None, None
        finally:
            cursor.close()

    def init_database(self):
        cursor = self._get_cursor()
        try:
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
        cycles_data =[
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
        today = datetime.now().strftime('%Y-%m-%d')
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT cycle_number, effective_date FROM cycles WHERE effective_date <= ? ORDER BY effective_date DESC LIMIT 1', (today,))
            result = cursor.fetchone()
            if result:
                active_cycle_num, active_date = result
                cursor.execute("UPDATE cycles SET status = 'active' WHERE cycle_number = ?", (active_cycle_num,))
                cursor.execute("UPDATE cycles SET status = 'expired' WHERE effective_date < ?", (active_date,))
                cursor.execute("UPDATE cycles SET status = 'upcoming' WHERE effective_date > ?", (active_date,))
                self.conn.commit()
        finally:
            cursor.close()

    def update_cycle_status_after_install(self, cycle_number):
        self.auto_update_statuses_by_date()

    def record_update(self, cycle_number, engineer_name, file_path, notes, aircraft_reg=None, update_datetime=None):
        if update_datetime:
            try:
                dt = datetime.strptime(update_datetime, '%Y-%m-%d %H:%M:%S')
                update_date, update_time = dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S')
            except:
                dt = datetime.now()
                update_date, update_time = dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S')
        else:
            dt = datetime.now()
            update_date, update_time = dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S')
        
        # 1. الحفظ في NEON DB أولاً (المصدر الرئيسي)
        try:
            neon_conn = psycopg2.connect(NEON_DB_URL)
            neon_cursor = neon_conn.cursor()
            neon_cursor.execute('''
                INSERT INTO updates (cycle_number, engineer_name, update_date, update_time, file_path, notes, aircraft_reg)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (cycle_number, engineer_name, update_date, update_time, file_path, notes, aircraft_reg))
            neon_conn.commit()
            neon_conn.close()
        except Exception as e:
            print(f"❌ Failed to save to Neon DB: {e}")

        # 2. الحفظ في Local SQLite
        cursor = self._get_cursor()
        try:
            cursor.execute('''
                INSERT INTO updates (cycle_number, engineer_name, update_date, update_time, file_path, notes, aircraft_reg)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cycle_number, engineer_name, update_date, update_time, file_path, notes, aircraft_reg))
            self.conn.commit()
            self.update_cycle_status_after_install(cycle_number)
            return cursor.lastrowid
        finally:
            cursor.close()

    def mark_update_installed_on_aircraft(self, update_id, actual_install_datetime=None):
        if not actual_install_datetime:
            actual_install_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = self._get_cursor()
        try:
            # نجيب السيكل ورقم الطيارة عشان نحدثهم في نيون
            cursor.execute("SELECT cycle_number, aircraft_reg FROM updates WHERE id = ?", (update_id,))
            res = cursor.fetchone()
            
            if res:
                cycle_num, ac_reg = res
                
                # 1. التحديث في Neon DB
                try:
                    neon_conn = psycopg2.connect(NEON_DB_URL)
                    neon_cursor = neon_conn.cursor()
                    neon_cursor.execute('''
                        UPDATE updates SET installed_on_aircraft = 1, actual_install_datetime = %s
                        WHERE cycle_number = %s AND aircraft_reg = %s
                    ''', (actual_install_datetime, cycle_num, ac_reg))
                    neon_conn.commit()
                    neon_conn.close()
                except Exception as e:
                    print(f"❌ Failed to update install status in Neon DB: {e}")

            # 2. التحديث في Local SQLite
            cursor.execute('''
                UPDATE updates SET installed_on_aircraft = 1, actual_install_datetime = ?
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
            
            final_results =[]
            for row in results:
                d = dict(zip(columns, row))
                d['is_recorded'] = d['cycle_number'] in recorded_cycles
                d['submission_status'] = "Done" if d['is_recorded'] else "Waiting"
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
            cursor.execute('SELECT * FROM cycles WHERE effective_date <= ? ORDER BY effective_date DESC LIMIT 1', (today,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
            return None
        finally:
            cursor.close()

    def get_active_cycle_data(self):
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT * FROM cycles WHERE status = 'active' LIMIT 1")
            result = cursor.fetchone()
            if result:
                columns =[desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
            return None
        finally:
            cursor.close()

    def get_upcoming_cycle_data(self):
        today = datetime.now().strftime('%Y-%m-%d')
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM cycles WHERE effective_date > ? ORDER BY effective_date ASC LIMIT 1', (today,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                cycle_data = dict(zip(columns, result))
                eff_date = datetime.strptime(cycle_data['effective_date'], "%Y-%m-%d")
                days_remaining = (eff_date - datetime.now()).days + 1
                return cycle_data, days_remaining
            return None, 0
        finally:
            cursor.close()

    def get_dashboard_data(self):
        self.pull_from_neon() # تحديث الواجهة بأحدث داتا عند كل ريفرش
        return self.get_upcoming_cycle_data()

    def get_update_history(self):
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM updates ORDER BY update_date DESC, update_time DESC')
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in results]
        finally:
            cursor.close()

    def get_days_remaining(self, cycle_number=None):
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
        if cycle_number is None:
            upcoming_cycle = self.get_upcoming_cycle_data()
            if upcoming_cycle[0]:
                cycle_number = upcoming_cycle[0]['cycle_number']
            else:
                return {}
        
        aircraft_list =['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
        aircraft_status = {}
        cursor = self._get_cursor()
        try:
            for aircraft in aircraft_list:
                cursor.execute('SELECT COUNT(*) FROM updates WHERE cycle_number = ? AND aircraft_reg = ?', (cycle_number, aircraft))
                result = cursor.fetchone()
                count = result[0] if result else 0
                aircraft_status[aircraft] = 'Updated' if count > 0 else 'Pending'
            return aircraft_status
        finally:
            cursor.close()

    def get_aircraft_installation_status(self, cycle_number=None):
        if cycle_number is None:
            active_cycle = self.get_active_cycle_data()
            if active_cycle:
                cycle_number = active_cycle['cycle_number']
            else:
                return {}
        
        aircraft_list =['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
        installation_status = {}
        cursor = self._get_cursor()
        try:
            for aircraft in aircraft_list:
                cursor.execute('SELECT installed_on_aircraft, actual_install_datetime FROM updates WHERE cycle_number = ? AND aircraft_reg = ? ORDER BY id DESC LIMIT 1', (cycle_number, aircraft))
                result = cursor.fetchone()
                if result:
                    installation_status[aircraft] = {'installed': bool(result[0]), 'datetime': result[1] if result[1] else 'N/A'}
                else:
                    installation_status[aircraft] = {'installed': False, 'datetime': 'N/A'}
            return installation_status
        finally:
            cursor.close()

    def get_aircraft_update_dates(self, cycle_number=None):
        if cycle_number is None:
            active_cycle = self.get_active_cycle_data()
            if active_cycle:
                cycle_number = active_cycle['cycle_number']
            else:
                return {}
        
        aircraft_list =['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
        update_dates = {}
        cursor = self._get_cursor()
        try:
            for aircraft in aircraft_list:
                cursor.execute('SELECT update_date, update_time, actual_install_datetime FROM updates WHERE cycle_number = ? AND aircraft_reg = ? ORDER BY id DESC LIMIT 1', (cycle_number, aircraft))
                result = cursor.fetchone()
                if result:
                    update_dates[aircraft] = {'engineer_date': f"{result[0]} {result[1]}" if result[1] else result[0], 'installation_date': result[2] if result[2] else 'N/A'}
                else:
                    update_dates[aircraft] = {'engineer_date': 'N/A', 'installation_date': 'N/A'}
            return update_dates
        finally:
            cursor.close()