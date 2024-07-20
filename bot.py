import pandas as pd
import requests
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
from flask import Flask

# رابط الجوجل شيتس
SHEET_ID = '1--Lcu0S2dSgH81qHNKPpiF9vGeSnqZiZ'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)

def start(update: Update, context: CallbackContext) -> None:
    start_message = (
        "👋 أهلاً! أرسل رقم الهوية للبحث. \n\n"
        "📋 مثال: 123456789\n"
        "🔍 سيقوم البوت بالبحث في البيانات وإرجاع النتائج."
    )
    update.message.reply_text(start_message)

def search(update: Update, context: CallbackContext) -> None:
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
    TOKEN = os.getenv("7124688280:AAGB4MzzUNc9aYEeeLhnDO7Q5Coa6IQZuwg")
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, search))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=8080)
