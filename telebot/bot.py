import logging

import telebot
from telebot import types

from database import create_connection, add_user, get_user, update_balance, get_top_users, get_user_from_link, do_transfer

bot = telebot.TeleBot("7714684338:AAEynrLWSJNoMWcMgWTvZIOakF_pFc4WZ6s")
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # дебаггер в консоли (опционально)
# Инициализация базы данных при запуске
from database import init_db

init_db()
transfers = dict()

menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("💰 Баланс")
btn2 = types.KeyboardButton("📋 Задания")
btn3 = types.KeyboardButton("🔄 Перевод")
btn4 = types.KeyboardButton("🏆 Рейтинг")
btn5 = types.KeyboardButton("🛒 Магазин")
menu_keyboard.add(btn1, btn2, btn3, btn4, btn5)


@bot.message_handler(commands=['start'])
def start(message):
    conn = create_connection()
    if conn:
        add_user(conn, message.chat.id, message.from_user.username)
        update_balance(conn, message.chat.id, 100, 100)
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
    bot.send_message(message.chat.id, "👇 Выберите действие:", reply_markup=menu_keyboard)


@bot.callback_query_handler(lambda call: call.data == 'get_menu')
def get_menu(call):
    bot.send_message(call.message.chat.id, "👇 Выберите действие:", reply_markup=menu_keyboard)


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
                           "Введите ссылку на пользователя, сумму перевода и комментарий (по желанию) через пробел:\nПример: @example 100 Спасибо!)")
    bot.register_next_step_handler(msg, process_transfer_amount)


def process_transfer_amount(message):
    try:
        data = message.text.split() + ['']
        recipient_link, amount, comment = data[0], int(data[1]), data[2:]
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

        if not sender:
            bot.send_message(message.chat.id, "❌ Вы не прошли регистрацию!")
            conn.close()
            return

        if not recipient:
            bot.send_message(message.chat.id, "❌ Получатель не найден!")
            conn.close()
            return

        if sender[3] < amount:  # passive_balance
            bot.send_message(message.chat.id, "❌ Недостаточно средств на пассивном балансе для перевода!")
            conn.close()
            return

        transfers[f'{sender[0]}'] = (sender, recipient, amount, comment)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button_send = types.InlineKeyboardButton('Отправить', callback_data=f'transfer_from_{sender[0]}')
        button_cancel = types.InlineKeyboardButton('Отменить', callback_data=f'get_menu')
        keyboard.add(button_send, button_cancel)

        # Сохраняем данные для перевода
        bot.send_message(
            message.chat.id,
            f"Готово к переводу:\n"
            f"Получатель: @{recipient[1]}\n"
            f"Сумма: {amount} баллов\n\n"
            "Выберите тип перевода:",
            reply_markup=keyboard
        )

        conn.close()

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неправильный формат! Используйте: ID_получателя СУММА")


@bot.callback_query_handler(lambda call: 'transfer_from_' in call.data)
def transfer_from(call):
    message = call.message

    conn = create_connection()
    sender, recipient, amount, comment = transfers[call.data.split('_')[-1]]
    print(sender, recipient)
    comment = ' '.join(comment)
    do_transfer(conn, sender, recipient, amount)

    transfers[sender[0]] = ()
    bot.send_message(call.message.chat.id, "Перевод успешно отправлен!")
    get_menu(call)

    bot.send_message(recipient[0],
                     f'Вам отправлен перевод от {sender[1]} на сумму {amount}.'
                     f'\n{f"Комментарий: <i>{comment}</i>." if comment else ""}', parse_mode='html')


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
