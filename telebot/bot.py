import logging
import telebot
from telebot import types
from database import *
import schedule
import time
import threading
from datetime import datetime, timedelta

bot = telebot.TeleBot("7783814922:AAHnHN_U8YlVTuxu8jKkMsqzZ4Gxz3Nh_k0")
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Инициализация базы данных
init_db()
transfers = dict()

# Функция для пассивного дохода
def add_passive_income():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Начисляем 1000 баллов всем пользователям
            cursor.execute("UPDATE users SET passive_balance = passive_balance + 1000")
            conn.commit()
            print("Успешно начислен пассивный доход всем пользователям")
        except Exception as e:
            print(f"Ошибка при начислении пассивного дохода: {e}")
        finally:
            conn.close()


# Запуск планировщика в отдельном потоке
def run_scheduler():
    schedule.every(3).minutes.do(add_passive_income)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запускаем планировщик
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

@bot.message_handler(commands=['start'])
def start(message):
    conn = create_connection()
    if conn:
        add_user(conn, message.chat.id, message.from_user.username)
        update_balance(conn, message.chat.id, 100, 100)
        conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("✅ Согласиться"))
    bot.send_message(
        message.chat.id,
        "🔐 Для использования бота необходимо согласиться на обработку данных.\n\n"
        "💡 Каждые 3 минуты вам будет начисляться 1000 пассивных баллов!",
        reply_markup=markup
    )

# Список товаров
PRODUCTS = [
    {
        "name": "🖊️ Премиум ручка",
        "description": "Эксклюзивная ручка с логотипом проекта",
        "price": 1500,
        "image": "https://storage.yandexcloud.net/mostro-gm-media/ea9ede2f-968c-9ddd-5cb0-afa64553bf12/4.jpg"
    },
    {
        "name": "📔 Блокнот PRO",
        "description": "Качественный блокнот в твердой обложке",
        "price": 2500,
        "image": "https://fastcolor.ru/wp-content/uploads/2024/01/gazprom-energoholding-bloknoty_3.jpg"
    },
    {
        "name": "🧥 Худи с принтом",
        "description": "Удобное худи с уникальным принтом",
        "price": 5000,
        "image": "https://sun9-63.userapi.com/s/v1/ig2/HIcM9pHSmM-TSeUiPoDnDpxCU9UsHeH5QtWql8IDwMxRleT1mo0WtqgSu5r4khDc7ywTB62fNdw5yabJBdJ_Vuuz.jpg?quality=95&as=32x43,48x64,72x96,108x144,160x213,240x320,360x480,480x639,540x719,640x853,720x959,1080x1439,1201x1600&from=bu&u=xrd3D3CKlxxcapbeJULbXE202AJx__K9BbZtgldCDXY&cs=453x604"
    },
{
        "name": "📖 Открытка на 23 февраля",
        "description": "Эксклюзивная открытка на 23 февраля ",
        "price": 50,
        "image": "https://s8.stc.all.kpcdn.net/family/wp-content/uploads/2024/02/title-photo-in-otkrytki-s-23-fevralja-960x540-1.jpg"
    },
{
        "name": "🏖 путёвка на Байкал",
        "description": "Типо отпуск",
        "price": 100000,
        "image": "https://baikalfoundation.ru/wp-content/uploads/2021/04/14-1400x933.png"
    }
]

# Клавиатура меню
menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(
    types.KeyboardButton("💰 Баланс"),
    types.KeyboardButton("📋 Задания"),
    types.KeyboardButton("🔄 Перевод"),
    types.KeyboardButton("🏆 Рейтинг"),
    types.KeyboardButton("🛒 Магазин"),
    types.KeyboardButton("📜 История")
)


@bot.message_handler(commands=['start'])
def start(message):
    conn = create_connection()
    if conn:
        add_user(conn, message.chat.id, message.from_user.username)
        update_balance(conn, message.chat.id, 100, 100)
        conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("✅ Согласиться"))
    bot.send_message(message.chat.id, "🔐 Для использования бота необходимо согласиться на обработку данных.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "✅ Согласиться")
def show_menu(message):
    bot.send_message(message.chat.id, "👇 Выберите действие:", reply_markup=menu_keyboard)


@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    conn = create_connection()
    if conn:
        user = get_user(conn, message.from_user.id)
        conn.close()
        if user:
            bot.send_message(
                message.chat.id,
                f"Ваши балансы:\n\n"
                f"Активный: {user[2]} баллов\n"
                f"Пассивный: {user[3]} баллов\n\n"
                f"💡 Следующее начисление через 3 минуты"
            )
        else:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")


@bot.message_handler(func=lambda message: message.text == "📋 Задания")
def tasks(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Перейти к заданиям", url="https://example.com/tasks"))
    bot.send_message(message.chat.id, "Задания доступны в нашем веб-приложении:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🔄 Перевод")
def transfer(message):
    msg = bot.send_message(message.chat.id,
                           "Введите ссылку на пользователя и сумму перевода через пробел:\nПример: @username 100")
    bot.register_next_step_handler(msg, process_transfer_amount)


def process_transfer_amount(message):
    try:
        data = message.text.split()
        if len(data) < 2:
            raise ValueError

        recipient_link, amount = data[0], int(data[1])
        user_id = message.chat.id

        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return

        conn = create_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
            return

        # Проверка на перевод самому себе
        if recipient_link.strip('@') == message.from_user.username:
            bot.send_message(message.chat.id, "❌ Нельзя переводить деньги самому себе!")
            conn.close()
            return

        # Проверка количества переводов за сегодня
        today = datetime.now().date()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM transfers 
            WHERE sender_id = ? AND date(transfer_date) = ?
        ''', (user_id, today))
        transfers_today = cursor.fetchone()[0]

        if transfers_today >= 3:
            bot.send_message(message.chat.id, "❌ Вы уже сделали 3 перевода сегодня! Лимит исчерпан.")
            conn.close()
            return

        recipient = get_user_from_link(conn, recipient_link)
        sender = get_user(conn, user_id)

        if not sender or not recipient:
            bot.send_message(message.chat.id, "❌ Один из пользователей не найден!")
            conn.close()
            return

        if sender[3] < amount:
            bot.send_message(message.chat.id, "❌ Недостаточно средств на пассивном балансе!")
            conn.close()
            return

        transfers[str(user_id)] = (sender, recipient, amount)

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_transfer_{user_id}"),
            types.InlineKeyboardButton("❌ Отменить", callback_data="cancel")
        )

        bot.send_message(
            message.chat.id,
            f"Перевод для @{recipient[1]} на {amount} Джоулей\nПодтвердите:",
            reply_markup=markup
        )
        conn.close()

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неправильный формат! Используйте: @username сумма")


# Обновляем функцию confirm_transfer
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_transfer_'))
def confirm_transfer(call):
    user_id = call.data.split('_')[-1]
    if user_id not in transfers:
        bot.answer_callback_query(call.id, "❌ Данные перевода утеряны")
        return

    sender, recipient, amount = transfers[user_id]
    conn = create_connection()
    if conn:
        # Записываем перевод в базу
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transfers (sender_id, recipient_id, amount, transfer_date)
            VALUES (?, ?, ?, datetime('now'))
        ''', (sender[0], recipient[0], amount))

        # Выполняем перевод
        do_transfer(conn, sender, recipient, amount)
        conn.close()

        bot.send_message(sender[0], f"✅ Перевод @{recipient[1]} на {amount} Джоулей выполнен!")
        bot.send_message(recipient[0], f"💸 Вам перевели {amount} Джоулей от @{sender[1]}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        del transfers[user_id]

@bot.message_handler(func=lambda message: message.text == "🏆 Рейтинг")
def rating(message):
    conn = create_connection()
    if not conn:
        bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
        return

    top_users = get_top_users(conn)
    conn.close()

    if not top_users:
        bot.send_message(message.chat.id, "🏆 Рейтинг пока пуст!")
        return

    rating_text = "🏆 Топ пользователей:\n\n"
    for i, (username, balance) in enumerate(top_users, 1):
        rating_text += f"{i}. @{username} - {balance} Джоулей\n"

    bot.send_message(message.chat.id, rating_text)

@bot.message_handler(func=lambda message: message.text == "🛒 Магазин")
def shop(message):
    markup = types.InlineKeyboardMarkup()
    for i, product in enumerate(PRODUCTS):
        markup.add(
            types.InlineKeyboardButton(
                f"{product['name']} - {product['price']} баллов",
                callback_data=f"buy_{i}"
            )
        )
    bot.send_message(message.chat.id, "🛍️ Магазин мерча. Выберите товар:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_product_selection(call):
    try:
        product_id = int(call.data.split('_')[1])  # Получаем ID товара из callback_data
        product = PRODUCTS[product_id]  # Получаем товар из списка

        conn = create_connection()
        if not conn:
            bot.answer_callback_query(call.id, "❌ Ошибка базы данных!")
            return

        user = get_user(conn, call.from_user.id)
        conn.close()

        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден!")
            return

        # Создаем клавиатуру с кнопками
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(
                "✅ Купить",
                callback_data=f"confirm_{product_id}"  # Используем product_id здесь
            ),
            types.InlineKeyboardButton(
                "❌ Отмена",
                callback_data="cancel"
            )
        )

        # Отправляем сообщение с товаром
        bot.send_photo(
            call.message.chat.id,
            product['image'],
            caption=(
                f"<b>{product['name']}</b>\n\n"
                f"{product['description']}\n\n"
                f"💵 Цена: {product['price']} активных баллов\n"
                f"💰 Ваш баланс: {user[2]} баллов"
            ),
            parse_mode="HTML",
            reply_markup=markup
        )

    except IndexError:
        bot.answer_callback_query(call.id, "❌ Товар не найден!")
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка!")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def confirm_purchase(call):
    product_id = int(call.data.split('_')[1])
    product = PRODUCTS[product_id]
    user_id = call.from_user.id

    conn = create_connection()
    if not conn:
        bot.answer_callback_query(call.id, "❌ Ошибка базы данных!")
        return

    user = get_user(conn, user_id)

    if not user:
        bot.answer_callback_query(call.id, "❌ Пользователь не найден!")
        conn.close()
        return

    if user[2] < product['price']:
        bot.answer_callback_query(
            call.id,
            f"❌ Недостаточно активных баллов! Нужно {product['price']}",
            show_alert=True
        )
        conn.close()
        return

    # Списание средств и запись покупки
    new_balance = user[2] - product['price']
    update_balance(conn, user_id, active_balance=new_balance)
    add_purchase(conn, user_id, product['name'], product['price'])

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(
        call.message.chat.id,
        product['image'],
        caption=(
            f"🎉 Поздравляем с покупкой!\n\n"
            f"<b>{product['name']}</b>\n"
            f"💰 Потрачено: {product['price']} баллов\n"
            f"💳 Новый баланс: {new_balance} баллов\n\n"
            "🛍️ Ожидайте товар!"
        ),
        parse_mode="HTML"
    )
    conn.close()


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_purchase(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Покупка отменена")


@bot.message_handler(commands=['history'])
def purchase_history(message):
    conn = create_connection()
    if not conn:
        bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
        return

    history = get_purchase_history(conn, message.from_user.id)
    conn.close()

    if not history:
        bot.send_message(message.chat.id, "📦 У вас ещё нет покупок")
        return

    history_text = "📜 История ваших покупок:\n\n"
    for item in history:
        history_text += f"🛒 {item[0]} - {item[1]} баллов\n"
        history_text += f"📅 {item[2]}\n\n"

    bot.send_message(message.chat.id, history_text)


# Обработчик для кнопки "История"
@bot.message_handler(func=lambda message: message.text == "📜 История")
def purchase_history(message):
    conn = create_connection()
    if not conn:
        bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
        return

    # Получаем историю покупок и переводов
    purchases = get_purchase_history(conn, message.from_user.id)
    transfers = get_transfer_history(conn, message.from_user.id)
    conn.close()

    if not purchases and not transfers:
        bot.send_message(message.chat.id, "📦 У вас ещё нет истории операций")
        return

    history_text = "📜 История ваших операций:\n\n"

    # Добавляем покупки
    if purchases:
        history_text += "🛍️ <b>Покупки:</b>\n"
        for item in purchases:
            history_text += f"🛒 {item[0]} - {item[1]} баллов\n"
            history_text += f"📅 {item[2]}\n\n"

    # Добавляем переводы
    if transfers:
        history_text += "💸 <b>Переводы:</b>\n"
        for item in transfers:
            direction = "Отправлен" if item[3] == "out" else "Получен"
            history_text += f"🔄 {direction} перевод {item[1]} баллов\n"
            history_text += f"👤 {'@' + item[2] if item[2] else 'пользователь'}\n"
            history_text += f"📅 {item[0]}\n\n"

    bot.send_message(message.chat.id, history_text, parse_mode="HTML")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling()

