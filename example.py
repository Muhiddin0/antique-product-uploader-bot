"""
Mahsulot yuklash misoli
"""

from product_uploader import ProductUploaderAgent

def main():
    # Do'kon ma'lumotlari
    # Iltimos, o'z email va parolingizni kiriting

    # Venu
    # EMAIL = "themodestn@venu.uz"
    # PASSWORD = "Themodestn@venu3001.uz"

    # Antique
    EMAIL = "testdokon@antik.uz"
    PASSWORD = "Testdokon@antik.uz2026"
    
    # Agent yaratish
    print("🤖 Product Uploader Agent ishga tushmoqda...\n")
    agent = ProductUploaderAgent(EMAIL, PASSWORD)
    
    # Tizimni ishga tushirish
    if not agent.initialize():
        print("❌ Tizimni ishga tushirishda xato!")
        return
    
    # Mahsulot ma'lumotlari (oddiy matn - AI avtomatik HTML formatiga o'tkazadi)
    # Test uchun elektronika kategoriyasiga mos mahsulot
    product_description = """
Detail Description
These handcrafted golden yellow and burgundy embroidered traditional flats combine vibrant colors with timeless artisan craftsmanship. Each pair is carefully handmade by skilled artisans, reflecting cultural heritage through detailed embroidery and refined finishing.

The warm golden yellow base is beautifully accented with rich burgundy, teal, black, and ivory tones, creating elegant floral and geometric patterns inspired by traditional motifs. High-quality embroidery threads ensure excellent durability, color retention, and resistance to fading, allowing the design to remain vibrant over time.

The breathable woven textile upper provides natural flexibility and adapts comfortably to the shape of the foot. The classic closed-toe slip-on silhouette allows easy wear, while the cushioned insole offers reliable support for extended comfort. The smooth inner lining minimizes friction and enhances overall wearability.

Finished with premium leather-trimmed edges, these flats feature added strength, structure, and a polished appearance. The durable outsole delivers stable grip and long-lasting performance, making them suitable for everyday wear, cultural gatherings, travel, and special occasions.

These embroidered flats pair effortlessly with traditional dresses, ethnic outfits, casual ensembles, and modern fashion styles. Each pair is unique, showcasing authentic handcraft artistry and cultural expression. Designed for women who appreciate elegance, comfort, and individuality, these flats are a refined addition to any footwear collection
"""
    
    # Mahsulot yuklash
    # Eslatma: AI agent oddiy matnni avtomatik HTML formatiga o'tkazadi
    print("\n📦 Mahsulot yuklanmoqda...\n")
    print("🤖 AI agent tavsifni HTML formatiga o'tkazmoqda...\n")
    result = agent.upload_product(
        description=product_description.strip(),
        image_path="test_rasm.png",  # Rasm yo'lini o'zgartiring
        price=12000000.0,  # 12 million so'm
        stock=3,
        discount=5.0,  # 5% chegirma
        discount_type="percent"
    )
    
    # Natijani ko'rsatish
    print("\n" + "="*50)
    if result["success"]:
        print("✅ MAHSULOT MUVAFFAQIYATLI YUKLANDI!")
        print(f"📝 Xabar: {result.get('message', 'Nomalum xato')}")
        if "data" in result:
            print(f"📊 Ma'lumotlar: {result['data']}")
    else:
        print("❌ MAHSULOT YUKLASHDA XATO!")
        print(f"🔴 Xato: {result.get('error', 'Nomalum xato')}")
        if "status_code" in result:
            print(f"📊 Status code: {result['status_code']}")
    print("="*50)

if __name__ == "__main__":
    main()