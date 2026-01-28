# Venu Marketplace Product Uploader Bot

Bu loyiha Venu marketplace'ga mahsulotlarni avtomatik yuklash uchun AI agent class'ini o'z ichiga oladi.

## Xususiyatlar

- ✅ Avtomatik login va autentifikatsiya
- ✅ Kategoriya, brend va atributlarni avtomatik topish
- ✅ Rasm yuklash
- ✅ Mahsulot ma'lumotlarini avtomatik to'ldirish
- ✅ AI agent - qolgan maydonlarni o'zi to'ldiradi
- ✅ **HTML description qo'llab-quvvatlash** - b, strong, ul, ol, li, h1-h6, p, br va boshqa HTML taglar

## O'rnatish

```bash
pip install -r requirements.txt
```

## Foydalanish

### Asosiy foydalanish

```python
from product_uploader import ProductUploaderAgent

# Do'kon ma'lumotlari
EMAIL = "your_email@venu.uz"
PASSWORD = "your_password"

# Agent yaratish
agent = ProductUploaderAgent(EMAIL, PASSWORD)

# Tizimni ishga tushirish
if agent.initialize():
    # Mahsulot yuklash (HTML description bilan)
    html_description = """
    <h1>Mahsulot nomi</h1>
    <p>Ajoyib <strong>xususiyatlar</strong> bilan!</p>
    <ul>
        <li>Birinchi xususiyat</li>
        <li>Ikkinchi xususiyat</li>
    </ul>
    """
    
    result = agent.upload_product(
        description=html_description.strip(),
        image_path="path/to/image.jpg",
        price=500000.0,
        stock=10,
        discount=10.0
    )
    
    if result["success"]:
        print("✅ Mahsulot muvaffaqiyatli yuklandi!")
    else:
        print(f"❌ Xato: {result.get('error')}")
```

### Batafsil foydalanish

```python
from product_uploader import ProductUploaderAgent

agent = ProductUploaderAgent("email@venu.uz", "password")

# Login qilish
agent.login()

# Kategoriyalarni yuklash
agent.get_categories()

# Brendlarni yuklash
agent.get_brands()

# Mahsulot yuklash (barcha parametrlar bilan)
result = agent.upload_product(
    description="Yangi smartfon - ajoyib xususiyatlar bilan. "
                "Yuqori sifatli kamera, kuchli protsessor va uzoq ishlaydigan batareya.",
    image_path="smartphone.jpg",
    price=5000000.0,
    name="Samsung Galaxy S24",  # Ixtiyoriy
    category_id="422",  # Ixtiyoriy - avtomatik topiladi
    brand_id=14,  # Ixtiyoriy - avtomatik topiladi
    stock=5,
    discount=15.0,
    discount_type="percent"
)
```

## Parametrlar

### `upload_product()` metodi

- `description` (required): Mahsulot tavsifi
- `image_path` (required): Rasm fayl yo'li
- `price` (required): Mahsulot narxi
- `name` (optional): Mahsulot nomi (bo'lmasa tavsifdan generatsiya qilinadi)
- `category_id` (optional): Kategoriya ID (bo'lmasa avtomatik topiladi)
- `brand_id` (optional): Brend ID (bo'lmasa avtomatik topiladi)
- `stock` (optional): Ombordagi miqdor (default: 10)
- `discount` (optional): Chegirma foizi (default: 0.0)
- `discount_type` (optional): Chegirma turi - "percent" yoki "amount" (default: "percent")

## Avtomatik funksiyalar

Agent quyidagi maydonlarni avtomatik to'ldiradi:

1. **Kategoriya**: Mahsulot tavsifidan kategoriyani topadi
2. **Brend**: Mahsulot nomi va tavsifidan brendni aniqlaydi
3. **Mahsulot kodi**: 6 belgili random kod generatsiya qiladi
4. **Meta ma'lumotlar**: SEO uchun meta title va description
5. **Rasm**: Rasmni yuklab, thumbnail va asosiy rasm sifatida saqlaydi

## Xatolar

Agar xato yuzaga kelsa, `result` dict'ida quyidagi ma'lumotlar bo'ladi:

```python
{
    "success": False,
    "error": "Xato xabari",
    "status_code": 400  # HTTP status code (agar mavjud bo'lsa)
}
```

## Misollar

### Misol 1: Oddiy mahsulot yuklash (HTML bilan)

```python
agent = ProductUploaderAgent("email@venu.uz", "password")
agent.initialize()

html_desc = """
<h2>Yangi Noutbuk</h2>
<p><strong>Intel Core i7</strong>, <strong>16GB RAM</strong>, <strong>512GB SSD</strong></p>
<ul>
    <li>Yuqori unumdorlik</li>
    <li>Tez ishlash</li>
</ul>
"""

result = agent.upload_product(
    description=html_desc.strip(),
    image_path="laptop.jpg",
    price=12000000.0
)
```

### Misol 2: Chegirma bilan mahsulot (HTML bilan)

```python
html_desc = """
<h1>Smartfon</h1>
<p><b>128GB</b> xotira, <b>48MP</b> kamera</p>
<ol>
    <li>Yuqori sifatli kamera</li>
    <li>Katta xotira</li>
    <li>Tez ishlash</li>
</ol>
"""

result = agent.upload_product(
    description=html_desc.strip(),
    image_path="phone.jpg",
    price=3000000.0,
    discount=20.0,  # 20% chegirma
    stock=3
)
```

## Eslatmalar

- Rasm fayli mavjud bo'lishi kerak
- Email va parol to'g'ri bo'lishi kerak
- Internet ulanishi bo'lishi kerak
- API key fayl ichida hardcoded (production uchun environment variable ishlatish tavsiya etiladi)

## Muammolar

Agar muammo yuzaga kelsa:

1. Login qilishni tekshiring
2. Rasm fayl yo'lini tekshiring
3. Internet ulanishini tekshiring
4. API endpoint'larni tekshiring

## Rivojlantirish

- [ ] Environment variables qo'llab-quvvatlash
- [ ] Ko'p rasm yuklash
- [ ] Batch upload (bir nechta mahsulot)
- [ ] Logging tizimi
- [ ] Error handling yaxshilash
