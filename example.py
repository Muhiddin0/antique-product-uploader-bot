"""
Mahsulot yuklash misoli
"""

from product_uploader import ProductUploaderAgent

def main():
    # Do'kon ma'lumotlari
    # Iltimos, o'z email va parolingizni kiriting
    EMAIL = "your_email@venu.uz"
    PASSWORD = "your_password"
    
    # Agent yaratish
    print("🤖 Product Uploader Agent ishga tushmoqda...\n")
    agent = ProductUploaderAgent(EMAIL, PASSWORD)
    
    # Tizimni ishga tushirish
    if not agent.initialize():
        print("❌ Tizimni ishga tushirishda xato!")
        return
    
    # Mahsulot ma'lumotlari (HTML formatida)
    product_description = """
🌸 New Collection 2026 | 100% Silk
✨ O‘zbekiston Milliy Hunarmandchiligi — Qo‘lda Kashta Tikilgan Antiqa Buyum

Bu nafis buyum — O‘zbekiston qadimiy hunarmandchiligi an’analari va zamonaviy dizayn uyg‘unligining yorqin namunasi. 100% sof ipak matodan tayyorlangan bo‘lib, har bir kashta naqshi qo‘lda, sabr va mahorat bilan ishlangan.

🌿 Naqshlar ma’nosi
Gul va barglardan iborat kashta naqshlar Sharqona baraka, go‘zallik va hayotiylik ramzi hisoblanadi. Ranglar uyg‘unligi esa buyumga nafislik va qimmatbaho ko‘rinish beradi.

💎 Asosiy xususiyatlar:

🧵 100% tabiiy ipak (Silk)

✋ To‘liq qo‘lda tikilgan kashta

🎨 An’anaviy o‘zbek naqshlari

🔔 Pastki qismida mayin bezakli osma elementlar

📦 New Collection 2026

🌍 Ekologik va noyob hunarmandchilik mahsuloti

👗 Qayerda mos keladi?

Milliy liboslar bilan

Fotosessiya va sahna chiqishlari

Kolleksionerlar uchun antiqa buyum

Sovg‘a sifatida juda qimmatli tanlov

⚜️ Noyoblik kafolati
Bu mahsulot ommaviy ishlab chiqarilmaydi. Har bir nusxa — takrorlanmas, o‘ziga xos san’at asari.
    """
    
    # Mahsulot yuklash
    print("\n📦 Mahsulot yuklanmoqda...\n")
    result = agent.upload_product(
        description=product_description.strip(),
        image_path="test_rasm.png",  # Rasm yo'lini o'zgartiring
        price=15000000.0,  # 15 million so'm
        stock=5,
        discount=10.0,  # 10% chegirma
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