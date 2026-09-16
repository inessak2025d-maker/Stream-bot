import asyncio
import sqlite3
import re
import os
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [1060224856, 6249616641, 464072191, 491893726]  # Твої ID
NOTIFY_ADMIN_IDS = [1060224856,6249616641,464072191]  # ID тих адмінів, яким писати в ЛС про запуск/вимкнення

# === СЛОВНИК СИНОНІМІВ (АЛІАСІВ) ===
ALIASES = {
    "папка для квитка": ["папка", "папку"],
    "картка з всіма персонажами": ["картка", "картку"],
    "стікери": ["стікер", "наліпки", "наліпка"],
    "блукач": ["скара", "скарамучча"],
    "пожирач місяця": ["пожирач"],
    "дан хенг": ["дань хен", "даня", "данхенг", "данхен" ],
    "тарталья": ["чайлд", "аякс"],
    "чжун лі": ["дід", "чжун", "моракc"],
    "Сьоме березня": ["7 березня"],
    "неділя": ["сандей"],
    "першовідкривач": ["гг"],
    "світлячок": ["світляк", "фаєрфлай"],
    "робін": ["зарянка"],
    "іскорка": ["спаркл", "спарксі", "іскринка", "жаринка", "ханабі"],
    "файнон": ["Каслана", "Каослана", "Викрадач Полум'я", "Викрадач Полум'я Рівер", "рівер", "Сталесклеп", "фаєнон"],
    "галлахер": ["галахер"],
    "чорний лебідь": ["лебідь", "лебедиця", "чорна лебедиця"],
    "цзин юань": ["цзинь юань", "генерал", "юань"],
    "бутхіл": ["бутхілл"],
    "Цзяоцю": ["цзяоцзю"],
    "невілетт": ["невілет"],
    "раміель": ["реміель"],
    "жуань мей": ["жуань", "мей", "жуаньмей", "руан мей", "руанмей"],
    "Аль Хайтам": ["Альхайтам", "хайтам"],
    "раціо": ["ратіо"],
    "анакса": ["анаксагор"],
    "Яо Гуан": ["Яо Гуанг", "Яо Гуанґ", "Гуан", "Гуанґ", "Гуанг", "яогуан", "яогуанг", "яогуанґ"],
    "раппа": ["рапа"],
    "Кирена": ["Кірена", "Сайріні"],
    "кея": ["кая", "кайя", "кейя", "кєйя"],
    "велика герта": ["герта", "верта"],
    "ци ци": ["цици", "чічі", "чі чі"],
    "бай чжу": ["байчжу", "байджу", "бай джу"],
    "ділюк": ["дилюк"],
    "коломбіна": ["колумбіна"],
    "Нангон Юй": ["Нангон"],
    "Ху Тао": ["хутао"],
    "Яе Міко": ["Яє Міко"],
    "є шуньгуань": ["шуньгуань"],
    "кадзуха": ["казуха"],
    "дотторе": ["доторе", "Зандик"],
    "чан лі": ["чанлі"],
    "фуріна": ["Фокалорс"],
    "ян ян ": ["янян"],
    "авантюрин ": ["аван", "тюрин"],
    "Триґґер": ["Триггер", "Тригер", "Триґер"],
    "фу сюань": ["фусюань"],
    "тріббі": ["трібі"],
    "Вічноніччя": ["евернайт"],
    "Срібляста Вовчиця": ["Сріблястий вовк", "вовчиця", "срібна", "срібна вовчиця"],
    "гань юй": ["ганьюй", "ганька"],
    "хуго": ["хюго", "хьюго", "влад", "гюго"],
    "ровер": [],
    "айміс": ["емет", "еміс"],
    "джінсі": ["джинши", "джинсі", "дзіньсі"],
    "цьов'юань": ["цююань", "цьовюань"],
    "чанлі": ["чанглі"],
    "Їдхарі": ["ідхарі", "Їдгарі"],
    "їнлінь": ["їнлін"],
    "сяньлі яо": ["сянлі яо", "яо"],
    "шоркіпер": ["хранителька", "Хранителька Берегів"],
    "камелія": [],
    "джіян": ["джиян"],
    "джеші": ["жежи", "жежі"],
    "карлотта": ["карлота"],
    "кальчаро": ["калькулятор"],
    "санхва": ["санхуа"],
    "байджі": ["байжи", "байчжи"],
    "данджін": ["данжин"],
    "янян": ["сюаньлін"],
    "чіся": ["чися"],
    "юдзуха": ["юзуха"],
    "лучілла": ["люцилла", "люцілла", "люсілла", "люцила"],
    "свейсвей": [],
    "цінсяо": [],
    "дзінжань": ["цзінжань"],
    "сінь": ["хсін", "сін"],
    "свомін": [],
    "хіюкі": [],
    "денія": ["данія"],
    "морньє": ["морні"],
    "брант": [],
    "люпа": ["лупа"],
    "августа": ["аугуста"],
    "чакона": [],
    "картесія": ["картетія", "карт"],
    "юно": ["луно", "іуно"],
    "сігріка": ["сіґріка", "сіггі"],
    "фібі": [],
    "зані": [],
    "лінае": ["ліне", "ліней", "лінея"],
    "лююк": ["люк"],
    "роча": ["роччіа"],
    "кантарелла": ["кантарела"],
    "фролова": []
}

# === СЛОВНИК ЧИСЛОВИХ БРОНЕЙ ===
NUMBER_ALIASES = {
    1: ["1", "перша", "перший", "перше", "першу", "один"],
    2: ["2", "друга", "другий", "друге", "другу", "два"],
    3: ["3", "третя", "третій", "третє", "третю", "три"],
    4: ["4", "четверта", "четвертий", "четверte", "четверту", "чотири"],
    5: ["5", "п'ята", "пята", "п'ятий", "пятий", "п'яте", "пять", "п'ять", "п'яту", "пяту"],
    6: ["6", "шоста", "шостий", "шосте", "шосту", "шість"],
    7: ["7", "сьома", "сьомий", "сьоме", "сьому", "сім"],
    8: ["8", "восьма", "восьмий", "восьме", "восьму", "вісім"],
    9: ["9", "дев'ята", "девята", "дев'ятий", "девятий", "дев'яте", "девять", "дев'ять", "дев'яту", "девяту"],
    10: ["10", "десята", "десятий", "десяте", "десяту", "десять"],
    11: ["11", "одинадцята", "одинадцятий", "одинадцяте", "одинадцяту", "одинадцять"],
    12: ["12", "дванадцята", "дванадцятий", "дванадцяте", "дванадцяту", "дванадцять"],
    13: ["13", "тринадцята", "тринадцятий", "тринадцяте", "тринадцяту", "тринадцять"],
    14: ["14", "чотирнадцята", "чотирнадцятий", "чотирнадцяте", "чотирнадцяту", "чотирнадцять"],
    15: ["15", "п'ятнадцята", "пятнадцята", "п'ятнадцятий", "пятнадцятий", "п'ятнадцяте", "пятнадцяте", "п'ятнадцяту", "пятнадцяту", "п'ятнадцять", "пятнадцять"],
    16: ["16", "шістнадцята", "шістнадцятий", "шістнадцяте", "шістнадцяту", "шістнадцять"],
    17: ["17", "сімнадцята", "сімнадцятий", "сімнадцяте", "сімнадцяту", "сімнадцять"],
    18: ["18", "вісімнадцята", "вісімнадцятий", "вісімнадцяте", "вісімнадцяту", "вісімнадцять"],
    19: ["19", "дев'ятнадцята", "девятнадцята", "дев'ятнадцятий", "девятнадцятий", "дев'ятнадцяте", "девятнадцяте", "дев'ятнадцяту", "девятнадцяту", "дев'ятнадцять", "девятнадцять"],
    20: ["20", "двадцята", "двадцятий", "двадцяте", "двадцяту", "двадцять"],
    21: ["21", "двадцять перша", "двадцять перший", "двадцять перше", "двадцять першу", "двадцять один"],
    22: ["22", "двадцять друга", "двадцять другий", "двадцять друге", "двадцять другу", "двадцять два"],
    23: ["23", "двадцять третя", "двадцять третій", "двадцять третє", "двадцять третю", "двадцять три"],
    24: ["24", "двадцять четверта", "двадцять четвертий", "двадцять четверте", "двадцять четверту", "двадцять чотири"],
    25: ["25", "двадцять п'ята", "двадцять пята", "двадцять п'ятий", "двадцять пятий", "двадцять п'яте", "двадцять пяте", "двадцять п'яту", "двадцять пяту", "двадцять п'ять", "двадцять пять"],
    26: ["26", "двадцять шоста", "двадцять шостий", "двадцять шосте", "двадцять шосту", "двадцять шість"],
    27: ["27", "двадцять сьома", "двадцять сьомий", "двадцять сьоме", "двадцять сьому", "двадцять сім"],
    28: ["28", "двадцять восьма", "двадцять восьмий", "двадцять восьме", "двадцять восьму", "двадцять вісім"],
    29: ["29", "двадцять дев'ята", "двадцять девята", "двадцять дев'ятий", "двадцять девятий", "двадцять дев'яте", "двадцять девяте", "двадцять дев'яту", "двадцять девяту", "двадцять дев'ять", "двадцять девять"],
    30: ["30", "тридцята", "тридцятий", "тридцяте", "тридцяту", "тридцять"],
    31: ["31", "тридцять перша", "тридцять перший", "тридцять перше", "тридцять першу", "тридцять один"],
    32: ["32", "тридцять друга", "тридцять другий", "тридцять друге", "тридцять другу", "тридцять два"],
    33: ["33", "тридцять третя", "тридцять третій", "тридцять третє", "тридцять третю", "тридцять три"],
    34: ["34", "тридцять четверта", "тридцять четвертий", "тридцять четверте", "тридцять четверту", "тридцять чотири"],
    35: ["35", "тридцять п'ята", "тридцять пята", "тридцять п'ятий", "тридцять пятий", "тридцять п'яте", "тридцять пяте", "тридцять п'яту", "тридцять пяту", "тридцять п'ять", "тридцять пять"],
    36: ["36", "тридцять шоста", "тридцять шостий", "тридцять шосте", "тридцять шосту", "тридцять шість"]
}

db_path = os.getenv("DB_PATH", "merch.db") 
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ДОДАНО ПОЛЕ is_auction у таблицю merch
cursor.execute('''CREATE TABLE IF NOT EXISTS merch (id INTEGER PRIMARY KEY AUTOINCREMENT, photo_id TEXT, game TEXT, merch_type TEXT, character TEXT, price INTEGER, is_auction BOOLEAN DEFAULT 0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS stream_state (chat_id INTEGER PRIMARY KEY, active_merch_id INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS chat_log (message_id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, text TEXT, merch_id INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, merch_id INTEGER, chat_id INTEGER, message_id INTEGER, booked_character TEXT, booked_price INTEGER)''')

# Перевірка та оновлення існуючої таблиці (якщо база стара і колонки is_auction ще немає)
try:
    cursor.execute("SELECT is_auction FROM merch LIMIT 1")
except sqlite3.OperationalError:
    cursor.execute("ALTER TABLE merch ADD COLUMN is_auction BOOLEAN DEFAULT 0")

conn.commit()

bot = Bot(token=TOKEN)
dp = Dispatcher()

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Сформувати чеки броней", callback_data="get_invoices")]
])

# ДОДАНО: Клавіатура для звичайних покупців
user_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🧾 Мій чек", callback_data="my_invoice")]
])

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Привіт, адміне! Бот готовий до стріму.", reply_markup=admin_keyboard)
    else:
        # ДОДАНО: Привітання для звичайних користувачів
        await message.answer(
            f"Привіт, {message.from_user.first_name}! 👋\n\n"
            "Тут ти можеш перевірити свої поточні броні зі стріму.\n"
            "Натисни кнопку нижче, щоб побачити свій чек:",
            reply_markup=user_keyboard
        )

@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_messages(message: types.Message):
    text = message.text or message.caption or ""
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    # ПЕРЕВІРКА НА АУКЦІОН (найвищий пріоритет)
    if message.from_user.id in ADMIN_IDS and "Стартова ціна" in text:
        print("[ЛОГ] Знайдено шаблон АУКЦІОНУ! Розшифровую...")

        # Шукаємо назву аукціону (текст перед "Стартова ціна")
        lines = text.split('\n')
        auction_name = "Аукціон"
        for i, line in enumerate(lines):
            if "Стартова ціна" in line and i > 0:
                # Намагаємося взяти попередній непорожній рядок як назву
                for prev_line in reversed(lines[:i]):
                    if prev_line.strip() and not prev_line.startswith('['):
                        auction_name = f"Аукціон: {prev_line.strip()}"
                        break
                break

        # Витягуємо стартову ціну просто для запису в базу (реальна ціна буде з коментаря)
        price_match = re.search(r'Стартова ціна\s*[-:]?\s*(\d+)', text, re.IGNORECASE)
        start_price = int(price_match.group(1).strip()) if price_match else 0

        photo_id = message.photo[-1].file_id if message.photo else None

        cursor.execute('''INSERT INTO merch (photo_id, game, merch_type, character, price, is_auction) VALUES (?, ?, ?, ?, ?, ?)''',
                       (photo_id, "Аукціон", auction_name, "Переможець аукціону", start_price, True))
        merch_id = cursor.lastrowid

        cursor.execute('''INSERT OR REPLACE INTO stream_state (chat_id, active_merch_id) VALUES (?, ?)''', (message.chat.id, merch_id))

        cursor.execute('''INSERT OR REPLACE INTO chat_log (message_id, user_id, username, text, merch_id) VALUES (?, ?, ?, ?, ?)''',
                       (message.message_id, message.from_user.id, username, text, merch_id))
        conn.commit()

        print(f"[ЛОГ] Аукціон №{merch_id} ({auction_name}) успішно додано та активовано!")
        return

    # ПЕРЕВІРКА НА ЗВИЧАЙНИЙ ЛОТ
    elif message.from_user.id in ADMIN_IDS and ("Тип:" in text or "Персонаж" in text):
        print("[ЛОГ] Знайдено шаблон лоту! Розшифровую...")

        game_match = re.search(r'Гра:\s*(.*?)(?=\s*Тип:|\s*Персонаж[і]?:|\s*Ціна:|$)', text, re.IGNORECASE | re.DOTALL)
        type_match = re.search(r'Тип:\s*(.*?)(?=\s*Персонаж[і]?:|\s*Ціна:|$)', text, re.IGNORECASE | re.DOTALL)
        char_match = re.search(r'Персонаж[і]?:\s*(.*?)(?=\s*Ціна:|$)', text, re.IGNORECASE | re.DOTALL)
        price_match = re.search(r'Ціна:\s*(\d+)', text, re.IGNORECASE)

        game = game_match.group(1).strip() if game_match else "Невідомо"
        merch_type = type_match.group(1).strip() if type_match else "Невідомо"
        character = char_match.group(1).strip() if char_match else "Невідомо"
        price = int(price_match.group(1).strip()) if price_match else 0

        photo_id = message.photo[-1].file_id if message.photo else None

        cursor.execute('''INSERT INTO merch (photo_id, game, merch_type, character, price, is_auction) VALUES (?, ?, ?, ?, ?, ?)''',
                       (photo_id, game, merch_type, character, price, False))
        merch_id = cursor.lastrowid

        cursor.execute('''INSERT OR REPLACE INTO stream_state (chat_id, active_merch_id) VALUES (?, ?)''', (message.chat.id, merch_id))

        cursor.execute('''INSERT OR REPLACE INTO chat_log (message_id, user_id, username, text, merch_id) VALUES (?, ?, ?, ?, ?)''',
                       (message.message_id, message.from_user.id, username, text, merch_id))
        conn.commit()

        print(f"[ЛОГ] Лот №{merch_id} ({character}) успішно додано та активовано!")
        return

    target_merch_id = None

    if message.reply_to_message:
        cursor.execute("SELECT merch_id FROM chat_log WHERE message_id = ?", (message.reply_to_message.message_id,))
        replied_log = cursor.fetchone()
        if replied_log and replied_log[0]:
            target_merch_id = replied_log[0]

    if not target_merch_id:
        cursor.execute("SELECT active_merch_id FROM stream_state WHERE chat_id = ?", (message.chat.id,))
        state = cursor.fetchone()
        target_merch_id = state[0] if state else None

    cursor.execute('''INSERT OR REPLACE INTO chat_log (message_id, user_id, username, text, merch_id) VALUES (?, ?, ?, ?, ?)''',
                   (message.message_id, message.from_user.id, username, text, target_merch_id))
    conn.commit()

@dp.edited_message(F.chat.type.in_({"group", "supergroup"}))
async def handle_edited_group_messages(message: types.Message):
    # Якщо людина відредагувала коментар, оновлюємо його в базі даних бота
    text = message.text or message.caption or ""
    cursor.execute("UPDATE chat_log SET text = ? WHERE message_id = ?", (text, message.message_id))
    conn.commit()

@dp.message_reaction()
async def catch_reactions(reaction: types.MessageReactionUpdated):
    if reaction.user.id not in ADMIN_IDS:
        return

    new_emojis = [r.emoji for r in reaction.new_reaction if r.type == "emoji"]
    old_emojis = [r.emoji for r in reaction.old_reaction if r.type == "emoji"]

    has_heart_now = any(emoji in ["❤️", "❤"] for emoji in new_emojis)
    had_heart_before = any(emoji in ["❤️", "❤"] for emoji in old_emojis)

    if has_heart_now and not had_heart_before:
        cursor.execute("SELECT user_id, username, merch_id, text FROM chat_log WHERE message_id = ?", (reaction.message_id,))
        buyer = cursor.fetchone()

        if buyer and buyer[2]:
            buyer_user_id, buyer_username, merch_id, comment_text = buyer

            cursor.execute("SELECT character, price, is_auction, merch_type FROM merch WHERE id = ?", (merch_id,))
            merch_row = cursor.fetchone()
            if not merch_row: return

            original_characters = merch_row[0]
            base_price = merch_row[1]
            is_auction = merch_row[2]
            merch_type = merch_row[3]

            # --- ЛОГІКА ДЛЯ АУКЦІОНУ ---
            if is_auction:
                # Шукаємо число в коментарі (ставку)
                bid_match = re.search(r'(\d+)', comment_text)
                if bid_match:
                    final_price = int(bid_match.group(1))

                    # Для аукціону завжди тільки один переможець на лот. Перевіряємо, чи вже хтось не "виграв" його
                    cursor.execute("SELECT id FROM bookings WHERE merch_id = ?", (merch_id,))
                    if cursor.fetchone():
                        print(f"[ЛОГ] УВАГА: Аукціон №{merch_id} вже завершено. Повторна ставка від {buyer_username} ігнорується.")
                        return

                    cursor.execute("INSERT INTO bookings (user_id, username, merch_id, chat_id, message_id, booked_character, booked_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (buyer_user_id, buyer_username, merch_id, reaction.chat.id, reaction.message_id, "Переможець аукціону", final_price))
                    conn.commit()
                    print(f"[ЛОГ] ФІКСАЦІЯ АУКЦІОНУ: {buyer_username} виграв '{merch_type}' зі ставкою {final_price} грн")
                else:
                    print(f"[ЛОГ] УВАГА: Не вдалося знайти ставку в коментарі '{comment_text}' від {buyer_username}.")
                return # Завершуємо обробку реакції, якщо це аукціон

            # --- ЛОГІКА ДЛЯ ЗВИЧАЙНОГО ЛОТУ ---
            comment_lower = comment_text.lower()
            padded_comment = f" {comment_lower.replace(',', ' ').replace('.', ' ')} "

            # 1. Глобальний множник (якщо написали "х2", "x3")
            mult_match = re.search(r'(?:х|x)\s*(\d+)', comment_lower)
            global_mult = int(mult_match.group(1)) if mult_match else 1

            char_list = [c.strip() for c in re.split(r',|\n', original_characters) if c.strip()]
            parsed_items = []

            for c in char_list:
                item_price = base_price
                item_qty = 1
                name_part = c.strip()

                name_part = re.sub(r'^\d+[\.\)]\s*', '', name_part).strip()

                ind_price_match = re.search(r'[-–—\s]+(\d+)\s*(?:грн|uah|грн\.|uah\.)?$', name_part, re.IGNORECASE)
                if ind_price_match:
                    item_price = int(ind_price_match.group(1))
                    name_part = name_part[:ind_price_match.start()].strip()

                qty_match = re.search(r'(?:\s+)?[xх](\d+)(?:\s+)?$', name_part, re.IGNORECASE)
                if qty_match:
                    item_qty = int(qty_match.group(1))
                    name_part = name_part[:qty_match.start()].strip()
                    
                # --- ДОДАНО: Відрізаємо коментарі в дужках [] або () ---
                name_part = re.sub(r'\[.*?\]|\(.*?\)', '', name_part).strip()
                    
                parsed_items.append({"name": name_part, "price": item_price, "qty": item_qty})

            requested_items = []
            for idx, item in enumerate(parsed_items, start=1):
                matched_qty = 0
                name_lower = item["name"].lower()
                num_aliases = NUMBER_ALIASES.get(idx, [str(idx)])

                # Шукаємо стільки разів, скільки фізично є цього товару в лоті
                for _ in range(item["qty"]):
                    match_found = False

                    # Перевірка по цифрах
                    for num_alias in num_aliases:
                        target = f" {num_alias} "
                        if target in padded_comment:
                            match_found = True
                            padded_comment = padded_comment.replace(target, " ", 1)
                            # ДОДАНО: Стираємо знайдену цифру і з текстового коментаря,
                            # щоб бот не знаходив її вдруге вже як буквальне ім'я персонажа
                            comment_lower = re.sub(rf'\b{num_alias}\b', ' ', comment_lower, count=1)
                            break

                    # Перевірка по іменах
                    if not match_found:
                        if name_lower in comment_lower:
                            match_found = True
                            comment_lower = comment_lower.replace(name_lower, " ", 1)
                        else:
                            for canonical, aliases in ALIASES.items():
                                if name_lower == canonical or name_lower in aliases:
                                    if canonical in comment_lower:
                                        match_found = True
                                        comment_lower = comment_lower.replace(canonical, " ", 1)
                                        break

                                    matched_alias = next((a for a in aliases if a in comment_lower), None)
                                    if matched_alias:
                                        match_found = True
                                        comment_lower = comment_lower.replace(matched_alias, " ", 1)
                                        break

                    # План В: перевірка по типу (тільки якщо лот одиночний)
                    if not match_found and merch_type.lower() != "невідомо" and len(parsed_items) == 1:
                        type_words = [w for w in re.findall(r'[а-яіїєґa-z]+', merch_type.lower()) if len(w) >= 4]
                        for t_word in type_words:
                            if t_word in comment_lower:
                                match_found = True
                                comment_lower = comment_lower.replace(t_word, " ", 1)
                                break

                    if match_found:
                        matched_qty += 1

                # Якщо знайшли хоча б 1 раз і є "х2", збільшуємо кількість
                if matched_qty > 0 and global_mult > 1:
                    matched_qty = max(matched_qty, global_mult)
                    matched_qty = min(matched_qty, item["qty"]) # Але не більше, ніж є в лоті

                # Додаємо в список бажаних покупок
                for _ in range(matched_qty):
                    new_item = item.copy()
                    new_item["display_name"] = f"{idx}. {item['name']}"
                    requested_items.append(new_item)

            # Якщо нічого не знайшли, але лот один (можливо просто "+")
            if not requested_items and len(parsed_items) == 1:
                matched_qty = min(global_mult, parsed_items[0]["qty"])
                for _ in range(matched_qty):
                    new_item = parsed_items[0].copy()
                    new_item["display_name"] = f"1. {parsed_items[0]['name']}"
                    requested_items.append(new_item)

            cursor.execute("SELECT booked_character FROM bookings WHERE merch_id = ?", (merch_id,))
            already_booked = [row[0] for row in cursor.fetchall()]

            successfully_booked = []
            for item in requested_items:
                current_bookings_count = already_booked.count(item["display_name"]) + already_booked.count(item["name"])

                if current_bookings_count < item["qty"]:
                    cursor.execute("INSERT INTO bookings (user_id, username, merch_id, chat_id, message_id, booked_character, booked_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (buyer_user_id, buyer_username, merch_id, reaction.chat.id, reaction.message_id, item["display_name"], item["price"]))

                    already_booked.append(item["display_name"])
                    successfully_booked.append(f"{item['display_name']} ({item['price']} грн)")

            conn.commit()

            # --- ПЕРЕВІРКА НА НЕРОЗПІЗНАНІ АБО ПРОПУЩЕНІ СЛОВА ---
            leftover_request = False
            for n in range(1, 37):
                for num_alias in NUMBER_ALIASES.get(n, [str(n)]):
                    if f" {num_alias} " in padded_comment:
                        leftover_request = True
                        break
                if leftover_request: break

            if not leftover_request:
                for canonical, aliases in ALIASES.items():
                    if canonical in comment_lower or any(a in comment_lower for a in aliases):
                        leftover_request = True
                        break

            # Чи не отримала людина все, що хотіла? (часткове бронювання)
            partial_booking = len(successfully_booked) < len(requested_items) or leftover_request

            if successfully_booked:
                print(f"[ЛОГ] ФІКСАЦІЯ: {buyer_username} отримав: {', '.join(successfully_booked)}")
                if partial_booking:
                    booked_str = ", ".join(successfully_booked)
                    try:
                        await bot.send_message(reaction.chat.id, f"{buyer_username}, зарахована бронь лише: {booked_str}", reply_to_message_id=reaction.message_id)
                    except Exception as e:
                        print(f"[Помилка відправки повідомлення] {e}")
            else:
                print(f"[ЛОГ] УВАГА: {buyer_username} нічого не отримав.")
                try:
                    await bot.send_message(reaction.chat.id, f"{buyer_username}, не зарахована бронь. Якщо це помилка - відредагуйте своє повідомлення по зразку поста з мерчом", reply_to_message_id=reaction.message_id)
                except Exception as e:
                    print(f"[Помилка відправки повідомлення] {e}")

    elif had_heart_before and not has_heart_now:
        cursor.execute("DELETE FROM bookings WHERE chat_id = ? AND message_id = ?", (reaction.chat.id, reaction.message_id))
        conn.commit()
        print(f"[ЛОГ] СКАСУВАННЯ: Броні із повідомлення {reaction.message_id} видалено.")

@dp.callback_query(F.data == "get_invoices")
async def generate_invoices(callback: types.CallbackQuery):
    cursor.execute('''SELECT b.username, m.merch_type, b.booked_character, b.booked_price, b.chat_id, b.message_id, m.is_auction 
                      FROM bookings b JOIN merch m ON b.merch_id = m.id''')
    all_bookings = cursor.fetchall()
    
    if not all_bookings:
        await callback.message.answer("Поки що немає зафіксованих броней.")
        await callback.answer()
        return
        
    user_buckets = {}
    for username, merch_type, booked_char, booked_price, chat_id, msg_id, is_auction in all_bookings:
        if username not in user_buckets:
            user_buckets[username] = {"items": [], "total": 0}
            
        chat_id_str = str(chat_id)
        link = f"https://t.me/c/{chat_id_str[4:]}/{msg_id}" if chat_id_str.startswith("-100") else ""
        link_text = f" <a href='{link}'>[Показати коментар]</a>" if link else ""
        
        if is_auction:
            user_buckets[username]["items"].append(f"• {merch_type} ({booked_price} грн){link_text}")
        else:
            user_buckets[username]["items"].append(f"• {merch_type} {booked_char} ({booked_price} грн){link_text}")
            
        user_buckets[username]["total"] += booked_price
        
    # --- ЗМІНЕНО: Нова залізобетонна логіка нарізки тексту ---
    
    # Спочатку збираємо ВСІ чеки в один довгий текст
    full_text = "📋 <b>ГОТОВІ ТЕКСТИ ДЛЯ ВІДПИСКИ ПОКУПЦЯМ:</b>\n\n"
    
    for username, data in user_buckets.items():
        items_string = "\n".join(data["items"])
        user_block = f"<code>{username}</code>\nПривіт, пишу з приводу броней зі стріма:\n{items_string}\n<b>До сплати:</b> {data['total']} грн.\n___________________________\n\n"
        full_text += user_block
        
    # Тепер ріжемо цей величезний текст на шматки (не більше 4000 символів)
    while len(full_text) > 4000:
        # Шукаємо останній перенос рядка перед лімітом, щоб не розірвати HTML-теги посередині
        split_pos = full_text.rfind('\n', 0, 4000)
        
        # Якщо переносу чомусь немає (дуже малоймовірно), ріжемо жорстко по ліміту
        if split_pos == -1: 
            split_pos = 4000
            
        part_to_send = full_text[:split_pos]
        await callback.message.answer(part_to_send, parse_mode="HTML", disable_web_page_preview=True)
        
        # Відрізаємо відправлену частину від основного тексту і продовжуємо
        full_text = full_text[split_pos:].lstrip('\n')
        
    # Відправляємо залишок тексту, який залишився після всіх відрізань
    if full_text.strip():
        await callback.message.answer(full_text, parse_mode="HTML", disable_web_page_preview=True)
        
    await callback.answer()

@dp.startup()
async def on_startup(bot: Bot):
    for admin_id in NOTIFY_ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "✅ Бот успішно запущений і готовий до роботи на стрімі!")
        except Exception as e:
            print(f"[Помилка] Не вдалося написати адміну {admin_id} про запуск. Можливо, він не натискав /start у ЛС з ботом.")

@dp.shutdown()
async def on_shutdown(bot: Bot):
    for admin_id in NOTIFY_ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "🛑 Бот вимкнений! Обробка броней призупинена.")
        except Exception as e:
            print(f"[Помилка] Не вдалося написати адміну {admin_id} про вимкнення.")
@dp.callback_query(F.data == "my_invoice")
async def get_my_invoice(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Шукаємо броні ТІЛЬКИ для того користувача, який натиснув кнопку
    cursor.execute('''SELECT m.merch_type, b.booked_character, b.booked_price, b.chat_id, b.message_id, m.is_auction 
                      FROM bookings b JOIN merch m ON b.merch_id = m.id 
                      WHERE b.user_id = ?''', (user_id,))
    user_bookings = cursor.fetchall()
    
    if not user_bookings:
        # Якщо броней немає, показуємо спливаюче віконце
        await callback.answer("У тебе поки що немає зафіксованих броней. 🥺", show_alert=True)
        return
        
    items_string_list = []
    total = 0
    
    for merch_type, booked_char, booked_price, chat_id, msg_id, is_auction in user_bookings:
        chat_id_str = str(chat_id)
        link = f"https://t.me/c/{chat_id_str[4:]}/{msg_id}" if chat_id_str.startswith("-100") else ""
        link_text = f" <a href='{link}'>[Показати коментар]</a>" if link else ""
        
        if is_auction:
            items_string_list.append(f"• {merch_type} ({booked_price} грн){link_text}")
        else:
            items_string_list.append(f"• {merch_type} {booked_char} ({booked_price} грн){link_text}")
            
        total += booked_price
        
    items_str = "\n".join(items_string_list)
    
    receipt_msg = (
        f"🧾 <b>ТВІЙ ПОТОЧНИЙ ЧЕК:</b>\n\n"
        f"{items_str}\n\n"
        f"<b>💰 Загалом до сплати:</b> {total} грн."
    )
    
    # --- ДОДАНО: Логіка нарізки тексту для великих особистих чеків ---
    while len(receipt_msg) > 4000:
        split_pos = receipt_msg.rfind('\n', 0, 4000)
        
        if split_pos == -1: 
            split_pos = 4000
            
        part_to_send = receipt_msg[:split_pos]
        await callback.message.answer(part_to_send, parse_mode="HTML", disable_web_page_preview=True)
        
        receipt_msg = receipt_msg[split_pos:].lstrip('\n')
        
    if receipt_msg.strip():
        await callback.message.answer(receipt_msg, parse_mode="HTML", disable_web_page_preview=True)
        
    await callback.answer()

async def main():
    print("Бот запущений! Підтримка аукціонів активована.")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query", "message_reaction", "edited_message"])

if __name__ == "__main__":
    asyncio.run(main())