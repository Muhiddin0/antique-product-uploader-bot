"""
Telegram Bot - Venu Marketplace Product Uploader
Do'konga mahsulot kiritsh uchun Telegram bot
"""

import os
import logging
import re
from typing import Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from product_uploader import ProductUploaderAgent

from dotenv import load_dotenv

load_dotenv()


# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation holatlari
WAITING_EMAIL, WAITING_PASSWORD, WAITING_IMAGE, WAITING_DESCRIPTION, WAITING_PRICE, WAITING_DISCOUNT = range(6)

# User ma'lumotlarini saqlash
user_data: Dict[int, Dict] = {}


def enrich_text_with_html(plain_text: str) -> str:
    """
    Oddiy matnni HTML taglar bilan boyitish.
    Agar matn allaqachon HTML bo'lsa, o'zgartirmaydi.
    """
    # Agar matn allaqachon HTML taglariga ega bo'lsa, o'zgartirmaydi
    if re.search(r'<[^>]+>', plain_text):
        return plain_text
    
    lines = plain_text.split('\n')
    html_parts = []
    in_list = False
    in_paragraph = False
    current_paragraph = []
    heading_count = 0  # Sarlavhalar sonini kuzatish
    
    # Emoji pattern - barcha emoji turlarini qamrab oladi
    emoji_pattern = re.compile(
        r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F'
        r'\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0'
        r'\U000024C2-\U0001F251]'
    )
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Bo'sh qator - paragraf yoki ro'yxatni yopish
        if not line:
            if in_paragraph and current_paragraph:
                html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                current_paragraph = []
                in_paragraph = False
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            i += 1
            continue
        
        # Emoji bilan boshlanadigan qatorlarni tekshirish
        if emoji_pattern.match(line):
            # Paragrafni yopish
            if in_paragraph and current_paragraph:
                html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                current_paragraph = []
                in_paragraph = False
            
            # Keyingi qatorlarni tekshirish
            next_line_empty = (i + 1 >= len(lines) or not lines[i + 1].strip())
            next_line_emoji = False
            if i + 1 < len(lines) and lines[i + 1].strip():
                next_line_emoji = bool(emoji_pattern.match(lines[i + 1].strip()))
            
            # Emoji keyin matn bor yoki yo'qligini tekshirish
            # Agar emoji keyin darhol matn bo'lsa va keyingi qator bo'sh/emoji bo'lmasa, bu ro'yxat elementi
            text_after_emoji = line[1:].strip() if len(line) > 1 else ""
            is_list_item = bool(text_after_emoji and not next_line_empty and not next_line_emoji)
            
            # Agar keyingi qator bo'sh yoki yangi emoji bilan boshlansa, bu sarlavha
            if next_line_empty or next_line_emoji or not text_after_emoji:
                # Ro'yxatni yopish
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                
                # Sarlavha darajasini aniqlash
                heading_count += 1
                if heading_count == 1:
                    html_parts.append(f"<h2>{line}</h2>")
                else:
                    html_parts.append(f"<h3>{line}</h3>")
            else:
                # Ro'yxat elementi
                if not in_list:
                    html_parts.append("<ul>")
                    in_list = True
                # Emoji va matnni ajratish
                html_parts.append(f"<li><strong>{text_after_emoji}</strong></li>")
        else:
            # Oddiy matn - paragrafga qo'shish
            # Agar qator ":" bilan tugasa va qisqa bo'lsa, bu sarlavha bo'lishi mumkin
            if line.endswith(':') and len(line) < 60:
                # Paragrafni yopish
                if in_paragraph and current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                    in_paragraph = False
                # Ro'yxatni yopish
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                # Sarlavha sifatida qo'shish
                heading_count += 1
                html_parts.append(f"<h3>{line}</h3>")
            else:
                # Oddiy paragraf
                if not in_paragraph:
                    in_paragraph = True
                    current_paragraph = []
                current_paragraph.append(line)
        
        i += 1
    
    # Qolgan paragrafni yopish
    if in_paragraph and current_paragraph:
        html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
    
    # Qolgan ro'yxatni yopish
    if in_list:
        html_parts.append("</ul>")
    
    result = '\n'.join(html_parts)
    
    # Agar hech narsa qaytmasa, oddiy paragraf sifatida qaytarish
    if not result.strip():
        return f"<p>{plain_text.strip()}</p>"
    
    return result


def get_user_data(user_id: int) -> Dict:
    """User ma'lumotlarini olish"""
    if user_id not in user_data:
        user_data[user_id] = {
            'agent': None,
            'email': None,
            'password': None,
            'image_path': None,
            'description': None,
            'price': None,
            'stock': 1,
            'discount': 0.0
        }
    return user_data[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Botni boshlash"""
    user_id = update.effective_user.id
    user_data_dict = get_user_data(user_id)
    
    # Eski ma'lumotlarni tozalash
    user_data_dict['agent'] = None
    user_data_dict['email'] = None
    user_data_dict['password'] = None
    user_data_dict['image_path'] = None
    user_data_dict['description'] = None
    user_data_dict['price'] = None
    user_data_dict['stock'] = 1
    user_data_dict['discount'] = 0.0
    
    await update.message.reply_text(
        "👋 Assalomu alaykum! Venu Marketplace mahsulot yuklovchi botiga xush kelibsiz!\n\n"
        "Bot do'konga mahsulot qo'shishga yordam beradi.\n\n"
        "Boshlash uchun do'kon email manzilini yuboring:"
    )
    return WAITING_EMAIL


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Email qabul qilish"""
    user_id = update.effective_user.id
    email = update.message.text.strip()
    
    # Email formatini tekshirish
    if '@' not in email or '.' not in email:
        await update.message.reply_text(
            "❌ Email formati noto'g'ri. Iltimos, to'g'ri email manzilini kiriting:\n"
            "Masalan: example@venu.uz"
        )
        return WAITING_EMAIL
    
    user_data_dict = get_user_data(user_id)
    user_data_dict['email'] = email
    
    await update.message.reply_text(
        f"✅ Email qabul qilindi: {email}\n\n"
        "Endi do'kon parolini yuboring:"
    )
    return WAITING_PASSWORD


async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Password qabul qilish va login tekshirish"""
    user_id = update.effective_user.id
    password = update.message.text.strip()
    
    user_data_dict = get_user_data(user_id)
    user_data_dict['password'] = password
    
    await update.message.reply_text("⏳ Login tekshirilmoqda...")
    
    # Agent yaratish va login tekshirish
    try:
        agent = ProductUploaderAgent(user_data_dict['email'], password)
        if agent.login():
            user_data_dict['agent'] = agent
            # Kategoriya va brendlarni yuklash
            agent.get_categories()
            agent.get_brands()
            
            await update.message.reply_text(
                "✅ Muvaffaqiyatli login qilindi!\n\n"
                "Endi mahsulot rasmini yuboring (rasm fayl sifatida):"
            )
            return WAITING_IMAGE
        else:
            await update.message.reply_text(
                "❌ Login xatosi! Email yoki parol noto'g'ri.\n\n"
                "Qaytadan email manzilini yuboring:"
            )
            return WAITING_EMAIL
    except Exception as e:
        logger.error(f"Login xatosi: {str(e)}")
        await update.message.reply_text(
            f"❌ Xato yuz berdi: {str(e)}\n\n"
            "Qaytadan email manzilini yuboring:"
        )
        return WAITING_EMAIL


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Rasm qabul qilish"""
    user_id = update.effective_user.id
    user_data_dict = get_user_data(user_id)
    
    # Rasm faylini olish
    if update.message.photo:
        # Eng katta rasmni olish
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
    elif update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
    else:
        await update.message.reply_text(
            "❌ Iltimos, rasm faylini yuboring (rasm yoki fayl sifatida):"
        )
        return WAITING_IMAGE
    
    # Rasmni saqlash
    try:
        # Temp papkasini yaratish
        os.makedirs('temp_images', exist_ok=True)
        
        # Fayl nomini generatsiya qilish
        file_extension = os.path.splitext(file.file_path or 'image.jpg')[1] or '.jpg'
        image_filename = f"temp_images/{user_id}_{photo.file_id if update.message.photo else update.message.document.file_id}{file_extension}"
        
        # Rasmni yuklab olish
        await file.download_to_drive(image_filename)
        user_data_dict['image_path'] = image_filename
        
        await update.message.reply_text(
            "✅ Rasm qabul qilindi!\n\n"
            "Endi mahsulot tavsifini yuboring (HTML formatida yoki oddiy matn):"
        )
        return WAITING_DESCRIPTION
    except Exception as e:
        logger.error(f"Rasm yuklash xatosi: {str(e)}")
        await update.message.reply_text(
            f"❌ Rasm yuklashda xato: {str(e)}\n\n"
            "Qaytadan rasm yuboring:"
        )
        return WAITING_IMAGE


async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Tavsif qabul qilish va AI yordamida HTML bilan boyitish"""
    user_id = update.effective_user.id
    description = update.message.text.strip()
    
    if not description:
        await update.message.reply_text(
            "❌ Tavsif bo'sh bo'lishi mumkin emas. Qaytadan yuboring:"
        )
        return WAITING_DESCRIPTION
    
    user_data_dict = get_user_data(user_id)
    
    # Agent mavjudligini tekshirish
    if not user_data_dict.get('agent'):
        await update.message.reply_text(
            "❌ Agent topilmadi. Qaytadan /start buyrug'ini yuboring."
        )
        return ConversationHandler.END
    
    # AI yordamida oddiy matnni HTML formatiga o'tkazish
    await update.message.reply_text("🤖 AI yordamida tavsifni HTML formatiga o'tkazilmoqda...")
    
    try:
        agent = user_data_dict['agent']
        enriched_description = agent.convert_text_to_html_with_ai(description)
        user_data_dict['description'] = enriched_description
        
        await update.message.reply_text(
            "✅ Tavsif qabul qilindi va AI yordamida HTML taglar bilan chiroyli ko'rinishga keltirildi!\n\n"
            "Endi mahsulot narxini yuboring (dollarda, faqat raqam):\n"
            "Masalan: 100 yoki 100.50"
        )
        return WAITING_PRICE
    except Exception as e:
        logger.error(f"Tavsifni HTML formatiga o'tkazishda xato: {str(e)}")
        # Xato bo'lsa, oddiy formatlashdan foydalanish
        enriched_description = enrich_text_with_html(description)
        user_data_dict['description'] = enriched_description
        
        await update.message.reply_text(
            "✅ Tavsif qabul qilindi va HTML taglar bilan boyitildi!\n\n"
            "Endi mahsulot narxini yuboring (dollarda, faqat raqam):\n"
            "Masalan: 100 yoki 100.50"
        )
        return WAITING_PRICE


async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Narx qabul qilish (dollarda)"""
    user_id = update.effective_user.id
    price_text = update.message.text.strip()
    
    try:
        original_price = float(price_text.replace(',', '').replace(' ', ''))
        if original_price <= 0:
            raise ValueError("Narx musbat bo'lishi kerak")
    except ValueError:
        await update.message.reply_text(
            "❌ Narx noto'g'ri formatda. Faqat raqam kiriting:\n"
            "Masalan: 100 yoki 100.50"
        )
        return WAITING_PRICE
    
    # 15% qo'shish
    price_with_margin = original_price * 1.15
    
    user_data_dict = get_user_data(user_id)
    user_data_dict['price'] = price_with_margin  # 15% qo'shilgan narxni saqlash
    user_data_dict['stock'] = 1  # Default miqdor har doim 1
    
    # Skip button yaratish
    keyboard = [
        [InlineKeyboardButton("⏭️ Skip (0% chegirma)", callback_data='skip_discount')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Narx qabul qilindi: ${original_price:,.2f}\n"
        f"💲 15% pul qo'shilidi\n"
        f"📊 Yangi narx: ${price_with_margin:,.2f}\n\n"
        "Chegirma foizini kiriting (ixtiyoriy, default: 0):\n"
        "Masalan: 10 (10% chegirma) yoki skip buttonini bosing:",
        reply_markup=reply_markup
    )
    return WAITING_DISCOUNT


async def handle_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Chegirma qabul qilish va mahsulotni yuklash"""
    user_id = update.effective_user.id
    discount_text = update.message.text.strip().lower()
    
    user_data_dict = get_user_data(user_id)
    
    if discount_text in ['skip', "o'tkazib yuborish", 'otkazib yuborish', 'default', '0', '']:
        user_data_dict['discount'] = 0.0
    else:
        try:
            discount = float(discount_text.replace('%', '').replace(',', '.'))
            if discount < 0 or discount > 100:
                raise ValueError("Chegirma 0-100% orasida bo'lishi kerak")
            user_data_dict['discount'] = discount
        except ValueError:
            # Skip button yaratish
            keyboard = [
                [InlineKeyboardButton("⏭️ Skip (0% chegirma)", callback_data='skip_discount')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ Chegirma noto'g'ri formatda. 0-100 orasida raqam kiriting:\n"
                "Masalan: 10 yoki skip buttonini bosing:",
                reply_markup=reply_markup
            )
            return WAITING_DISCOUNT
    
    # Mahsulotni yuklash
    await update.message.reply_text("⏳ Mahsulot yuklanmoqda...")
    
    try:
        agent = user_data_dict['agent']
        result = agent.upload_product(
            description=user_data_dict['description'],
            image_path=user_data_dict['image_path'],
            price=user_data_dict['price'],
            stock=user_data_dict['stock'],
            discount=user_data_dict['discount']
        )
        
        # Temp rasmni o'chirish
        try:
            if os.path.exists(user_data_dict['image_path']):
                os.remove(user_data_dict['image_path'])
        except:
            pass
        
        if result.get('success'):
            # Muvaffaqiyatli yuklangan buttonlar
            keyboard = [
                [
                    InlineKeyboardButton("➕ Yana yangi mahsulot qo'shish", callback_data='new_product'),
                    InlineKeyboardButton("🔄 Boshqa do'konga mahsulot qo'shish", callback_data='new_store')
                ],
                [
                    InlineKeyboardButton("✅ Tugatish", callback_data='finish')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ Mahsulot muvaffaqiyatli yuklandi!\n\n"
                f"📝 Xabar: {result.get('message', 'Muvaffaqiyatli')}",
                reply_markup=reply_markup
            )
            return ConversationHandler.END
        else:
            error_msg = result.get('error', 'Nomalum xato')
            await update.message.reply_text(
                f"❌ Mahsulot yuklashda xato:\n{error_msg}\n\n"
                "Qaytadan boshlash uchun /start buyrug'ini yuboring."
            )
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Mahsulot yuklash xatosi: {str(e)}")
        await update.message.reply_text(
            f"❌ Xato yuz berdi: {str(e)}\n\n"
            "Qaytadan boshlash uchun /start buyrug'ini yuboring."
        )
        return ConversationHandler.END


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Button callback handler"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == 'new_product':
        # Yana yangi mahsulot qo'shish
        user_data_dict = get_user_data(user_id)
        # Agent va email/password saqlanadi, faqat mahsulot ma'lumotlarini tozalash
        user_data_dict['image_path'] = None
        user_data_dict['description'] = None
        user_data_dict['price'] = None
        user_data_dict['stock'] = 1
        user_data_dict['discount'] = 0.0
        
        await query.edit_message_text(
            "✅ Yana yangi mahsulot qo'shish!\n\n"
            "Mahsulot rasmini yuboring (rasm fayl sifatida):"
        )
        return WAITING_IMAGE
    
    elif query.data == 'new_store':
        # Boshqa do'konga mahsulot qo'shish
        user_data_dict = get_user_data(user_id)
        # Barcha ma'lumotlarni tozalash
        user_data_dict['agent'] = None
        user_data_dict['email'] = None
        user_data_dict['password'] = None
        user_data_dict['image_path'] = None
        user_data_dict['description'] = None
        user_data_dict['price'] = None
        user_data_dict['stock'] = 1
        user_data_dict['discount'] = 0.0
        
        await query.edit_message_text(
            "✅ Boshqa do'konga mahsulot qo'shish!\n\n"
            "Do'kon email manzilini yuboring:"
        )
        return WAITING_EMAIL
    
    elif query.data == 'skip_discount':
        # Chegirmani skip qilish
        user_data_dict = get_user_data(user_id)
        user_data_dict['discount'] = 0.0
        
        # Mahsulotni yuklash
        await query.edit_message_text("⏳ Mahsulot yuklanmoqda...")
        
        try:
            agent = user_data_dict['agent']
            result = agent.upload_product(
                description=user_data_dict['description'],
                image_path=user_data_dict['image_path'],
                price=user_data_dict['price'],
                stock=user_data_dict['stock'],
                discount=user_data_dict['discount']
            )
            
            # Temp rasmni o'chirish
            try:
                if os.path.exists(user_data_dict['image_path']):
                    os.remove(user_data_dict['image_path'])
            except:
                pass
            
            if result.get('success'):
                # Muvaffaqiyatli yuklangan buttonlar
                keyboard = [
                    [
                        InlineKeyboardButton("➕ Yana yangi mahsulot qo'shish", callback_data='new_product'),
                        InlineKeyboardButton("🔄 Boshqa do'konga mahsulot qo'shish", callback_data='new_store')
                    ],
                    [
                        InlineKeyboardButton("✅ Tugatish", callback_data='finish')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    "✅ Mahsulot muvaffaqiyatli yuklandi!\n\n"
                    f"📝 Xabar: {result.get('message', 'Muvaffaqiyatli')}",
                    reply_markup=reply_markup
                )
                return ConversationHandler.END
            else:
                error_msg = result.get('error', 'Nomalum xato')
                await query.edit_message_text(
                    f"❌ Mahsulot yuklashda xato:\n{error_msg}\n\n"
                    "Qaytadan boshlash uchun /start buyrug'ini yuboring."
                )
                return ConversationHandler.END
        except Exception as e:
            logger.error(f"Mahsulot yuklash xatosi: {str(e)}")
            await query.edit_message_text(
                f"❌ Xato yuz berdi: {str(e)}\n\n"
                "Qaytadan boshlash uchun /start buyrug'ini yuboring."
            )
            return ConversationHandler.END
    
    elif query.data == 'finish':
        # Tugatish
        await query.edit_message_text("✅ Rahmat! Botdan foydalanganingiz uchun tashakkur!")
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Jarayonni bekor qilish"""
    await update.message.reply_text(
        "❌ Jarayon bekor qilindi.\n"
        "Qaytadan boshlash uchun /start buyrug'ini yuboring."
    )
    return ConversationHandler.END


def main():
    """Botni ishga tushirish"""
    # Bot tokenini environment variable'dan olish
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN environment variable topilmadi!")
        print("Iltimos, bot tokenini o'rnating:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
        return
    
    # Application yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email),
                CallbackQueryHandler(button_callback)
            ],
            WAITING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
            WAITING_IMAGE: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_image),
                CallbackQueryHandler(button_callback)
            ],
            WAITING_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description)],
            WAITING_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_price)],
            WAITING_DISCOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_discount),
                CallbackQueryHandler(button_callback)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(button_callback)
        ],
        allow_reentry=True
    )
    
    # Handlerlarni qo'shish
    application.add_handler(conv_handler)
    # ConversationHandler.END holatida ham button callback handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Botni ishga tushirish
    print("🤖 Bot ishga tushmoqda...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
