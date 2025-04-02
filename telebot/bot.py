import telebot
from telebot import types
import sqlite3
from database import create_connection, add_user, get_user, update_balance, get_top_users

bot = telebot.TeleBot("7104621861:AAH4Aj9TSFVDzYlB14Wnw4dgxx9jUXJJbjc")

# Инициализация базы данных при запуске
from database import init_db

init_db()



@bot.message_handler(commands=['start'])
def start(message):
    conn = create_connection()
    if conn:
        add_user(conn, message.from_user.id, message.from_user.username)
        conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_accept = types.KeyboardButton("✅ Согласиться")
    markup.add(button_accept)

    bot.send_message(
        message.chat.id,
        "🔐 Для использования бота необходимо согласиться на обработку данных.",
        reply_markup=markup
    )


# Обработчик кнопки "Согласиться"
@bot.message_handler(func=lambda message: message.text == "✅ Согласиться")
def show_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💰 Баланс")
    btn2 = types.KeyboardButton("📋 Задания")
    btn3 = types.KeyboardButton("🔄 Перевод")
    btn4 = types.KeyboardButton("🏆 Рейтинг")
    btn5 = types.KeyboardButton("🛒 Магазин")
    markup.add(btn1, btn2, btn3, btn4, btn5)

    bot.send_message(message.chat.id, "👇 Выберите действие:", reply_markup=markup)


# Обработчик кнопки "Баланс"
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
                f"Пассивный: {user[3]} баллов"
            )
        else:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")


# Обработчик кнопки "Задания"
@bot.message_handler(func=lambda message: message.text == "📋 Задания")
def tasks(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Перейти к заданиям", url="https://example.com/tasks"))
    bot.send_message(message.chat.id, "Задания доступны в нашем веб-приложении:", reply_markup=markup)


# Обработчик кнопки "Перевод"
@bot.message_handler(func=lambda message: message.text == "🔄 Перевод")
def transfer(message):
    msg = bot.send_message(message.chat.id,
                           "Введите ID получателя и сумму перевода (через пробел):\nПример: 123456789 100")
    bot.register_next_step_handler(msg, process_transfer_amount)


def process_transfer_amount(message):
    try:
        user_id = message.from_user.id
        recipient_id, amount = message.text.split()
        recipient_id = int(recipient_id)
        amount = int(amount)

        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return

        conn = create_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
            return

        # Проверяем существование пользователей
        sender = get_user(conn, user_id)
        recipient = get_user(conn, recipient_id)

        if not sender or not recipient:
            bot.send_message(message.chat.id, "❌ Один из пользователей не найден!")
            conn.close()
            return

        if sender[3] < amount:  # passive_balance
            bot.send_message(message.chat.id, "❌ Недостаточно средств на пассивном балансе!")
            conn.close()
            return

        # Сохраняем данные для перевода
        bot.send_message(
            message.chat.id,
            f"Готово к переводу:\n"
            f"Получатель: @{recipient[1]}\n"
            f"Сумма: {amount} баллов\n\n"
            "Выберите тип перевода:",
            reply_markup=create_transfer_buttons()
        )


        # Сохраняем данные в глобальной переменной (временное решение)
        bot.transfer_data = {
            "sender_id": user_id,
            "recipient_id": recipient_id,
            "amount": amount
        }

        conn.close()

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неправильный формат! Используйте: ID_получателя СУММА")


def create_transfer_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📝 С текстом")
    btn2 = types.KeyboardButton("📨 Без текста")
    markup.add(btn1, btn2)
    return markup


@bot.message_handler(func=lambda message: message.text in ["📝 С текстом", "📨 Без текста"])
def process_transfer_type(message):
    if not hasattr(bot, 'transfer_data'):
        bot.send_message(message.chat.id, "❌ Ошибка: данные перевода утеряны")
        return

    if message.text == "📝 С текстом":
        msg = bot.send_message(message.chat.id, "📝 Введите текст сообщения для получателя:")
        bot.register_next_step_handler(msg, complete_transfer_with_text)
    else:
        complete_transfer_without_text(message)


def complete_transfer_with_text(message):
    if not hasattr(bot, 'transfer_data'):
        bot.send_message(message.chat.id, "❌ Ошибка: данные перевода утеряны")
        return

    conn = create_connection()
    if not conn:
        bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
        return

    data = bot.transfer_data
    sender_id = data["sender_id"]
    recipient_id = data["recipient_id"]
    amount = data["amount"]

    # Обновляем балансы
    sender = get_user(conn, sender_id)
    recipient = get_user(conn, recipient_id)

    new_sender_passive = sender[3] - amount
    new_recipient_active = recipient[2] + amount

    update_balance(conn, sender_id, passive_balance=new_sender_passive)
    update_balance(conn, recipient_id, active_balance=new_recipient_active)

    # Отправляем сообщение получателю
    try:
        bot.send_message(
            recipient_id,
            f"💸 Вам перевели {amount} баллов!\n"
            f"Сообщение от отправителя:\n\n{message.text}"
        )
    except:
        pass  # Если не удалось отправить

    # Возвращаем меню
    show_menu(message)
    bot.send_message(
        message.chat.id,
        f"✅ Перевод выполнен!\n"
        f"Новый пассивный баланс: {new_sender_passive}"
    )

    del bot.transfer_data  # Удаляем временные данные
    conn.close()


def complete_transfer_without_text(message):
    if not hasattr(bot, 'transfer_data'):
        bot.send_message(message.chat.id, "❌ Ошибка: данные перевода утеряны")
        return

    conn = create_connection()
    if not conn:
        bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
        return

    data = bot.transfer_data
    sender_id = data["sender_id"]
    recipient_id = data["recipient_id"]
    amount = data["amount"]

    # Обновляем балансы
    sender = get_user(conn, sender_id)
    recipient = get_user(conn, recipient_id)

    new_sender_passive = sender[3] - amount
    new_recipient_active = recipient[2] + amount

    update_balance(conn, sender_id, passive_balance=new_sender_passive)
    update_balance(conn, recipient_id, active_balance=new_recipient_active)

    # Отправляем сообщение получателю
    try:
        bot.send_message(recipient_id, f"💸 Вам перевели {amount} баллов!")
    except:
        pass  # Если не удалось отправить

    # Возвращаем меню
    show_menu(message)
    bot.send_message(
        message.chat.id,
        f"✅ Перевод выполнен!\n"
        f"Новый пассивный баланс: {new_sender_passive}"
    )

    del bot.transfer_data  # Удаляем временные данные
    conn.close()


# Обработчик кнопки "Рейтинг"
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

    rating_text = "🏆 Топ-5 пользователей:\n\n"
    for i, (username, balance) in enumerate(top_users, 1):
        rating_text += f"{i}. @{username} — {balance} баллов\n"

    bot.send_message(message.chat.id, rating_text)


# Обработчик кнопки "Магазин"
@bot.message_handler(func=lambda message: message.text == "🛒 Магазин")
def shop(message):
    bot.send_message(message.chat.id, "🛍 Магазин скоро откроется! Следите за обновлениями.")



if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling()