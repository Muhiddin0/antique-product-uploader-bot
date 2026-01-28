"""
Venu Marketplace Product Uploader
Avtomatik mahsulot yuklovchi AI agent class
"""

import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import random
import string
from datetime import datetime
from html import escape
from collections import Counter


class ProductUploaderAgent:
    """Avtomatik mahsulot yuklovchi AI agent"""
    
    BASE_URL = "https://api.venu.uz/api/v3"
    # API_KEY ni environment variable yoki config fayldan olish tavsiya etiladi
    API_KEY = os.getenv("VENU_API_KEY", "mPzVh43jap7LOAy9bX8TwGdzj2eTxNOBq4DS3xhV7U4P8McxjC")
    
    def __init__(self, email: str, password: str):
        """
        Args:
            email: Do'kon email manzili
            password: Do'kon paroli
        """
        self.email = email
        self.password = password
        self.token = None
        self.categories = []
        self.brands = []
        self.attributes = []
        
    def login(self) -> bool:
        """Login qilib token olish"""
        url = f"{self.BASE_URL}/seller/auth/login"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.API_KEY}",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Python/requests"
        }
        data = {
            "email": self.email,
            "password": self.password
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("token")
                if self.token:
                    print(f"✅ Muvaffaqiyatli login qilindi!")
                    return True
            print(f"❌ Login xatosi: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Login xatosi: {str(e)}")
            return False
    
    def get_categories(self) -> List[Dict]:
        """Kategoriyalarni olish"""
        if not self.token:
            print("❌ Avval login qiling!")
            return []
        
        url = f"{self.BASE_URL}/seller/categories"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json; charset=UTF-8",
            "lang": "en",
            "user-agent": "Python/requests"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.categories = response.json()
                print(f"✅ {len(self.categories)} ta kategoriya yuklandi")
                return self.categories
            return []
        except Exception as e:
            print(f"❌ Kategoriyalarni olishda xato: {str(e)}")
            return []
    
    def get_brands(self) -> List[Dict]:
        """Brendlarni olish"""
        if not self.token:
            print("❌ Avval login qiling!")
            return []
        
        url = f"{self.BASE_URL}/seller/brands"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Python/requests"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.brands = response.json()
                print(f"✅ {len(self.brands)} ta brend yuklandi")
                return self.brands
            return []
        except Exception as e:
            print(f"❌ Brendlarni olishda xato: {str(e)}")
            return []
    
    def get_attributes(self) -> List[Dict]:
        """Atributlarni olish"""
        if not self.token:
            print("❌ Avval login qiling!")
            return []
        
        url = f"https://api.venu.uz/api/v1/attributes"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json; charset=UTF-8",
            "lang": "en",
            "user-agent": "Python/requests"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.attributes = response.json()
                print(f"✅ {len(self.attributes)} ta atribut yuklandi")
                return self.attributes
            return []
        except Exception as e:
            print(f"❌ Atributlarni olishda xato: {str(e)}")
            return []
    
    def find_category_by_keywords(self, description: str, name: str) -> Optional[Dict]:
        """Tavsif va nomdan kategoriyani topish"""
        # HTML taglarini olib tashlash kategoriya topish uchun
        plain_text = re.sub(r'<[^>]+>', '', description)
        text = (plain_text + " " + name).lower()
        
        # Kalit so'zlar va kategoriya mapping
        category_keywords = {
            "smartfon": ["smartfon", "telefon", "phone", "mobile"],
            "noutbuk": ["noutbuk", "laptop", "notebook"],
            "kompyuter": ["kompyuter", "computer", "pc"],
            "planshet": ["planshet", "tablet", "планшет"],
            "monitor": ["monitor", "экран", "дисплей"],
            "klaviatura": ["klaviatura", "keyboard", "клавиатура"],
            "mush": ["mush", "mouse", "мышь"],
            "naushnik": ["naushnik", "headphone", "наушник"],
            "kamera": ["kamera", "camera", "камера"],
            "router": ["router", "маршрутизатор", "роутер"],
            "televizor": ["televizor", "tv", "телевизор"],
            "kreslo": ["kreslo", "chair", "кресло"],
            "blok": ["blok", "block", "блок"],
            "pamyat": ["pamyat", "memory", "память", "ram"],
            "disk": ["disk", "hard", "жесткий", "ssd", "hdd"],
        }
        
        best_match = None
        best_score = 0
        
        def search_in_category(cat, score=0):
            nonlocal best_match, best_score
            
            cat_name = cat.get("name", "").lower()
            cat_slug = cat.get("slug", "").lower()
            
            # Kategoriya nomida kalit so'zlar qidirish
            for keyword, variants in category_keywords.items():
                for variant in variants:
                    if variant in cat_name or variant in cat_slug or variant in text:
                        score += 1
            
            if score > best_score:
                best_score = score
                best_match = cat
            
            # Sub-kategoriyalarni qidirish
            for child in cat.get("childes", []):
                search_in_category(child, score)
        
        for category in self.categories:
            search_in_category(category)
        
        return best_match
    
    def find_brand_by_name(self, description: str, name: str) -> Optional[int]:
        """Tavsif va nomdan brendni topish"""
        # HTML taglarini olib tashlash brend topish uchun
        plain_text = re.sub(r'<[^>]+>', '', description)
        text = (plain_text + " " + name).lower()
        
        # Mashhur brendlar
        brand_names = [
            "samsung", "apple", "iphone", "xiaomi", "huawei", "oppo", "vivo",
            "asus", "acer", "hp", "lenovo", "dell", "msi", "gigabyte",
            "sony", "lg", "nokia", "motorola", "realme", "oneplus",
            "redmi", "honor", "poco", "zte", "meizu"
        ]
        
        for brand in self.brands:
            brand_name = brand.get("name", "").lower()
            if brand_name in text:
                return brand.get("id")
        
        # Agar brend topilmasa, birinchi brendni qaytarish (yoki None)
        if self.brands:
            return self.brands[0].get("id")
        return None
    
    def generate_product_code(self) -> str:
        """Yangi mahsulot kodi generatsiya qilish"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def generate_product_name(self, description: str) -> str:
        """
        AI yordamida tavsifdan mahsulot nomini generatsiya qilish
        
        Args:
            description: Mahsulot tavsifi (HTML yoki oddiy matn)
        
        Returns:
            str: Generatsiya qilingan mahsulot nomi
        """
        # HTML taglarini olib tashlash
        plain_text = self.strip_html_tags(description)
        
        # Qatorlarga bo'lish
        lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
        
        if not lines:
            return "Yangi mahsulot"
        
        # Birinchi qatorni tekshirish - ko'pincha sarlavha bo'ladi
        first_line = lines[0]
        
        # Emoji va maxsus belgilarni olib tashlash
        first_line_clean = re.sub(r'[^\w\s\-|]', '', first_line).strip()
        
        # Agar birinchi qator juda qisqa yoki bo'sh bo'lsa, keyingi qatorlarni tekshirish
        if len(first_line_clean) < 5 or not first_line_clean:
            # Keyingi qatorlarni tekshirish
            for line in lines[1:6]:  # Keyingi 5 qatorni tekshirish
                clean_line = re.sub(r'[^\w\s\-|]', '', line).strip()
                if len(clean_line) >= 5:
                    first_line_clean = clean_line
                    break
        
        # Agar hali ham topilmasa, barcha matndan muhim so'zlarni ajratish
        if not first_line_clean or len(first_line_clean) < 5:
            # Barcha matndan muhim so'zlarni topish
            words = re.findall(r'\b\w{3,}\b', plain_text.lower())
            
            # Eng ko'p ishlatilgan so'zlarni topish (stop words'larni olib tashlash)
            stop_words = {'bu', 'va', 'uchun', 'bilan', 'ham', 'yoki', 'lekin', 'agar', 
                         'qilib', 'qilish', 'qiladi', 'bo\'ladi', 'bo\'lishi', 'kerak',
                         'xususiyatlar', 'ma\'lumotlar', 'qo\'shimcha', 'asosiy'}
            
            important_words = [w for w in words if w not in stop_words and len(w) > 3]
            
            if important_words:
                # Eng ko'p ishlatilgan so'zlar
                word_freq = Counter(important_words)
                top_words = [word for word, _ in word_freq.most_common(3)]
                first_line_clean = ' '.join(top_words).title()
        
        # Nomni tozalash va formatlash
        name = first_line_clean.strip()
        
        # Uzunligini cheklash (100 belgi)
        if len(name) > 100:
            name = name[:97] + "..."
        
        # Agar hali ham bo'sh bo'lsa
        if not name or len(name) < 3:
            name = "Yangi mahsulot"
        
        # Birinchi harfni katta qilish
        name = name[0].upper() + name[1:] if len(name) > 1 else name.upper()
        
        return name
    
    def generate_meta_title(self, description: str, product_name: str = None) -> str:
        """
        AI yordamida SEO-friendly meta title generatsiya qilish
        
        Args:
            description: Mahsulot tavsifi
            product_name: Mahsulot nomi (ixtiyoriy)
        
        Returns:
            str: Generatsiya qilingan meta title (maksimal 60 belgi)
        """
        # HTML taglarini olib tashlash
        plain_text = self.strip_html_tags(description)
        
        # Agar product_name berilgan bo'lsa, undan foydalanish
        if product_name:
            base_title = product_name
        else:
            # Tavsifdan muhim so'zlarni ajratish
            lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
            if lines:
                base_title = lines[0]
                # Emoji va maxsus belgilarni olib tashlash
                base_title = re.sub(r'[^\w\s\-|]', '', base_title).strip()
            else:
                base_title = "Mahsulot"
        
        # Meta title uchun optimallashtirish
        # 1. Kategoriya yoki brend so'zlarini qo'shish (agar mavjud bo'lsa)
        text_lower = plain_text.lower()
        
        # Mashhur brendlar va kategoriyalar
        brand_keywords = ['samsung', 'apple', 'iphone', 'xiaomi', 'huawei', 'oppo', 'vivo',
                         'asus', 'acer', 'hp', 'lenovo', 'dell', 'sony', 'lg', 'nokia']
        
        category_keywords = ['smartfon', 'telefon', 'noutbuk', 'laptop', 'kompyuter',
                            'planshet', 'tablet', 'monitor', 'kamera', 'televizor']
        
        # Brendni topish
        found_brand = None
        for brand in brand_keywords:
            if brand in text_lower:
                found_brand = brand.title()
                break
        
        # Kategoriyani topish
        found_category = None
        for category in category_keywords:
            if category in text_lower:
                found_category = category.title()
                break
        
        # Meta title yaratish
        if found_brand and found_brand.lower() not in base_title.lower():
            meta_title = f"{found_brand} {base_title}"
        elif found_category and found_category.lower() not in base_title.lower():
            meta_title = f"{base_title} - {found_category}"
        else:
            meta_title = base_title
        
        # Uzunligini cheklash (60 belgi - SEO uchun optimal)
        if len(meta_title) > 60:
            # So'zlar bo'yicha kesish
            words = meta_title.split()
            meta_title = ""
            for word in words:
                if len(meta_title + " " + word) <= 57:  # 3 belgi qoldirish "..."
                    meta_title += (" " + word if meta_title else word)
                else:
                    break
            if len(meta_title) < len(base_title):
                meta_title = base_title[:57] + "..."
        
        # Tozalash
        meta_title = meta_title.strip()
        
        # Agar hali ham bo'sh yoki juda qisqa bo'lsa
        if not meta_title or len(meta_title) < 5:
            meta_title = product_name[:60] if product_name else "Mahsulot"
        
        # Birinchi harfni katta qilish
        if len(meta_title) > 1:
            meta_title = meta_title[0].upper() + meta_title[1:]
        
        return meta_title[:60]  # Maksimal 60 belgi
    
    def upload_image(self, image_path: str, image_type: str = "thumbnail") -> Optional[str]:
        """Rasm yuklash"""
        if not self.token:
            print("❌ Avval login qiling!")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ Rasm topilmadi: {image_path}")
            return None
        
        url = f"{self.BASE_URL}/seller/products/upload-images"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "user-agent": "Python/requests"
        }
        
        # Rasm fayl tipini aniqlash
        file_ext = os.path.splitext(image_path)[1].lower()
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        content_type = content_type_map.get(file_ext, 'image/jpeg')
        
        try:
            with open(image_path, 'rb') as f:
                files = {
                    'image': (os.path.basename(image_path), f, content_type)
                }
                data = {
                    'type': image_type,
                    'color': '',
                    'colors_active': 'false'
                }
                
                response = requests.post(url, headers=headers, files=files, data=data)
                if response.status_code == 200:
                    try:
                        result = response.json()
                        # Turli xil response formatlarini qo'llab-quvvatlash
                        if isinstance(result, dict):
                            # Birinchi navbatda turli xil key'larni tekshirish
                            image_name = (
                                result.get('image_name') or 
                                result.get('name') or 
                                result.get('filename') or
                                result.get('image') or
                                result.get('file_name') or
                                result.get('path')
                            )
                            
                            # Agar dict ichida yana dict bo'lsa
                            if not image_name and 'data' in result:
                                data_obj = result['data']
                                if isinstance(data_obj, dict):
                                    image_name = (
                                        data_obj.get('image_name') or
                                        data_obj.get('name') or
                                        data_obj.get('filename')
                                    )
                            
                            if image_name:
                                # Agar to'liq path bo'lsa, faqat fayl nomini olish
                                if '/' in str(image_name):
                                    image_name = str(image_name).split('/')[-1]
                                print(f"✅ Rasm yuklandi: {image_name}")
                                return str(image_name)
                        
                        # Agar string formatida bo'lsa
                        if isinstance(result, str):
                            print(f"✅ Rasm yuklandi: {result}")
                            return result
                        
                        print(f"⚠️ Rasm yuklandi, lekin format noto'g'ri: {result}")
                        # Response'dan fayl nomini qidirish
                        response_text = str(result)
                        # Pattern: yyyy-mm-dd-xxxxx.webp
                        pattern = r'\d{4}-\d{2}-\d{2}-[a-zA-Z0-9]+\.(webp|jpg|jpeg|png)'
                        match = re.search(pattern, response_text)
                        if match:
                            image_name = match.group(0)
                            print(f"✅ Rasm nomi topildi: {image_name}")
                            return image_name
                        
                        return None
                    except json.JSONDecodeError:
                        # Agar JSON bo'lmasa, text formatida qaytgan bo'lishi mumkin
                        response_text = response.text
                        # Pattern qidirish
                        pattern = r'\d{4}-\d{2}-\d{2}-[a-zA-Z0-9]+\.(webp|jpg|jpeg|png)'
                        match = re.search(pattern, response_text)
                        if match:
                            image_name = match.group(0)
                            print(f"✅ Rasm yuklandi: {image_name}")
                            return image_name
                        print(f"⚠️ JSON parse qilishda xato, lekin rasm yuklangan bo'lishi mumkin")
                        return None
                else:
                    print(f"❌ Rasm yuklash xatosi: {response.status_code}")
                    print(f"Xato javobi: {response.text[:200]}")
                    return None
        except Exception as e:
            print(f"❌ Rasm yuklash xatosi: {str(e)}")
            return None
    
    def extract_category_ids(self, category: Dict) -> Tuple[str, str, str]:
        """Kategoriya IDlarini olish"""
        category_id = str(category.get("id", ""))
        sub_category_id = ""
        sub_sub_category_id = ""
        
        # Sub-kategoriya topish
        childes = category.get("childes", [])
        if childes:
            sub_category = childes[0]  # Birinchi sub-kategoriyani olish
            sub_category_id = str(sub_category.get("id", ""))
            
            # Sub-sub-kategoriya topish
            sub_childes = sub_category.get("childes", [])
            if sub_childes:
                sub_sub_category = sub_childes[0]  # Birinchi sub-sub-kategoriyani olish
                sub_sub_category_id = str(sub_sub_category.get("id", ""))
        
        return category_id, sub_category_id, sub_sub_category_id
    
    def clean_html_description(self, html_content: str) -> str:
        """
        HTML description'ni tozalash va xavfsiz taglarni saqlash
        Ruxsat etilgan taglar: b, strong, i, em, u, ul, ol, li, h1-h6, p, br, div, span
        """
        # Ruxsat etilgan HTML taglari
        allowed_tags = [
            'b', 'strong', 'i', 'em', 'u', 's', 'strike',
            'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'div', 'span',
            'a', 'img', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
            'blockquote', 'code', 'pre'
        ]
        
        # Agar HTML bo'lmasa, oddiy text sifatida qaytarish
        if not re.search(r'<[^>]+>', html_content):
            return html_content
        
        # Xavfsiz HTML taglarini saqlash
        # Barcha ruxsat etilgan taglarni saqlash
        pattern = r'<(/?)(' + '|'.join(allowed_tags) + r')(\s[^>]*)?>'
        
        # Ruxsat etilgan taglarni saqlash
        cleaned = re.sub(
            r'<(?!\/?(?:' + '|'.join(allowed_tags) + r')(?:\s|>))[^>]+>',
            '',
            html_content,
            flags=re.IGNORECASE
        )
        
        return cleaned
    
    def strip_html_tags(self, html_content: str) -> str:
        """HTML taglarini olib tashlash (meta description uchun)"""
        # HTML taglarini olib tashlash
        text = re.sub(r'<[^>]+>', '', html_content)
        # Ko'p bo'shliqlarni bitta bo'shliqqa o'zgartirish
        text = re.sub(r'\s+', ' ', text)
        # HTML entity'larni decode qilish
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        return text.strip()
    
    def upload_product(
        self,
        description: str,
        image_path: str,
        price: float,
        name: Optional[str] = None,
        category_id: Optional[str] = None,
        brand_id: Optional[int] = None,
        stock: int = 1,
        discount: float = 0.0,
        discount_type: str = "percent"
    ) -> Dict:
        """
        Mahsulot yuklash
        
        Args:
            description: Mahsulot tavsifi
            image_path: Rasm yo'li
            price: Narx
            name: Mahsulot nomi (ixtiyoriy, tavsifdan generatsiya qilinadi)
            category_id: Kategoriya ID (ixtiyoriy, avtomatik topiladi)
            brand_id: Brend ID (ixtiyoriy, avtomatik topiladi)
            stock: Ombordagi miqdor
            discount: Chegirma foizi
            discount_type: Chegirma turi (percent yoki amount)
        
        Returns:
            Dict: Natija
        """
        if not self.token:
            if not self.login():
                return {"success": False, "error": "Login qilishda xato"}
        
        # Ma'lumotlarni yuklash
        if not self.categories:
            self.get_categories()
        if not self.brands:
            self.get_brands()
        
        # Mahsulot nomini AI yordamida generatsiya qilish
        if not name:
            name = self.generate_product_name(description)
            print(f"🤖 AI generatsiya qilgan nom: {name}")
        
        # Kategoriyani topish
        category = None
        if category_id:
            # ID bo'yicha kategoriya topish
            for cat in self.categories:
                if str(cat.get("id")) == str(category_id):
                    category = cat
                    break
        else:
            # Avtomatik kategoriya topish
            category = self.find_category_by_keywords(description, name)
        
        if not category:
            # Agar kategoriya topilmasa, birinchi kategoriyani olish
            if self.categories:
                category = self.categories[0]
            else:
                return {"success": False, "error": "Kategoriya topilmadi"}
        
        category_id, sub_category_id, sub_sub_category_id = self.extract_category_ids(category)
        
        # Brendni topish
        if not brand_id:
            brand_id = self.find_brand_by_name(description, name)
        
        if not brand_id:
            # Agar brend topilmasa, birinchi brendni olish
            if self.brands:
                brand_id = self.brands[0].get("id")
            else:
                brand_id = 1  # Default brend
        
        # Rasm yuklash
        print("📤 Rasm yuklanmoqda...")
        thumbnail_name = self.upload_image(image_path, "thumbnail")
        if not thumbnail_name:
            return {"success": False, "error": "Rasm yuklashda xato"}
        
        # Meta rasm (thumbnail bilan bir xil)
        meta_image_name = thumbnail_name
        
        # Asosiy rasm (bir xil rasmni qayta yuklash shart emas, lekin agar kerak bo'lsa)
        # Ko'pincha bir xil rasm nomi qaytariladi
        main_image_name = self.upload_image(image_path, "main")
        if not main_image_name:
            main_image_name = thumbnail_name
        
        # Rasm ma'lumotlarini tayyorlash
        images_data = [{
            "image_name": main_image_name,
            "storage": "public"
        }]
        
        # Description'ni HTML formatida tozalash
        html_description = self.clean_html_description(description)
        
        # Meta description uchun HTML taglarini olib tashlash
        plain_description = self.strip_html_tags(description)
        
        # Meta title ni AI yordamida generatsiya qilish
        meta_title = self.generate_meta_title(description, name)
        print(f"🤖 AI generatsiya qilgan meta title: {meta_title}")
        
        # Mahsulot ma'lumotlarini tayyorlash
        product_data = {
            "name": json.dumps([name], ensure_ascii=False),
            "description": json.dumps([html_description], ensure_ascii=False),
            "unit_price": price,
            "discount": discount,
            "discount_type": discount_type,
            "tax_ids": "[]",
            "tax_model": "exclude",
            "category_id": category_id,
            "unit": "pc",
            "brand_id": brand_id,
            "meta_title": meta_title,
            "meta_description": plain_description[:160] if plain_description else "",
            "lang": json.dumps(["ru"], ensure_ascii=False),
            "colors": "[]",
            "images": json.dumps(images_data, ensure_ascii=False),
            "thumbnail": thumbnail_name,
            "colors_active": False,
            "video_url": "",
            "meta_image": meta_image_name,
            "current_stock": stock,
            "shipping_cost": 0.0,
            "multiply_qty": 0,
            "code": os.urandom(3).hex().upper(),
            "minimum_order_qty": 1,
            "product_type": "physical",
            "digital_product_type": "ready_after_sell",
            "digital_file_ready": "",
            "tags": json.dumps(["tag", "product"], ensure_ascii=False),
            "publishing_house": "[]",
            "authors": "[]",
            "color_image": "[]",
            "meta_index": "1",
            "meta_no_follow": "",
            "meta_no_image_index": "0",
            "meta_no_archive": "0",
            "meta_no_snippet": "0",
            "meta_max_snippet": "0",
            "meta_max_snippet_value": None,
            "meta_max_video_preview": "0",
            "meta_max_video_preview_value": None,
            "meta_max_image_preview": "0",
            "meta_max_image_preview_value": "large",
            "sub_category_id": sub_category_id if sub_category_id else category_id,
            "sub_sub_category_id": sub_sub_category_id if sub_sub_category_id else (sub_category_id if sub_category_id else category_id),
            "tax": "0",

            # Remove in feature
            "weight": 0.0,
            "height": 0.0,
            "width": 0.0,
            "length": 0.0,
            
            "package_code": "121212",
            "mxik":"121212",

            "is_install":False,
            "is_seasonal":False,
            "is_discount":False,
        }
        
        # Mahsulot yaratish
        url = f"{self.BASE_URL}/seller/products/add"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Python/requests"
        }
        
        try:
            print("📦 Mahsulot yuklanmoqda...")
            response = requests.post(url, json=product_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Mahsulot muvaffaqiyatli yuklandi!")
                return {
                    "success": True,
                    "message": "Mahsulot muvaffaqiyatli yuklandi!",
                    "data": result
                }
            else:
                error_msg = response.text
                print(f"❌ Mahsulot yuklash xatosi: {response.status_code}")
                print(f"Xato: {error_msg}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_msg}",
                    "status_code": response.status_code
                }
        except Exception as e:
            print(f"❌ Mahsulot yuklash xatosi: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def initialize(self):
        """Barcha kerakli ma'lumotlarni yuklash"""
        print("🔄 Tizim ishga tushmoqda...")
        if not self.login():
            return False
        
        self.get_categories()
        self.get_brands()
        self.get_attributes()
        
        print("✅ Tizim tayyor!")
        return True


# Foydalanish misoli
if __name__ == "__main__":
    # Do'kon ma'lumotlari
    # Iltimos, o'z email va parolingizni kiriting
    EMAIL = os.getenv("VENU_EMAIL", "your_email@venu.uz")
    PASSWORD = os.getenv("VENU_PASSWORD", "your_password")
    
    # Agent yaratish
    agent = ProductUploaderAgent(EMAIL, PASSWORD)
    
    # Tizimni ishga tushirish
    if agent.initialize():
        # Mahsulot yuklash
        result = agent.upload_product(
            description="Yangi smartfon - ajoyib xususiyatlar bilan",
            image_path="test_rasm.png",  # Rasm yo'li
            price=500000.0,  # Narx
            stock=5,  # Ombordagi miqdor
            discount=10.0  # 10% chegirma
        )
        
        if result["success"]:
            print("\n🎉 Mahsulot muvaffaqiyatli yuklandi!")
        else:
            print(f"\n❌ Xato: {result.get('error', 'Nomalum xato')}")
