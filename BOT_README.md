# Telegram Bot - Venu Marketplace Product Uploader

Bu Telegram bot Venu marketplace do'konlariga mahsulot qo'shishga yordam beradi.

## O'rnatish

1. Kerakli kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

2. Bot tokenini o'rnating:
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
```

Bot tokenini olish uchun [@BotFather](https://t.me/BotFather) ga murojaat qiling.

## Ishga tushirish

```bash
python telegram_bot.py
```

## Foydalanish

1. Botni `/start` buyrug'i bilan boshlang
2. Do'kon email manzilini yuboring
3. Do'kon parolini yuboring
4. Mahsulot rasmini yuboring
5. Mahsulot tavsifini yuboring (HTML formatida yoki oddiy matn)
6. Mahsulot narxini yuboring
7. Ombordagi miqdorni kiriting (ixtiyoriy, default: 10)
8. Chegirma foizini kiriting (ixtiyoriy, default: 0)

Mahsulot muvaffaqiyatli yuklangandan keyin quyidagi buttonlar ko'rsatiladi:
- **➕ Yana yangi mahsulot qo'shish** - Xuddi shu do'konga yana mahsulot qo'shish
- **🔄 Boshqa do'konga mahsulot qo'shish** - Boshqa do'kon ma'lumotlari bilan yangi mahsulot qo'shish
- **✅ Tugatish** - Botdan chiqish

## Xususiyatlar

- ✅ Email va parol tekshiruvi
- ✅ Rasm yuklash (rasm yoki fayl sifatida)
- ✅ HTML formatida tavsif qo'llab-quvvatlash
- ✅ Avtomatik kategoriya va brend topish
- ✅ Ombordagi miqdor va chegirma sozlash
- ✅ Muvaffaqiyatli yuklagandan keyin buttonlar

## Eslatmalar

- Bot tokenini xavfsiz saqlang
- Rasm fayllari vaqtinchalik saqlanadi va yuklangandan keyin o'chiriladi
- Agar login xatosi bo'lsa, qaytadan email va parol kiriting
