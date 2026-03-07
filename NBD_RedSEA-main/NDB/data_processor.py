import pandas as pd
from datetime import datetime, timedelta

class DataProcessor:
    def __init__(self):
        # بيانات CYCLES الكاملة من ملف PDF
        self.cycles_data = self.load_full_cycles_data()
    
    def load_full_cycles_data(self):
        """تحميل بيانات CYCLES كاملة"""
        cycles = []
        
        # بيانات 2025
        cycles_2025 = [
            # Format: (cycle_num, co_routes, honeywell, shipping, db_ship, effective)
            ('2501', '2024-12-27', '2025-01-06', '2025-01-13', '2025-01-15', '2025-01-23'),
            ('2502', '2025-01-24', '2025-02-03', '2025-02-10', '2025-02-12', '2025-02-20'),
            ('2503', '2025-02-21', '2025-03-03', '2025-03-10', '2025-03-12', '2025-03-20'),
            ('2504', '2025-03-21', '2025-03-31', '2025-04-07', '2025-04-09', '2025-04-17'),
            ('2505', '2025-04-18', '2025-04-28', '2025-05-05', '2025-05-07', '2025-05-15'),
            ('2506', '2025-05-16', '2025-05-26', '2025-06-02', '2025-06-04', '2025-06-12'),
            ('2507', '2025-06-13', '2025-06-23', '2025-06-30', '2025-07-02', '2025-07-10'),
            ('2508', '2025-07-11', '2025-07-21', '2025-07-28', '2025-07-30', '2025-08-07'),
            ('2509', '2025-08-08', '2025-08-18', '2025-08-25', '2025-08-27', '2025-09-04'),
            ('2510', '2025-09-05', '2025-09-15', '2025-09-22', '2025-09-24', '2025-10-02'),
            ('2511', '2025-10-03', '2025-10-13', '2025-10-20', '2025-10-22', '2025-10-30'),
            ('2512', '2025-10-31', '2025-11-10', '2025-11-17', '2025-11-19', '2025-11-27'),
            ('2513', '2025-11-28', '2025-12-08', '2025-12-15', '2025-12-17', '2025-12-25'),
        ]
        
        # بيانات 2026
        cycles_2026 = [
            ('2601', '2025-12-26', '2026-01-05', '2026-01-12', '2026-01-14', '2026-01-22'),
            ('2602', '2026-01-23', '2026-02-02', '2026-02-09', '2026-02-11', '2026-02-19'),
            ('2603', '2026-02-20', '2026-03-02', '2026-03-09', '2026-03-11', '2026-03-19'),
            ('2604', '2026-03-20', '2026-03-30', '2026-04-06', '2026-04-08', '2026-04-16'),
            ('2605', '2026-04-17', '2026-04-27', '2026-05-04', '2026-05-06', '2026-05-14'),
            ('2606', '2026-05-15', '2026-05-25', '2026-06-01', '2026-06-03', '2026-06-11'),
            ('2607', '2026-06-12', '2026-06-22', '2026-06-29', '2026-07-01', '2026-07-09'),
            ('2608', '2026-07-10', '2026-07-20', '2026-07-27', '2026-07-29', '2026-08-06'),
            ('2609', '2026-08-07', '2026-08-17', '2026-08-24', '2026-08-26', '2026-09-03'),
            ('2610', '2026-09-04', '2026-09-14', '2026-09-21', '2026-09-23', '2026-10-01'),
            ('2611', '2026-10-02', '2026-10-12', '2026-10-19', '2026-10-21', '2026-10-29'),
            ('2612', '2026-10-30', '2026-11-09', '2026-11-16', '2026-11-18', '2026-11-26'),
            ('2613', '2026-11-27', '2026-12-07', '2026-12-14', '2026-12-16', '2026-12-24'),
        ]
        
        all_cycles = cycles_2025 + cycles_2026
        
        for cycle in all_cycles:
            cycles.append({
                'cycle_number': cycle[0],
                'co_routes_date': cycle[1],
                'honeywell_date': cycle[2],
                'shipping_date': cycle[3],
                'database_ship_date': cycle[4],
                'effective_date': cycle[5],
                'status': 'upcoming'
            })
        
        return cycles
    
    def get_cycle_info(self, cycle_number):
        """الحصول على معلومات CYCLE محدد"""
        for cycle in self.cycles_data:
            if cycle['cycle_number'] == cycle_number:
                return cycle
        return None
    
    def get_current_cycle(self):
        """الحصول على CYCLE الحالي"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        for cycle in self.cycles_data:
            if cycle['effective_date'] <= today:
                current_cycle = cycle
        
        # البحث عن آخر CYCLE فعال
        current_cycle = None
        for cycle in self.cycles_data:
            if cycle['effective_date'] <= today:
                current_cycle = cycle
            else:
                break
        
        return current_cycle
    
    def calculate_days_remaining(self, cycle_number):
        """حساب الأيام المتبقية لـ CYCLE"""
        cycle = self.get_cycle_info(cycle_number)
        if not cycle:
            return None
        
        effective_date = datetime.strptime(cycle['effective_date'], '%Y-%m-%d')
        next_cycle_date = effective_date + timedelta(days=28)
        
        days_remaining = (next_cycle_date - datetime.now()).days
        return max(0, days_remaining)
    
    def get_upcoming_cycles(self, count=5):
        """الحصول على CYCLES القادمة"""
        today = datetime.now().strftime('%Y-%m-%d')
        upcoming = []
        
        for cycle in self.cycles_data:
            if cycle['effective_date'] > today:
                upcoming.append(cycle)
                if len(upcoming) >= count:
                    break
        
        return upcoming
    
    def export_to_csv(self, filepath="cycles_export.csv"):
        """تصدير البيانات إلى CSV"""
        df = pd.DataFrame(self.cycles_data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        return filepath