import logging
import telebot
from telebot import types
from database import *

bot = telebot.TeleBot("7783814922:AAHnHN_U8YlVTuxu8jKkMsqzZ4Gxz3Nh_k0")
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Инициализация базы данных
init_db()
transfers = dict()

# Список товаров
PRODUCTS = [
    {"name": "🖊️ Ручка", "price": 500, "image": "https://i.imgur.com/JqYeYn7.png"},
    {"name": "📔 Блокнот", "price": 1000, "image": "https://i.imgur.com/XWQ5B4y.png"},
    {"name": "🧥 Худи", "price": 3000, "image": "https://i.imgur.com/9Zk7W3v.png"}
]

# Клавиатура меню
menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(
    types.KeyboardButton("💰 Баланс"),
    types.KeyboardButton("📋 Задания"),
    types.KeyboardButton("🔄 Перевод"),
    types.KeyboardButton("🏆 Рейтинг"),
    types.KeyboardButton("🛒 Магазин")
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
            bot.send_message(message.chat.id,
                             f"Ваши балансы:\n\nАктивный: {user[2]} баллов\nПассивный: {user[3]} баллов")
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
            f"Перевод для @{recipient[1]} на {amount} баллов\nПодтвердите:",reply_markup=markup
        )
        conn.close()

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неправильный формат! Используйте: @username сумма")

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_transfer_'))
def confirm_transfer(call):
    user_id = call.data.split('_')[-1]
    if user_id not in transfers:
        bot.answer_callback_query(call.id, "❌ Данные перевода утеряны")
        return

    sender, recipient, amount = transfers[user_id]
    conn = create_connection()
    if conn:
        do_transfer(conn, sender, recipient, amount)
        conn.close()
        bot.send_message(sender[0], f"✅ Перевод @{recipient[1]} на {amount} баллов выполнен!")
        bot.send_message(recipient[0], f"💸 Вам перевели {amount} баллов от @{sender[1]}")
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
        rating_text += f"{i}. @{username} - {balance} баллов\n"

    bot.send_message(message.chat.id, rating_text)

@bot.message_handler(func=lambda message: message.text == "🛒 Магазин")
def shop(message):
    markup = types.InlineKeyboardMarkup()
    for idx, product in enumerate(PRODUCTS):
        markup.add(types.InlineKeyboardButton(f"{product['name']} - {product['price']} баллов", callback_data=f"buy_{idx}"))
    bot.send_message(message.chat.id, "🛍️ Выберите товар:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy(call):
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
        bot.answer_callback_query(call.id, f"❌ Недостаточно средств! Нужно {product['price']} баллов", show_alert=True)
        conn.close()
        return

    # Списание средств и запись покупки
    new_balance = user[2] - product['price']
    update_balance(conn, user_id, active_balance=new_balance)
    add_purchase(conn, user_id, product['name'], product['price'])

    bot.send_photo(
        call.message.chat.id,
        product['image'],
        caption=f"🎉 Вы купили {product['name']} за {product['price']} баллов!\nОжидайте товар!"
    )
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_action(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Действие отменено")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling()

