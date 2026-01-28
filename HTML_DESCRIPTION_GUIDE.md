# HTML Description Qo'llanmasi

Bu qo'llanma mahsulot description'ida HTML taglaridan qanday foydalanishni ko'rsatadi.

## Qo'llab-quvvatlanadigan HTML taglar

### Matn formatlash
- `<b>` - Qalin matn
- `<strong>` - Muhim matn (qalin)
- `<i>` - Kursiv matn
- `<em>` - Ta'kidlangan matn (kursiv)
- `<u>` - Chiziqli matn
- `<s>` yoki `<strike>` - O'chirilgan matn

### Ro'yxatlar
- `<ul>` - Tartibsiz ro'yxat
- `<ol>` - Tartibli ro'yxat
- `<li>` - Ro'yxat elementi

### Sarlavhalar
- `<h1>` - Eng katta sarlavha
- `<h2>` - Katta sarlavha
- `<h3>` - O'rta sarlavha
- `<h4>` - Kichik sarlavha
- `<h5>` - Juda kichik sarlavha
- `<h6>` - Eng kichik sarlavha

### Paragraflar va bo'linishlar
- `<p>` - Paragraf
- `<br>` - Qator o'tkazish
- `<div>` - Blok element
- `<span>` - Inline element

### Boshqa taglar
- `<a>` - Havola
- `<img>` - Rasm
- `<table>`, `<tr>`, `<td>`, `<th>`, `<thead>`, `<tbody>` - Jadval
- `<blockquote>` - Iqtibos
- `<code>` - Kod
- `<pre>` - Formatlangan kod

## Misollar

### Misol 1: Oddiy formatlash

```html
<h1>Mahsulot nomi</h1>
<p>Bu <strong>ajoyib</strong> mahsulot!</p>
<p>Narxi: <b>500,000</b> so'm</p>
```

### Misol 2: Ro'yxatlar

```html
<h2>Xususiyatlar:</h2>
<ul>
    <li><b>Yuqori sifat</b></li>
    <li><b>Uzoq muddatli</b></li>
    <li><b>Zamonaviy dizayn</b></li>
</ul>
```

### Misol 3: Sarlavhalar va paragraflar

```html
<h1>Samsung Galaxy S24</h1>
<h2>Asosiy xususiyatlar</h2>
<p>Eng yangi flagship smartfon</p>

<h3>Texnik xususiyatlar</h3>
<ul>
    <li>6.8 dyuymli ekran</li>
    <li>12GB RAM</li>
    <li>256GB xotira</li>
</ul>
```

### Misol 4: To'liq misol

```html
<h1>Yangi Smartfon</h1>
<p>Ajoyib <strong>xususiyatlar</strong> bilan!</p>

<h2>Asosiy xususiyatlar:</h2>
<ul>
    <li><b>48MP</b> asosiy kamera</li>
    <li><b>128GB</b> ichki xotira</li>
    <li><b>5000mAh</b> batareya</li>
    <li><b>IP68</b> suvdan himoya</li>
</ul>

<h2>Qo'shimcha ma'lumotlar:</h2>
<p>Bu smartfon eng zamonaviy texnologiyalar bilan jihozlangan va uzoq muddat ishlash uchun mo'ljallangan.</p>

<h3>Kafolat:</h3>
<ol>
    <li>1 yil rasmiy kafolat</li>
    <li>Bepul yetkazib berish</li>
    <li>24/7 texnik yordam</li>
</ol>
```

## Foydalanish

```python
from product_uploader import ProductUploaderAgent

agent = ProductUploaderAgent("email@venu.uz", "password")
agent.initialize()

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
    image_path="image.jpg",
    price=500000.0
)
```

## Eslatmalar

1. **Xavfsizlik**: Faqat ruxsat etilgan taglar saqlanadi, boshqalari avtomatik olib tashlanadi
2. **Meta description**: HTML taglari meta description uchun avtomatik olib tashlanadi
3. **Kategoriya/Brend topish**: HTML taglari kategoriya va brend topishda avtomatik olib tashlanadi
4. **Formatlash**: HTML to'g'ri formatlangan bo'lishi kerak (yopilgan taglar)

## Maslahatlar

- Sarlavhalarni mantiqiy tartibda ishlating (h1 → h2 → h3)
- Ro'yxatlarni to'g'ri yoping (`</ul>`, `</ol>`, `</li>`)
- Paragraflarni `<p>` taglari bilan ajrating
- Muhim matnlarni `<strong>` yoki `<b>` bilan ajrating
