import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk 
from datetime import datetime
import sync_cloud
class MainApplication:
    def __init__(self, root, db, notifier, scheduler):
        self.root = root
        self.db = db
        self.notifier = notifier
        self.scheduler = scheduler
        
        # إعدادات النافذة الرئيسية لتكون ملء الشاشة أو كبيرة
        self.root.geometry("1200x800")
        self.root.title("Red Sea Airlines | FMS Manager")
        
        self.setup_styles()
        self.create_main_frame()
        
        # تحديث بيانات الـ Dashboard عند البدء
        self.root.after(500, self.refresh_dashboard_data)
    def validate_date_within_cycle(self, date_str, cycle_number):
        """
        التحقق من التاريخ:
        يسمح للمهندس بتسجيل التحديث الجديد خلال فترة الدورة الحالية (التحضير)
        أو خلال فترة الدورة الجديدة نفسها.
        """
        try:
            input_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            
            # 1. نجيب تاريخ بداية ونهاية السايكل اللي بنسجلها (مثلاً 2602)
            target_start, target_end = self.db.get_cycle_date_range(cycle_number)
            
            if not target_start or not target_end:
                return True

            # 2. نجيب تاريخ بداية السايكل "الحالية" الشغالة دلوقت (مثلاً 2601)
            # عشان نسمح للمهندس يشتغل فيها
            active_cycle = self.db.get_active_cycle_data()
            
            if active_cycle:
                # لو فيه سايكل شغالة، يبقى بداية السماحية هي بداية السايكل الحالية
                current_active_start_str = active_cycle['effective_date']
                lower_bound = datetime.strptime(current_active_start_str, '%Y-%m-%d')
            else:
                # لو مفيش سايكل شغالة، يبقى السماحية تبدأ من السايكل الجديدة وخلاص
                lower_bound = target_start
            
            # الحد الأقصى هو نهاية السايكل الجديدة
            upper_bound = target_end
            
            # 3. الشرط المعدل:
            # التاريخ مقبول لو كان: (أكبر من بداية الحالية) و (أصغر من نهاية الجديدة)
            if lower_bound <= input_date < upper_bound:
                return True
            else:
                # رسالة الخطأ توضح النطاق الجديد
                return False, lower_bound.strftime('%Y-%m-%d'), upper_bound.strftime('%Y-%m-%d')
                
        except ValueError:
            messagebox.showerror("Error", "Date format must be: YYYY-MM-DD HH:MM:SS")
            return None
    
    def setup_styles(self):
        """تكوين الأنماط والألوان - النسخة الاحترافية"""
        self.style = ttk.Style()
        
        # استخدام ثيم 'clam' كقاعدة لأنه يقبل التخصيص اللوني بشكل أفضل
        self.style.theme_use('clam')
        
        # لوحة الألوان المحسنة
        self.colors = {
            'primary': '#003366',      # أزرق نيلي (الرئيسي)
            'secondary': '#C8102E',    # أحمر (لإجراءات الخطر أو التنبيه)
            'accent': '#FFD700',       # ذهبي (للأيقونات)
            'bg_main': '#F0F2F5',      # رمادي فاتح جداً للخلفية (SaaS Style)
            'bg_card': '#FFFFFF',      # أبيض للكروت
            'text_main': '#2C3E50',    # كحلي غامق للنصوص
            'text_light': '#7F8C8D',   # رمادي للنصوص الفرعية
            'success': '#27AE60',      # أخضر حيوي
            'warning': '#F39C12',      # برتقالي
            'danger': '#E74C3C'        # أحمر فاتح
        }
        
        # --- تكوين الإطارات (Frames) ---
        self.style.configure('Main.TFrame', background=self.colors['bg_main'])
        self.style.configure('Card.TFrame', background=self.colors['bg_card'], relief='flat')
        self.style.configure('Header.TFrame', background=self.colors['primary'])
        self.style.configure('Nav.TFrame', background=self.colors['bg_card'])
        
        # --- النصوص (Labels) ---
        # عناوين الكروت
        self.style.configure('CardTitle.TLabel', 
                           background=self.colors['bg_card'], 
                           foreground=self.colors['text_main'],
                           font=('Segoe UI', 12, 'bold'))
        
        # النصوص العادية داخل الكروت
        self.style.configure('CardBody.TLabel', 
                           background=self.colors['bg_card'], 
                           foreground=self.colors['text_main'],
                           font=('Segoe UI', 10))
        
        # العنوان الرئيسي في الهيدر
        self.style.configure('HeaderTitle.TLabel', 
                           background=self.colors['primary'], 
                           foreground='white',
                           font=('Segoe UI', 18, 'bold'))

        # --- الأزرار (Buttons) ---
        # زر عادي
        self.style.configure('TButton', 
                           font=('Segoe UI', 10), 
                           borderwidth=0, 
                           focuscolor='none',
                           padding=6)
        
        # زر الإجراء الرئيسي (Primary Action) - أحمر
        self.style.configure('RedSea.TButton', 
                           background=self.colors['secondary'],
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('RedSea.TButton', 
                      background=[('active', '#A00D24')]) # لون أغمق عند الضغط

        # زر التنقل (Nav Button)
        self.style.configure('Nav.TButton',
                           background=self.colors['bg_card'],
                           foreground=self.colors['primary'],
                           font=('Segoe UI', 11, 'bold'),
                           anchor='center')
        self.style.map('Nav.TButton',
                      background=[('active', self.colors['bg_main'])],
                      foreground=[('active', self.colors['secondary'])])

        # --- الجداول (Treeview) ---
        self.style.configure("Treeview",
                           background="white",
                           foreground=self.colors['text_main'],
                           rowheight=35,
                           fieldbackground="white",
                           font=('Segoe UI', 10),
                           borderwidth=0)
        
        self.style.configure("Treeview.Heading",
                           background=self.colors['bg_main'],
                           foreground=self.colors['primary'],
                           font=('Segoe UI', 10, 'bold'),
                           relief="flat")
        
        self.style.map("Treeview", background=[('selected', self.colors['primary'])])

        # --- شريط التقدم (Progress Bar) ---
        self.style.configure("Horizontal.TProgressbar",
                           troughcolor=self.colors['bg_main'],
                           background=self.colors['success'],
                           thickness=20)

    def create_main_frame(self):
        """إنشاء الإطار الرئيسي بتصميم محسن"""
        # الحاوية الرئيسية بلون الخلفية الرمادي الفاتح
        main_bg = ttk.Frame(self.root, style='Main.TFrame')
        main_bg.pack(fill='both', expand=True)

        self.create_header(main_bg)
        
        # منطقة المحتوى (Notebook)
        content_frame = ttk.Frame(main_bg, style='Main.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.create_main_content(content_frame)
        self.create_navigation(main_bg)
        
    def create_header(self, parent):
        """إنشاء رأس الصفحة مع الشعار المحسن"""
        header_frame = ttk.Frame(parent, style='Header.TFrame', height=90)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        inner_header = ttk.Frame(header_frame, style='Header.TFrame')
        inner_header.pack(fill='both', expand=True, padx=30)

        # العنوان (جهة اليسار)
        title_label = ttk.Label(
            inner_header, 
            text="✈️  RED SEA AIRLINES | FMS NAV MANAGER",
            style='HeaderTitle.TLabel'
        )
        title_label.pack(side='left', pady=20)
        
        # --- اللوجو المحسن (جهة اليمين) ---
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "images.png")
            
            if os.path.exists(image_path):
                pil_image = Image.open(image_path)
                
                # ✅ تحسينات:
                # 1. تحديد الحجم المناسب (أكبر قليلاً لرؤية أفضل)
                pil_image = pil_image.resize((120, 80), Image.Resampling.LANCZOS)
                
                # 2. إضافة خلفية بيضاء إذا كانت الصورة بخلفية شفافة
                # (اختياري - لكن يحسن المظهر)
                if pil_image.mode == 'RGBA':
                    # إنشاء صورة بيضاء كخلفية
                    background = Image.new('RGB', pil_image.size, (0, 51, 102))  # الأزرق الداكن
                    background.paste(pil_image, mask=pil_image.split()[3] if len(pil_image.split()) > 3 else None)
                    pil_image = background
                
                # 3. تحويلها إلى صورة tkinter
                self.logo_image = ImageTk.PhotoImage(pil_image)
                
                # 4. عرض الصورة
                logo_label = ttk.Label(
                    inner_header,
                    image=self.logo_image,
                    background=self.colors['primary']
                )
                logo_label.pack(side='right', pady=15, padx=10)
            else:
                raise FileNotFoundError("Couldn't find images.png")
                
        except Exception as e:
            print(f"⚠️ Logo Loading Error: {e}")
            # بديل نصي احترافي
            logo_label = ttk.Label(
                inner_header,
                text="🌊 RED SEA AIRLINES",
                font=('Segoe UI', 14, 'bold'),
                background=self.colors['primary'],
                foreground='white'
            )
            logo_label.pack(side='right', pady=20, padx=20)
            
    def create_logo_placeholder(self, parent_frame):
        pass # تم دمجها في الهيدر لتبسيط التصميم

    def create_main_content(self, parent):
        """إنشاء المحتوى الرئيسي مع تخصيص التبويبات"""
        # تخصيص شكل التبويبات
        self.style.configure('TNotebook', background=self.colors['bg_main'], borderwidth=0)
        self.style.configure('TNotebook.Tab', 
                           padding=[20, 10], 
                           font=('Segoe UI', 10),
                           background=self.colors['bg_main'])
        self.style.map('TNotebook.Tab', 
                      background=[('selected', self.colors['primary'])],
                      foreground=[('selected', 'white')])

        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        
        # إضافة الصفحات
        self.create_dashboard_tab()
        self.create_cycles_table_tab()
        self.create_update_registration_tab()
        self.create_installation_confirmation_tab()
        self.create_history_tab()
        
    def create_dashboard_tab(self):
            dashboard_bg = ttk.Frame(self.notebook, style='Main.TFrame')
            self.notebook.add(dashboard_bg, text="📊 DASHBOARD")
            
            # 1. إطار للزرار في الأعلى (عشان مياخدش مكان التايم لاين)
            top_bar = ttk.Frame(dashboard_bg, style='Main.TFrame')
            top_bar.pack(fill='x', padx=10, pady=5)
            
            sync_btn = ttk.Button(
                top_bar,
                text="🔄 Sync with Cloud",
                command=self.manual_sync,
                style='RedSea.TButton'
            )
            sync_btn.pack(side='right') # الزرار في اليمين فوق

            # 2. إطار البطاقات (الرئيسي)
            cards_container = ttk.Frame(dashboard_bg, style='Main.TFrame')
            cards_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            # --- باقي كود البطاقات (top_row و card2) هنا بنفس الترتيب ---
            top_row = ttk.Frame(cards_container, style='Main.TFrame')
            top_row.pack(fill='both', expand=False, pady=10)
            
            # --- البطاقة الأولى: الدورة الحالية (Active Cycle) ---
            card1 = ttk.Frame(top_row, style='Card.TFrame', padding=20)
            card1.pack(side='left', fill='both', expand=True, padx=(0, 10))
            
            ttk.Label(card1, text="CURRENT ACTIVE CYCLE", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 10))
            ttk.Separator(card1, orient='horizontal').pack(fill='x', pady=8)
            
            # تعريف المتغيرات التي يحتاجها الكود الجديد
            self.lbl_active_cycle = ttk.Label(
                card1,
                text="Loading...",
                font=('Segoe UI', 20, 'bold'),
                style='CardBody.TLabel',
                justify='center',
                foreground=self.colors['primary']
            )
            self.lbl_active_cycle.pack(pady=10)

            self.lbl_active_date = ttk.Label(
                card1, 
                text="--", 
                font=('Segoe UI', 10),
                style='CardBody.TLabel'
            )
            self.lbl_active_date.pack(pady=5)

            # حالة التسجيل (نستخدم tk.Label للتحكم الأسهل في الألوان)
            self.lbl_status = tk.Label(
                card1, 
                text="Checking Status...", 
                font=('Segoe UI', 10, 'bold'),
                bg='white',
                fg='gray',
                padx=15,
                pady=8
            )
            
            # --- البطاقة الثالثة: حالة الطيارات (Aircraft Status) مربوطة بالدورة القادمة ---
            card3 = ttk.Frame(top_row, style='Card.TFrame', padding=20)
            card3.pack(side='left', fill='both', expand=True, padx=(10, 0))
            
            ttk.Label(card3, text="✈️ AIRCRAFT STATUS (UPCOMING CYCLE)", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 10))
            ttk.Separator(card3, orient='horizontal').pack(fill='x', pady=8)
            
            # إنشاء إطار للطيارات مع حالاتها (مربوط بالدورة القادمة UPCOMING)
            aircraft_status_frame = ttk.Frame(card3, style='Card.TFrame')
            aircraft_status_frame.pack(fill='x', pady=10)
            
            self.aircraft_status_labels = {}  # حالات الطيارات للدورة القادمة (UPCOMING)
            self.aircraft_engineer_date_labels = {}  # تاريخ تحديث المهندس
            self.aircraft_installation_date_labels = {}  # تاريخ تحديث الطيارة
            aircraft_list = ['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
            
            for aircraft in aircraft_list:
                # إطار منفصل لكل طيارة (أفقي)
                ac_frame = ttk.Frame(aircraft_status_frame, style='Card.TFrame')
                ac_frame.pack(fill='x', pady=6)
                
                # اسم الطيارة
                ttk.Label(
                    ac_frame,
                    text=f"🛩️ {aircraft}",
                    font=('Segoe UI', 10, 'bold'),
                    style='CardBody.TLabel',
                    width=12
                ).pack(side='left', padx=10)
                
                # حالة الطيارة
                status_label = tk.Label(
                    ac_frame,
                    text="⊗ Pending",
                    font=('Segoe UI', 10, 'bold'),
                    bg='#FCF3CF',
                    fg=self.colors['warning'],
                    width=16,
                    relief='solid',
                    borderwidth=1,
                    padx=12,
                    pady=6
                )
                status_label.pack(side='left', padx=8)
                self.aircraft_status_labels[aircraft] = status_label
                
                # تاريخ تحديث المهندس
                engineer_date_label = tk.Label(
                    ac_frame,
                    text="Engineer: --",
                    font=('Segoe UI', 8),
                    bg=self.colors['bg_card'],
                    fg='gray',
                    padx=8,
                    pady=4
                )
                engineer_date_label.pack(side='left', padx=5)
                self.aircraft_engineer_date_labels[aircraft] = engineer_date_label
                
                # تاريخ تحديث الطيارة
                installation_date_label = tk.Label(
                    ac_frame,
                    text="Aircraft: --",
                    font=('Segoe UI', 8),
                    bg=self.colors['bg_card'],
                    fg='gray',
                    padx=8,
                    pady=4
                )
                installation_date_label.pack(side='left', padx=5)
                self.aircraft_installation_date_labels[aircraft] = installation_date_label
            
            # === الصف الثاني: الدورة القادمة (تحت السيكل والطيارات) ===
            card2 = ttk.Frame(cards_container, style='Card.TFrame', padding=20)
            card2.pack(fill='x', pady=10, ipady=10)
            
            ttk.Label(card2, text="UPCOMING CYCLE & TIMELINE", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 10))
            ttk.Separator(card2, orient='horizontal').pack(fill='x', pady=8)

            # معلومات الدورة القادمة
            self.lbl_upcoming = ttk.Label(
                card2, 
                text="Loading next cycle info...", 
                font=('Segoe UI', 11),
                style='CardBody.TLabel'
            )
            self.lbl_upcoming.pack(anchor='w', pady=(8, 15))
            
            # شريط التقدم
            ttk.Label(card2, text="Countdown:", style='CardBody.TLabel', font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 6))
            self.progress_bar = ttk.Progressbar(
                card2,
                length=300,
                mode='determinate',
                style="Horizontal.TProgressbar"
            )
            self.progress_bar.pack(fill='x', pady=5, ipady=6)
        
        
    def create_cycles_table_tab(self):
        """جدول بتصميم نظيف"""
        table_frame = ttk.Frame(self.notebook, style='Main.TFrame')
        self.notebook.add(table_frame, text="📅 ALL CYCLES")
        
        # شريط بحث عائم (Card look)
        search_card = ttk.Frame(table_frame, style='Card.TFrame', padding=10)
        search_card.pack(fill='x', padx=10, pady=(15, 5))
        
        ttk.Label(search_card, text="🔍 Search Database:", style='CardBody.TLabel').pack(side='left', padx=10)
        search_entry = ttk.Entry(search_card, width=40, font=('Segoe UI', 10))
        search_entry.pack(side='left', padx=10)
        
        # إطار الجدول
        tree_container = ttk.Frame(table_frame) # No style to avoid bg conflict with scrollbar
        tree_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Cycle', 'Effective Date', 'Status', 'Engineer Action')
        
        self.cycles_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=20)
        
        # تنسيق الهيدر
        for col in columns:
            self.cycles_tree.heading(col, text=col)
            self.cycles_tree.column(col, anchor='center')
            
        self.cycles_tree.column('Cycle', width=100)
        self.cycles_tree.column('Effective Date', width=150)
        self.cycles_tree.column('Engineer Action', width=200)

        # سكرول بار أنيق
        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.cycles_tree.yview)
        self.cycles_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cycles_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.load_cycles_table()
        
    def create_update_registration_tab(self):
        """نموذج تسجيل بستايل حديث مع Scroll"""
        update_frame = ttk.Frame(self.notebook, style='Main.TFrame')
        self.notebook.add(update_frame, text="📝 REGISTER UPDATE")
        
        # إضافة Canvas + Scrollbar
        canvas = tk.Canvas(update_frame, bg=self.colors['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(update_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Main.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ربط عجلة الماوس بـ Scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # جعل النموذج في المنتصف كبطاقة (داخل الـ scrollable_frame)
        center_frame = ttk.Frame(scrollable_frame, style='Main.TFrame')
        center_frame.pack(expand=True, fill='both', padx=100, pady=20)
        
        form_card = ttk.Frame(center_frame, style='Card.TFrame', padding=30)
        form_card.pack(fill='both', expand=True)
        
        ttk.Label(form_card, text="New Update Entry", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # الحقول
        fields = [
            ("Engineer Name:", "entry"),
            ("Cycle Number:", "combobox"),
            ("Upload File:", "file"),
            ("Update Date/Time:", "datetime"),
            ("Update Notes:", "text") # نقل الملاحظات للآخر
        ]
        
        self.form_widgets = {}
        
        try:
            # جلب فقط الدورة القادمة (UPCOMING) بدلاً من جميع الدورات
            upcoming_cycle_data, _ = self.db.get_upcoming_cycle_data()
            if upcoming_cycle_data:
                upcoming_cycle_num = upcoming_cycle_data['cycle_number'] if isinstance(upcoming_cycle_data, dict) else upcoming_cycle_data[1]
                cycle_values = [upcoming_cycle_num]
            else:
                cycle_values = []
        except:
            cycle_values = []

        for i, (label, widget_type) in enumerate(fields):
            field_container = ttk.Frame(form_card, style='Card.TFrame')
            field_container.pack(fill='x', pady=8)
            
            ttk.Label(field_container, text=label, width=15, style='CardBody.TLabel', anchor='w').pack(side='left')
            
            if widget_type == "entry":
                widget = ttk.Entry(field_container, width=40, font=('Segoe UI', 10))
            elif widget_type == "combobox":
                widget = ttk.Combobox(field_container, width=38, state='readonly', font=('Segoe UI', 10))
                widget['values'] = cycle_values
                
                # اختيار الدورة القادمة (UPCOMING) افتراضياً وهي الخيار الوحيد
                if cycle_values:
                    widget.set(cycle_values[0])
                
                # ربط الحدث: عند تغيير السيكل يتم تحديث حالات الطيارات
                widget.bind('<<ComboboxSelected>>', lambda e: self.update_aircraft_status_in_form())
            elif widget_type == "datetime":
                # حقل التاريخ والوقت - يتم ملؤه بالتاريخ والوقت الحالي تلقائياً
                from datetime import datetime
                widget = ttk.Entry(field_container, width=40, font=('Segoe UI', 10))
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                widget.insert(0, current_datetime)
            elif widget_type == "text":
                widget = tk.Text(field_container, height=5, width=40, font=('Segoe UI', 10), relief='flat', bg='#f0f2f5')
            elif widget_type == "file":
                f_frame = ttk.Frame(field_container, style='Card.TFrame')
                f_frame.pack(side='left', fill='x', expand=True)
                
                file_entry = ttk.Entry(f_frame, width=30, font=('Segoe UI', 10))
                file_entry.pack(side='left', padx=(0, 10))
                
                browse_btn = ttk.Button(
                    f_frame,
                    text="📂 Browse",
                    command=lambda e=file_entry: self.browse_file(e)
                )
                browse_btn.pack(side='left')
                widget = file_entry
            
            if widget_type != "file":
                widget.pack(side='left', fill='x')
            
            self.form_widgets[label] = widget
            
        # الأزرار (SAVE و CLEAR) - في الأعلى قبل الطيارات
        btn_frame = ttk.Frame(form_card, style='Card.TFrame')
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="💾 SAVE TO DATABASE",
            command=self.save_update,
            style='RedSea.TButton',
            width=20
        ).pack(side='left', padx=10)
        
        ttk.Button(
            btn_frame,
            text="❌ CLEAR",
            command=self.clear_form,
            width=15
        ).pack(side='left', padx=10)
            
        # --- قسم اختيار الطيارات (Aircraft Selection) ---
        ttk.Separator(form_card, orient='horizontal').pack(fill='x', pady=15)
        
        ttk.Label(form_card, text="SELECT AIRCRAFT:", style='CardTitle.TLabel').pack(anchor='w', pady=(10, 15))
        
        # إنشاء إطار للـ Checkboxes
        aircraft_frame = ttk.Frame(form_card, style='Card.TFrame')
        aircraft_frame.pack(fill='x', pady=10)
        
        # المتغيرات للـ Checkboxes
        self.aircraft_vars = {}
        self.aircraft_status_reg = {}  # لتخزين حالة كل طيارة في صفحة التسجيل
        aircraft_list = ['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
        
        for aircraft in aircraft_list:
            var = tk.BooleanVar()
            self.aircraft_vars[aircraft] = var
            
            # إطار منفصل لكل طيارة مع الحالة
            ac_item_frame = ttk.Frame(aircraft_frame, style='Card.TFrame')
            ac_item_frame.pack(side='left', padx=15, pady=5)
            
            # Checkbox للطيارة
            checkbox = tk.Checkbutton(
                ac_item_frame,
                text=aircraft,
                variable=var,
                font=('Segoe UI', 11, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['primary'],
                activebackground=self.colors['bg_main'],
                activeforeground=self.colors['primary'],
                selectcolor=self.colors['primary'],
                highlightthickness=0,
                padx=10,
                pady=5
            )
            checkbox.pack(side='left')
            
            # تسمية الحالة بجانب الـ checkbox
            status_label = tk.Label(
                ac_item_frame,
                text="Loading...",
                font=('Segoe UI', 9),
                bg=self.colors['bg_card'],
                fg='gray'
            )
            status_label.pack(side='left', padx=(10, 0))
            self.aircraft_status_reg[aircraft] = status_label
        
        # تحديث حالات الطيارات
        self.update_aircraft_status_in_form()

    def create_installation_confirmation_tab(self):
        """صفحة تأكيد التثبيت على الطيارات"""
        confirmation_frame = ttk.Frame(self.notebook, style='Main.TFrame')
        self.notebook.add(confirmation_frame, text="✅ INSTALLATION CONFIRMATION")
        
        # إضافة Canvas + Scrollbar
        canvas = tk.Canvas(confirmation_frame, bg=self.colors['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(confirmation_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Main.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ربط عجلة الماوس بـ Scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # جعل النموذج في المنتصف كبطاقة
        center_frame = ttk.Frame(scrollable_frame, style='Main.TFrame')
        center_frame.pack(expand=True, fill='both', padx=100, pady=20)
        
        form_card = ttk.Frame(center_frame, style='Card.TFrame', padding=30)
        form_card.pack(fill='both', expand=True)
        
        ttk.Label(form_card, text="Confirm Installation on Aircraft (UPCOMING CYCLE)", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # --- اختيار الدورة (فقط UPCOMING - لا يمكن اختيار دورات قديمة) ---
        cycle_container = ttk.Frame(form_card, style='Card.TFrame')
        cycle_container.pack(fill='x', pady=8)
        
        ttk.Label(cycle_container, text="Cycle Number:", width=15, style='CardBody.TLabel', anchor='w').pack(side='left')
        
        try:
            # جلب فقط الدورة القادمة (UPCOMING) بدلاً من جميع الدورات
            upcoming_cycle_data, _ = self.db.get_upcoming_cycle_data()
            if upcoming_cycle_data:
                upcoming_cycle_num = upcoming_cycle_data['cycle_number'] if isinstance(upcoming_cycle_data, dict) else upcoming_cycle_data[1]
                cycle_values = [upcoming_cycle_num]
            else:
                cycle_values = []
        except:
            cycle_values = []
        
        self.confirmation_cycle_combo = ttk.Combobox(cycle_container, width=38, state='readonly', font=('Segoe UI', 10))
        self.confirmation_cycle_combo['values'] = cycle_values
        
        # اختيار الدورة القادمة (UPCOMING) افتراضياً وهي الخيار الوحيد
        if cycle_values:
            self.confirmation_cycle_combo.set(cycle_values[0])
        
        self.confirmation_cycle_combo.pack(side='left', fill='x')
        
        # --- اختيار الطيارات ---
        ttk.Separator(form_card, orient='horizontal').pack(fill='x', pady=15)
        
        ttk.Label(form_card, text="SELECT AIRCRAFT:", style='CardTitle.TLabel').pack(anchor='w', pady=(10, 15))
        
        # إنشاء إطار للـ Checkboxes
        aircraft_frame = ttk.Frame(form_card, style='Card.TFrame')
        aircraft_frame.pack(fill='x', pady=10)
        
        # المتغيرات للـ Checkboxes
        self.confirmation_aircraft_vars = {}
        aircraft_list = ['SU-RSA', 'SU-RSB', 'SU-RSC', 'SU-RSD']
        
        for aircraft in aircraft_list:
            var = tk.BooleanVar()
            self.confirmation_aircraft_vars[aircraft] = var
            
            # إطار منفصل لكل طيارة
            ac_item_frame = ttk.Frame(aircraft_frame, style='Card.TFrame')
            ac_item_frame.pack(side='left', padx=15, pady=5)
            
            # Checkbox للطيارة
            checkbox = tk.Checkbutton(
                ac_item_frame,
                text=aircraft,
                variable=var,
                font=('Segoe UI', 11, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['primary'],
                activebackground=self.colors['bg_main'],
                activeforeground=self.colors['primary'],
                selectcolor=self.colors['primary'],
                highlightthickness=0,
                padx=10,
                pady=5
            )
            checkbox.pack(side='left')
        
        # --- حقل التاريخ والوقت الفعلي للتثبيت ---
        ttk.Separator(form_card, orient='horizontal').pack(fill='x', pady=15)
        
        install_time_container = ttk.Frame(form_card, style='Card.TFrame')
        install_time_container.pack(fill='x', pady=8)
        
        ttk.Label(install_time_container, text="Installation Time:", width=15, style='CardBody.TLabel', anchor='w').pack(side='left')
        
        from datetime import datetime
        self.confirmation_install_time = ttk.Entry(install_time_container, width=40, font=('Segoe UI', 10))
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.confirmation_install_time.insert(0, current_datetime)
        self.confirmation_install_time.pack(side='left', fill='x')
        
        # --- أزرار التحكم ---
        ttk.Separator(form_card, orient='horizontal').pack(fill='x', pady=15)
        
        btn_frame = ttk.Frame(form_card, style='Card.TFrame')
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="✓ CONFIRM INSTALLATION",
            command=self.confirm_installation,
            style='RedSea.TButton',
            width=25
        ).pack(side='left', padx=10)
        
        ttk.Button(
            btn_frame,
            text="❌ CLEAR",
            command=self.clear_confirmation_form,
            width=15
        ).pack(side='left', padx=10)

    def create_history_tab(self):
        """سجل التحديثات"""
        history_frame = ttk.Frame(self.notebook, style='Main.TFrame')
        self.notebook.add(history_frame, text="🕒 HISTORY")
        
        # نفس تصميم الجدول
        tree_container = ttk.Frame(history_frame, padding=10)
        tree_container.pack(fill='both', expand=True)
        
        columns = ('ID', 'Cycle', 'Engineer', 'Date', 'Time', 'Notes')
        self.history_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, anchor='center')
        
        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        ttk.Button(
            history_frame,
            text="🔄 Refresh Log",
            command=self.load_history
        ).pack(pady=10)

    def create_navigation(self, parent):
        """شريط تنقل سفلي حديث"""
        nav_frame = ttk.Frame(parent, style='Nav.TFrame', height=60)
        nav_frame.pack(fill='x', side='bottom')
        nav_frame.pack_propagate(False) # الحفاظ على الارتفاع
        
        # فاصل علوي
        ttk.Separator(nav_frame, orient='horizontal').pack(fill='x')
        
        # حاوية للأزرار في المنتصف
        center_nav = ttk.Frame(nav_frame, style='Nav.TFrame')
        center_nav.pack(expand=True)
        
        nav_buttons = [
            ("📊 Dashboard", 0),
            ("📅 Cycles", 1),
            ("📝 Register", 2),
            ("🕒 History", 3)
        ]
        
        for text, tab_index in nav_buttons:
            btn = ttk.Button(
                center_nav,
                text=text,
                style='Nav.TButton',
                command=lambda idx=tab_index: self.notebook.select(idx)
            )
            btn.pack(side='left', padx=20, pady=10)

    # =========================================================================
    # الدوال المنطقية (Logic) - لم يتم تغيير أي شيء فيها لضمان عمل البرنامج
    # =========================================================================

    def update_current_cycle_display(self, cycle_info, days_remaining, is_recorded=True):
        if cycle_info:
            cycle_num = cycle_info['cycle_number']
            
            # تم تحسين صياغة العرض فقط لتناسب التصميم الجديد
            info_text = f"CYCLE {cycle_num}\n"
            info_text += f"Effective: {cycle_info['effective_date']}\n"
            status = cycle_info.get('status', 'Unknown').upper()
            info_text += f"STATUS: {status}"
            
            self.current_cycle_info.config(text=info_text)
            
            if status == 'ACTIVE' and not is_recorded:
                self.alert_status_var.set(f"⚠️ CRITICAL: Cycle {cycle_num} Active NOT Installed!")
                self.current_cycle_info.configure(foreground=self.colors['secondary']) # أحمر
            else:
                self.current_cycle_info.configure(foreground=self.colors['text_main']) # طبيعي
                
                if days_remaining is not None and days_remaining <= 13:
                    self.alert_status_var.set("⚠️ YES - New Cycle Incoming!")
                else:
                    self.alert_status_var.set("✅ NO - System Up to Date")

            if days_remaining is not None:
                self.remaining_days_var.set(f"{days_remaining} Days")
                try:
                    progress = ((28 - days_remaining) / 28) * 100
                    self.progress_bar['value'] = min(max(progress, 0), 100)
                    
                    # تغيير لون الشريط حسب القرب (يتطلب ستايل ديناميكي لكن سنكتفي بالقياسي الآن)
                except:
                    self.progress_bar['value'] = 0
            else:
                self.remaining_days_var.set("Calculating...")

    def browse_file(self, entry_widget):
        file_path = filedialog.askopenfilename(
            title="Select Update File",
            filetypes=[
                ("All files", "*.*"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg *.jpeg *.png"),
                ("Document files", "*.doc *.docx *.txt")
            ]
        )
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
    
    def save_update(self):
            # 1. جلب البيانات من الحقول (التحقق الأولي)
            engineer_name = self.form_widgets["Engineer Name:"].get()
            cycle_number = self.form_widgets["Cycle Number:"].get()
            notes = self.form_widgets["Update Notes:"].get("1.0", tk.END).strip()
            file_path = self.form_widgets["Upload File:"].get()
            update_datetime = self.form_widgets["Update Date/Time:"].get()
            selected_aircraft = [aircraft for aircraft, var in self.aircraft_vars.items() if var.get()]
            
            if not engineer_name or not cycle_number:
                messagebox.showwarning("Validation", "Please fill in Engineer Name and Cycle Number")
                return
            
            if not selected_aircraft:
                messagebox.showwarning("Validation", "Please select at least one aircraft")
                return

            # 2. التحقق من التاريخ (يجب أن يتم في الـ Main Thread)
            validation_result = self.validate_date_within_cycle(update_datetime, cycle_number)
            if validation_result is None: return
            if validation_result is not True:
                _, valid_start, valid_end = validation_result
                messagebox.showerror("Invalid Date", f"❌ التاريخ خارج نطاق الدورة!\nمن {valid_start} إلى {valid_end}")
                return

            # 3. تشغيل الحفظ في الخلفية عشان ميهنجش
    def save_update(self):
            # 1. جلب البيانات
            engineer_name = self.form_widgets["Engineer Name:"].get()
            cycle_number = self.form_widgets["Cycle Number:"].get()
            notes = self.form_widgets["Update Notes:"].get("1.0", tk.END).strip()
            file_path = self.form_widgets["Upload File:"].get()
            update_datetime = self.form_widgets["Update Date/Time:"].get()
            selected_aircraft = [aircraft for aircraft, var in self.aircraft_vars.items() if var.get()]
            
            if not engineer_name or not cycle_number or not selected_aircraft:
                messagebox.showwarning("Validation", "Please fill all required fields and select aircraft")
                return

            # 2. التحقق من التاريخ
            validation_result = self.validate_date_within_cycle(update_datetime, cycle_number)
            if validation_result is None or validation_result is not True:
                return

            # 3. تشغيل الحفظ في الخلفية
            def perform_save():
                try:
                    # الحفظ في قاعدة البيانات
                    for aircraft in selected_aircraft:
                        self.db.record_update(cycle_number, engineer_name, file_path, notes, aircraft, update_datetime)
                    self.db.update_cycle_status_after_install(cycle_number)
                    
                    # تأخير بسيط لضمان حفظ الملف
                    import time
                    time.sleep(1)
                    
                    # رفع الداتا للسيرفر
                    sync_cloud.start_sync()

                    # تحديث الواجهة (لازم يكون داخل after)
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"✓ Updates saved successfully!"))
                    self.root.after(0, self.clear_form)
                    self.root.after(0, self.update_aircraft_status_in_form)
                    self.root.after(0, self.load_history)
                    self.root.after(0, self.load_cycles_table)
                    self.root.after(0, self.refresh_dashboard_data)
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

            import threading
            threading.Thread(target=perform_save, daemon=True).start()
    def manual_sync(self):
        """دالة للربط بين الزرار والسكربت"""
        import sync_cloud
        # رسالة للمستخدم إن العملية بدأت
        self.root.after(0, lambda: messagebox.showinfo("Sync", "Cloud Sync Started..."))
        
        # تشغيل عملية الرفع في الخلفية
        sync_cloud.start_sync()
    def clear_form(self):
        from datetime import datetime
        for label, widget in self.form_widgets.items():
            if label == "Update Notes:":
                widget.delete("1.0", tk.END)
            elif label == "Cycle Number:":
                # إعادة تعيين الدورة بالدورة القادمة (UPCOMING) الافتراضية
                upcoming_cycle_data, _ = self.db.get_upcoming_cycle_data()
                if upcoming_cycle_data:
                    upcoming_cycle_num = upcoming_cycle_data['cycle_number'] if isinstance(upcoming_cycle_data, dict) else upcoming_cycle_data[1]
                    widget.set(upcoming_cycle_num)
                else:
                    widget.set('')
            elif label == "Update Date/Time:":
                # إعادة تعيين التاريخ والوقت بالتاريخ الحالي
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                widget.delete(0, tk.END)
                widget.insert(0, current_datetime)
            else:
                widget.delete(0, tk.END)
        
        # مسح اختيارات الطيارات
        for var in self.aircraft_vars.values():
            var.set(False)
    
    def update_aircraft_status_in_form(self):
        """تحديث حالات الطيارات في صفحة التسجيل بناءً على السيكل القادم (UPCOMING)"""
        try:
            # جلب السيكل المختار من الـ Combobox
            selected_cycle = self.form_widgets["Cycle Number:"].get()
            
            if not selected_cycle:
                # إذا لم يتم اختيار سيكل، استخدم السيكل القادم (UPCOMING)
                upcoming_cycle_data, _ = self.db.get_upcoming_cycle_data()
                if not upcoming_cycle_data:
                    for label in self.aircraft_status_reg.values():
                        label.config(text="⊗ Pending", fg=self.colors['warning'])
                    return
                selected_cycle = upcoming_cycle_data['cycle_number'] if isinstance(upcoming_cycle_data, dict) else upcoming_cycle_data[1]
            
            # جلب حالات الطيارات للسيكل المختار
            aircraft_status = self.db.get_aircraft_status(selected_cycle)
            
            for aircraft, label in self.aircraft_status_reg.items():
                status = aircraft_status.get(aircraft, 'Pending')
                
                if status == 'Updated':
                    label.config(text="✓ Updated", fg=self.colors['success'])
                else:
                    label.config(text="⊗ Pending", fg=self.colors['warning'])
        except Exception as e:
            print(f"Error updating aircraft status in form: {e}")
    
    def load_cycles_table(self):
        for item in self.cycles_tree.get_children():
            self.cycles_tree.delete(item)
        
        cycles = self.db.get_all_cycles()
        
        for cycle in cycles:
            status = cycle['status'].upper()
            is_recorded = cycle['is_recorded']
            action_text = ""
            tags = ()
            
            if is_recorded:
                action_text = "✅ Updated"
                if status == 'ACTIVE': tags = ('active',)
                elif status == 'EXPIRED': tags = ('expired',)
            else:
                if status == 'MISSED':
                    action_text = "❌ FORGOTTEN!"
                    tags = ('missed',)
                elif status == 'ACTIVE':
                    action_text = "⚠️ PENDING..."
                    tags = ('active_alert',)
                elif status == 'UPCOMING':
                    action_text = "⏳ Waiting"
                    tags = ('upcoming',)

            values = (
                cycle['cycle_number'],
                cycle['effective_date'],
                status,
                action_text
            )
            self.cycles_tree.insert('', 'end', values=values, tags=tags)
        
        # ألوان الصفوف (تم تحديثها لتكون ألطف)
        self.cycles_tree.tag_configure('active', background='#D4EFDF', foreground='#145A32')
        self.cycles_tree.tag_configure('active_alert', background='#FCF3CF', foreground='#9A7D0A')
        self.cycles_tree.tag_configure('upcoming', background='white', foreground='#7F8C8D')
        self.cycles_tree.tag_configure('expired', background='#F2F3F4', foreground='#BDC3C7')
        self.cycles_tree.tag_configure('missed', background='#FADBD8', foreground='#78281F')
    # مثال للتعديل في gui.py

    def update_dashboard_display(self, active_cycle, upcoming_cycle, days_remaining, is_recorded):
        """تحديث الواجهة لعرض الدورة الحالية والقادمة وحالة الطيارات"""
        
        # 1. عرض الدورة الحالية (Active)
        if active_cycle:
            # نتأكد من التعامل مع البيانات سواء كانت قاموس أو صف
            cycle_num = active_cycle['cycle_number'] if isinstance(active_cycle, dict) else active_cycle[1]
            eff_date = active_cycle['effective_date'] if isinstance(active_cycle, dict) else active_cycle[2]
            
            self.lbl_active_cycle.config(text=f"CYCLE {cycle_num}")
            self.lbl_active_date.config(text=f"Effective Date: {eff_date}")
            
            # تغيير الحالة واللون بناءً على ما إذا تم التسجيل أم لا
            if is_recorded:
                self.lbl_status.config(text="✓ INSTALLED ON AIRCRAFT", fg=self.colors['success']) # أخضر
            else:
                self.lbl_status.config(text="⚠ ACTION REQUIRED: NOT INSTALLED YET", fg=self.colors['secondary']) # أحمر
        else:
            self.lbl_active_cycle.config(text="NO ACTIVE CYCLE")
            self.lbl_active_date.config(text="--")
            self.lbl_status.config(text="System Waiting...", fg="gray")

        # 2. عرض الدورة القادمة (Upcoming)
        if upcoming_cycle:
            next_num = upcoming_cycle['cycle_number'] if isinstance(upcoming_cycle, dict) else upcoming_cycle[1]
            self.lbl_upcoming.config(text=f"Next Update: Cycle {next_num} (in {days_remaining} days)")
            
            # تحديث شريط التقدم
            try:
                # نفترض أن الدورة مدتها 28 يوم
                progress = ((28 - days_remaining) / 28) * 100
                self.progress_bar['value'] = min(max(progress, 0), 100)
            except:
                self.progress_bar['value'] = 0
        else:
            self.lbl_upcoming.config(text="No upcoming cycle scheduled")
            self.progress_bar['value'] = 0
        
        # 3. عرض حالة الطيارات للدورة القادمة (UPCOMING)
        if upcoming_cycle:
            # استخدام الدورة القادمة (UPCOMING) بدلاً من الدورة الحالية (ACTIVE)
            cycle_num = upcoming_cycle['cycle_number'] if isinstance(upcoming_cycle, dict) else upcoming_cycle[1]
            aircraft_status = self.db.get_aircraft_status(cycle_num)
            installation_status = self.db.get_aircraft_installation_status(cycle_num)
            update_dates = self.db.get_aircraft_update_dates(cycle_num)
            
            for aircraft, status_label in self.aircraft_status_labels.items():
                status = aircraft_status.get(aircraft, 'Pending')
                install_info = installation_status.get(aircraft, {'installed': False, 'datetime': 'N/A'})
                date_info = update_dates.get(aircraft, {'engineer_date': 'N/A', 'installation_date': 'N/A'})
                
                if status == 'Updated':
                    if install_info['installed']:
                        # تم التثبيت فعلياً على الطيارة
                        status_label.config(
                            text="✓ Installed", 
                            fg=self.colors['success'], 
                            bg='#D4EFDF'
                        )
                    else:
                        # تم التسجيل لكن لم يتم التثبيت بعد
                        status_label.config(
                            text="⚡ Recorded (Not Installed)", 
                            fg=self.colors['warning'], 
                            bg='#FEF5E7'
                        )
                else:
                    status_label.config(text="⊗ Pending", fg=self.colors['secondary'], bg='#FCF3CF')
                
                # تحديث تاريخ تحديث المهندس
                engineer_date_text = f"Engineer: {date_info['engineer_date']}"
                self.aircraft_engineer_date_labels[aircraft].config(text=engineer_date_text)
                
                # تحديث تاريخ تحديث الطيارة
                aircraft_date_text = f"Aircraft: {date_info['installation_date']}"
                self.aircraft_installation_date_labels[aircraft].config(text=aircraft_date_text)
        else:
            # إذا لم تكن هناك دورة قادمة، نعرض جميع الطيارات كـ Pending
            for aircraft in self.aircraft_status_labels:
                self.aircraft_status_labels[aircraft].config(text="⊗ Pending", fg=self.colors['secondary'], bg='#FCF3CF')
                self.aircraft_engineer_date_labels[aircraft].config(text="Engineer: --")
                self.aircraft_installation_date_labels[aircraft].config(text="Aircraft: --")
    
    def confirm_installation(self):
        """تأكيد التثبيت على الطيارات المختارة"""
        try:
            cycle_number = self.confirmation_cycle_combo.get()
            selected_aircraft = [aircraft for aircraft, var in self.confirmation_aircraft_vars.items() if var.get()]
            install_time = self.confirmation_install_time.get()
            
            if not cycle_number:
                messagebox.showwarning("Validation", "Please select a cycle number")
                return
            
            if not selected_aircraft:
                messagebox.showwarning("Validation", "Please select at least one aircraft")
                return

            # ============================================================
            #  بداية التعديل الجديد: التحقق من الوقت والتاريخ
            # ============================================================
            validation_result = self.validate_date_within_cycle(install_time, cycle_number)
            
            if validation_result is None: return
            
            if validation_result is not True:
                _, valid_start, valid_end = validation_result
                messagebox.showerror(
                    "Invalid Installation Date",
                    f"❌ وقت التركيب (Installation Time) خارج نطاق الدورة!\n\n"
                    f"📅 الدورة {cycle_number} صالحة فقط من:\n"
                    f"   {valid_start}  إلى  {valid_end}\n\n"
                    f"يرجى تصحيح الوقت."
                )
                return
            # ============================================================
            
            # الحفظ
            for aircraft in selected_aircraft:
                cursor = self.db._get_cursor()
                try:
                    cursor.execute('''
                        SELECT id FROM updates 
                        WHERE cycle_number = ? AND aircraft_reg = ?
                        ORDER BY id DESC LIMIT 1
                    ''', (cycle_number, aircraft))
                    result = cursor.fetchone()
                    if result:
                        self.db.mark_update_installed_on_aircraft(result[0], install_time)
                finally:
                    cursor.close()
            
            messagebox.showinfo("Success", f"✓ Installation confirmed for {len(selected_aircraft)} aircraft!")
            self.clear_confirmation_form()
            self.refresh_dashboard_data()
            self.load_history()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to confirm installation: {str(e)}")
    
    def clear_confirmation_form(self):
        """مسح نموذج التأكيد"""
        from datetime import datetime
        
        self.confirmation_cycle_combo.set('')
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.confirmation_install_time.delete(0, tk.END)
        self.confirmation_install_time.insert(0, current_datetime)
        
        # مسح اختيارات الطيارات
        for var in self.confirmation_aircraft_vars.values():
            var.set(False)
    
    def refresh_dashboard_data(self):
        """دالة لإعادة قراءة البيانات من قاعدة البيانات وتحديث الواجهة فوراً"""
        try:
            # 1. التأكد من تحديث الحالات في القاعدة
            self.db.auto_update_statuses_by_date()
            
            # 2. جلب البيانات الجديدة
            active_cycle = self.db.get_active_cycle_data()
            upcoming_cycle, days_remaining = self.db.get_upcoming_cycle_data()
            
            # 3. التحقق من حالة التسجيل
            is_recorded = False
            if active_cycle:
                # التعامل مع البيانات سواء كانت قاموس أو صف
                cycle_num = active_cycle['cycle_number'] if isinstance(active_cycle, dict) else active_cycle[1]
                is_recorded = self.db.check_if_update_recorded(cycle_num)
                
            # 4. استدعاء دالة الرسم لتحديث النصوص والألوان
            self.update_dashboard_display(active_cycle, upcoming_cycle, days_remaining, is_recorded)
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
    def load_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = self.db.get_update_history()
        
        for record in history:
            values = (
                record['id'],
                record['cycle_number'],
                record['engineer_name'],
                record['update_date'],
                record['update_time'],
                record['notes'][:50] + "..." if len(record.get('notes', '')) > 50 else record.get('notes', '')
            )
            self.history_tree.insert('', 'end', values=values)
    
