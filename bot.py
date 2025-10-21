import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)
import gspread
from datetime import datetime
import json

# Настройки для Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # Берем из переменных окружения

# Обрабатываем Google credentials из переменной окружения
credentials_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
if credentials_json:
    GOOGLE_SHEETS_CREDENTIALS = json.loads(credentials_json)
else:
    GOOGLE_SHEETS_CREDENTIALS = None

SPREADSHEET_NAME = 'Хэллоуинский Обед 2025'

# Этапы разговора
NAME, FOOD_FORMAT, DISH, DRINKS, COSTUME, WISHES = range(6)

# Подключаемся к Google Таблице
try:
    if GOOGLE_SHEETS_CREDENTIALS:
        gc = gspread.service_account_from_dict(GOOGLE_SHEETS_CREDENTIALS)
        sh = gc.open(SPREADSHEET_NAME)
        worksheet = sh.sheet1
        # Создаем заголовки, если таблица пустая
        if not worksheet.get_all_values():
            worksheet.append_row([
                'ID', 'Имя', 'Формат еды', 'Блюдо/Напиток', 'Напитки', 
                'Костюм', 'Пожелания', 'Время записи', 'Актуальная запись'
            ])
    else:
        print("Google credentials not found!")
except Exception as e:
    print(f"Ошибка подключения к Google Таблицам: {e}")

def get_user_id(update: Update):
    """Генерирует ID пользователя"""
    return f"user_{update.message.from_user.id}"

def find_existing_record(user_id):
    """Ищет существующую запись пользователя"""
    try:
        records = worksheet.get_all_records()
        for i, record in enumerate(records, start=2):  # start=2 потому что первая строка - заголовки
            if record.get('ID') == user_id and record.get('Актуальная запись') == 'Да':
                return i  # возвращаем номер строки
        return None
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает опрос и проверяет существующие записи"""
    user = update.message.from_user
    user_id = get_user_id(update)
    
    # Проверяем, есть ли уже запись у пользователя
    existing_row = find_existing_record(user_id)
    
    if existing_row:
        # Получаем существующие данные
        existing_data = worksheet.row_values(existing_row)
        welcome_text = (
            f"🎃 *С возвращением, {user.first_name}!* 🧛‍♂️\n\n"
            f"У тебя уже есть запись на обед:\n"
            f"• *Формат еды:* {existing_data[2]}\n"
            f"• *Блюдо:* {existing_data[3]}\n"
            f"• *Напитки:* {existing_data[4]}\n"
            f"• *Костюм:* {existing_data[5]}\n\n"
            f"Хочешь *обновить* свои данные или *оставить всё как есть*?\n\n"
            f"Просто пройди опрос заново - я обновлю твою запись! 📝"
        )
    else:
        welcome_text = (
            "🎃 *Добро пожаловать на Хэллоуинский обед!* 🧛‍♂️\n\n"
            "Я помогу тебе записаться на наш жутко веселый праздник. "
            "Ответь на несколько вопросов, и твои данные попадут в нашу Книгу Ужасов!\n\n"
            "Для начала, как мне тебя записать?"
        )
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    
    return NAME

# [ВСТАВЬТЕ ЗДЕСЬ ВСЕ ОСТАЛЬНЫЕ ФУНКЦИИ ИЗ ПРЕДЫДУЩЕГО КОДА]
# get_name, get_food_format, get_drinks, get_dish, get_costume, get_wishes, cancel, status, main
