import sqlite3
from emoji import emojize
import re
from main import bot

from config import DB_PATH_GRLS, DB_PATH_ARMENIA, DB_PATH_KYRGYSTAN, DB_PATH_KAZAKHSTAN

async def get_info_from_db_substance(message, country, chat_id):
    if country == emojize(':Russia: Россия'):
        def sqlite_lower(_str):
            return _str.lower()
        # Разбиваем строку на отдельные слова и приводим каждое слово к строчной букве.
        drug_words = message.split()
        lower_drug_words = [word.lower() for word in drug_words]
        # Объединяем слова в строку
        lower_drug_substance = ' '.join(lower_drug_words)
        # Проверяем, что значение содержит только буквы кириллицы
        if not re.match('^[А-Яа-я\\s]+$', lower_drug_substance):
            await bot.send_message(chat_id, 'Вы некорректно ввели название. Нужно использовать только буквы кириллицы')
            return
        conn = sqlite3.connect(DB_PATH_GRLS)
        conn.create_function("mylower", 1, sqlite_lower)
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM grls_drugs_upd WHERE mylower(As_name_rus) LIKE ?', ('%' + lower_drug_substance + '%',)).fetchall()
        conn.close()
        return result


    elif country == emojize(':Armenia: Армения'):
        conn = sqlite3.connect(DB_PATH_ARMENIA)
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM mnn_pdf WHERE As_name_rus = ?', (message,)).fetchall()
        return result
    elif country == emojize(':Kyrgyzstan: Кыргызстан'):
        conn = sqlite3.connect(DB_PATH_KYRGYSTAN)
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM mnn_excel WHERE As_name_rus = ?', (message,)).fetchall()
        return result
    elif country == emojize(':Kazakhstan: Казахстан'):
        conn = sqlite3.connect(DB_PATH_KAZAKHSTAN)
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM ndda_drugs WHERE As_name_rus = ?', (message,)).fetchall()
        return result

async def get_info_from_db_name(message, country, chat_id):
    if country == emojize(':Russia: Россия'):
        def sqlite_lower(_str):
            return _str.lower()
        drug_name_words = message.split()
        lower_drug_name_words = [word.lower() for word in drug_name_words]
        lower_drug_name = ' '.join(lower_drug_name_words)
        if not re.match('^[А-Яа-я\\s]+$', lower_drug_name):
            await message.answer('Вы некорректно ввели название. Нужно использовать только буквы кириллицы')
            return
        conn_2 = sqlite3.connect(DB_PATH_GRLS)
        conn_2.create_function('mylower', 1, sqlite_lower)
        cursor_2 = conn_2.cursor()
        result_2 = cursor_2.execute('SELECT * FROM grls_drugs_upd WHERE mylower(Trade_name_rus) LIKE ?', ('%' + lower_drug_name + '%',)).fetchall()
        conn_2.close()
        return result_2






    elif country == emojize(':Armenia: Армения'):
        conn = sqlite3.connect(DB_PATH_ARMENIA)
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM mnn_pdf WHERE As_name_rus = ?', (message,)).fetchall()
        return result
    elif country == emojize(':Kyrgyzstan: Кыргызстан'):
        conn = sqlite3.connect(DB_PATH_KYRGYSTAN)
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM mnn_excel WHERE As_name_rus = ?', (message,)).fetchall()
        return result  
