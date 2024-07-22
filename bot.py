python
import pandas as pd
import requests
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
from flask import Flask

# إعدادات Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# رابط الجوجل شيتس
SHEET_ID = '1--Lcu0S2dSgH81qHNKPpiF9vGeSnqZiZ'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'

def download_file(url):
    """تحميل ملف Excel من جوجل شيتس"""
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)

def start(update: Update, context: CallbackContext) -> None:
    """إرسال رسالة ترحيبية عند بدء التفاعل مع البوت"""
    start_message = (
        "👋 أهلاً! أرسل رقم الهوية للبحث. \n\n"
        "📋 مثال: 123456789\n"
        "🔍 سيقوم البوت بالبحث في البيانات وإرجاع النتائج."
    )
    update.message.reply_text(start_message)

def search(update: Update, context: CallbackContext) -> None:
    """البحث في ملف جوجل شيتس عن رقم الهوية المرسل من المستخدم"""
    update.message.reply_text('🔄 بدء عملية البحث، يرجى الأنتظار...')
    
    query = update.message.text
    try:
        file_content = download_file(SHEET_URL)
        df = pd.read_excel(file_content)
        results = df[df['رقم الهوية'].astype(str) == query]

        if not results.empty:
            for index, row in results.iterrows():
                result_text = '\n'.join([f"📌 {col}: {row[col]}" for col in df.columns])
                update.message.reply_text(result_text)
        else:
            update.message.reply_text('❌ لم يتم العثور على نتائج.')
    except Exception as e:
        update.message.reply_text('⚠️ حدث خطأ أثناء محاولة الوصول إلى البيانات.')

def main() -> None:
    """إعداد البوت وتشغيله"""
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise ValueError("No TELEGRAM_TOKEN found in environment variables")
    
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, search))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=8080)
