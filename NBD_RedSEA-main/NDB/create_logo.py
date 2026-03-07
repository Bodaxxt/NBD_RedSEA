from PIL import Image, ImageDraw, ImageFont
import os

def create_temporary_logo():
    """إنشاء لوجو مؤقت لشركة Red Sea Airlines"""
    
    # إنشاء مجلد assets إذا لم يكن موجودًا
    os.makedirs("assets", exist_ok=True)
    
    # إنشاء صورة جديدة
    width, height = 400, 200
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # إضافة شعار موج البحر
    # رسم موجات زرقاء
    wave_colors = ['#003366', '#00509E', '#0077CC']
    
    for i in range(3):
        y_position = 70 + (i * 15)
        draw.ellipse([50, y_position, 350, y_position + 40], 
                    outline=wave_colors[i], width=3)
    
    # إضافة طائرة صغيرة
    draw.polygon([(200, 60), (190, 75), (210, 75)], fill='#C8102E')  # جسم الطائرة
    
    # إضافة نص
    try:
        font_large = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # نص الشركة
    draw.text((width//2, 120), "Red Sea Airlines", 
             fill='#C8102E', font=font_large, anchor='mm')
    
    # نص فرعي
    draw.text((width//2, 160), "FMS Navigation Data Manager", 
             fill='#003366', font=font_small, anchor='mm')
    
    # حفظ الصورة
    logo_path = "assets/red_sea_logo.png"
    image.save(logo_path)
    
    print(f"تم إنشاء لوجو مؤقت في: {logo_path}")
    return logo_path

if __name__ == "__main__":
    create_temporary_logo()