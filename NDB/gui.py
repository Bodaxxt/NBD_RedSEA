import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk  # استيراد مكتبة الصور

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
        self.create_history_tab()
        
    def create_dashboard_tab(self):
            """إنشاء لوحة المعلومات بتصميم البطاقات (Cards)"""
            dashboard_bg = ttk.Frame(self.notebook, style='Main.TFrame')
            self.notebook.add(dashboard_bg, text="📊 DASHBOARD")
            
            # حاوية مركزية للبطاقات بدون Scroll
            cards_container = ttk.Frame(dashboard_bg, style='Main.TFrame')
            cards_container.pack(fill='both', expand=True, padx=10, pady=20)
            
            # === الصف الأول: السيكل الحالي والطيارات جنب بعض ===
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
            self.lbl_status.pack(pady=10)
            
            # --- البطاقة الثالثة: حالة الطيارات (Aircraft Status) جنب السيكل ---
            card3 = ttk.Frame(top_row, style='Card.TFrame', padding=20)
            card3.pack(side='left', fill='both', expand=True, padx=(10, 0))
            
            ttk.Label(card3, text="✈️ AIRCRAFT STATUS", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 10))
            ttk.Separator(card3, orient='horizontal').pack(fill='x', pady=8)
            
            # إنشاء إطار للطيارات مع حالاتها
            aircraft_status_frame = ttk.Frame(card3, style='Card.TFrame')
            aircraft_status_frame.pack(fill='x', pady=10)
            
            self.aircraft_status_labels = {}
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
            ("Update Notes:", "text") # نقل الملاحظات للآخر
        ]
        
        self.form_widgets = {}
        
        try:
            all_cycles = self.db.get_all_cycles()
            cycle_values = [c['cycle_number'] for c in all_cycles]
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
                
                # اختيار السيكل الحالي بشكل افتراضي
                current_cycle = self.db.get_active_cycle_data()
                if current_cycle:
                    current_cycle_num = current_cycle['cycle_number'] if isinstance(current_cycle, dict) else current_cycle[1]
                    if current_cycle_num in cycle_values:
                        widget.set(current_cycle_num)
                
                # ربط الحدث: عند تغيير السيكل يتم تحديث حالات الطيارات
                widget.bind('<<ComboboxSelected>>', lambda e: self.update_aircraft_status_in_form())
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
        try:
            # جلب البيانات من الحقول
            engineer_name = self.form_widgets["Engineer Name:"].get()
            cycle_number = self.form_widgets["Cycle Number:"].get()
            notes = self.form_widgets["Update Notes:"].get("1.0", tk.END).strip()
            file_path = self.form_widgets["Upload File:"].get()
            
            # جلب الطيارات المختارة
            selected_aircraft = [aircraft for aircraft, var in self.aircraft_vars.items() if var.get()]
            
            # التحقق من صحة البيانات
            if not engineer_name or not cycle_number:
                messagebox.showwarning("Validation", "Please fill in Engineer Name and Cycle Number")
                return
            
            if not selected_aircraft:
                messagebox.showwarning("Validation", "Please select at least one aircraft")
                return
            
            # ========== فحص منع التكرار: التحقق من عدم تكرار نفس الطيارة في نفس الـ Cycle ==========
            duplicates = []
            for aircraft in selected_aircraft:
                # البحث عن هل هذه الطيارة سبق عملها في نفس الـ Cycle
                cursor = self.db._get_cursor()
                try:
                    cursor.execute('''
                        SELECT COUNT(*) FROM updates 
                        WHERE cycle_number = ? AND aircraft_reg = ?
                    ''', (cycle_number, aircraft))
                    result = cursor.fetchone()
                    count = result[0] if result else 0
                    
                    if count > 0:
                        duplicates.append(aircraft)
                finally:
                    cursor.close()
            
            # إذا كانت هناك طيارات متكررة، عرض رسالة تحذير
            if duplicates:
                dup_list = ", ".join(duplicates)
                messagebox.showerror(
                    "Duplicate Update",
                    f"❌ These aircraft already have updates in Cycle {cycle_number}:\n\n{dup_list}\n\n"
                    f"✓ You can only update each aircraft ONCE per cycle.\n"
                    f"🔄 Start a new cycle to update them again."
                )
                return
            
            # ========== إذا لم تكن هناك مشاكل، احفظ التحديثات ==========
            # حفظ تسجيل منفصل لكل طيارة مختارة
            for aircraft in selected_aircraft:
                update_id = self.db.record_update(cycle_number, engineer_name, file_path, notes, aircraft)
            
            self.db.update_cycle_status_after_install(cycle_number)

            messagebox.showinfo("Success", f"✓ Updates saved for {len(selected_aircraft)} aircraft successfully!")
            
            # تحديث الواجهة
            self.clear_form()
            self.update_aircraft_status_in_form()  # تحديث حالات الطيارات الفوري
            self.load_history()
            self.load_cycles_table()
            self.refresh_dashboard_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save update: {str(e)}")
    
    def clear_form(self):
        for label, widget in self.form_widgets.items():
            if label == "Update Notes:":
                widget.delete("1.0", tk.END)
            elif label == "Cycle Number:":
                widget.set('')
            else:
                widget.delete(0, tk.END)
        
        # مسح اختيارات الطيارات
        for var in self.aircraft_vars.values():
            var.set(False)
    
    def update_aircraft_status_in_form(self):
        """تحديث حالات الطيارات في صفحة التسجيل بناءً على السيكل المختار"""
        try:
            # جلب السيكل المختار من الـ Combobox
            selected_cycle = self.form_widgets["Cycle Number:"].get()
            
            if not selected_cycle:
                # إذا لم يتم اختيار سيكل، استخدم السيكل الحالي
                active_cycle = self.db.get_active_cycle_data()
                if not active_cycle:
                    for label in self.aircraft_status_reg.values():
                        label.config(text="⊗ Pending", fg=self.colors['warning'])
                    return
                selected_cycle = active_cycle['cycle_number'] if isinstance(active_cycle, dict) else active_cycle[1]
            
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
        
        # 3. عرض حالة الطيارات
        if active_cycle:
            cycle_num = active_cycle['cycle_number'] if isinstance(active_cycle, dict) else active_cycle[1]
            aircraft_status = self.db.get_aircraft_status(cycle_num)
            
            for aircraft, status_label in self.aircraft_status_labels.items():
                status = aircraft_status.get(aircraft, 'Pending')
                
                if status == 'Updated':
                    status_label.config(text="✓ Updated", fg=self.colors['success'], bg='#D4EFDF')
                else:
                    status_label.config(text="⊗ Pending", fg=self.colors['secondary'], bg='#FCF3CF')
        else:
            # إذا لم تكن هناك دورة نشطة، نعرض جميع الطيارات كـ Pending
            for status_label in self.aircraft_status_labels.values():
                status_label.config(text="⊗ Pending", fg=self.colors['secondary'], bg='#FCF3CF')
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