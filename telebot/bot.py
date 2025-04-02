import logging

import telebot
from telebot import types

from database import *
from keyboards import admin_keyboard, menu_keyboard

bot = telebot.TeleBot("7714684338:AAEynrLWSJNoMWcMgWTvZIOakF_pFc4WZ6s")
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Инициализация базы данных
init_db()
transfers = dict()

constants = {'rating_size': 5,  # определяет размер рейтингового списка
             'fake_bonus_time': 10}  # временная переменная, определяет время периода выдачи бонуса

# Список товаров
PRODUCTS = [
    {"name": "🖊️ Ручка", "price": 500, "image": "https://i.imgur.com/JqYeYn7.png"},
    {"name": "📔 Блокнот", "price": 1000, "image": "https://i.imgur.com/XWQ5B4y.png"},
    {"name": "🧥 Худи", "price": 3000, "image": "https://i.imgur.com/9Zk7W3v.png"}
]


# функция, возвращающая правильную форму слова
# именительный падеж, родительный падеж, именительный падеж во множественном числе
# пример входных данных: собака, собаки, собак, 3
# пример выходных данных: собаки
def word_for_count(nominative_singular: str = 'Джоуль',
                   genitive: str = 'Джоуля',
                   nominative_plural: str = 'Джоулей',
                   count: int = 1):
    if count % 100 in range(5, 21) or count % 10 in range(5, 10) or count % 10 == 0:
        return nominative_plural
    elif count % 10 in range(2, 5):
        return genitive
    else:
        return nominative_singular


@bot.message_handler(commands=['start'])
def start(message):
    conn = create_connection()
    if not get_user(conn, message.chat.id):
        add_user(conn, message.chat.id, message.from_user.username)
        update_balance(conn, message.chat.id, 100, 100)
        conn.close()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("📄 Пользовательское соглашение"))
        markup.add(types.KeyboardButton("✅ Принять"))
        bot.send_message(message.chat.id, "Добро пожаловать!\n\n"
                                          "🔐 Для использования бота необходимо принять пользовательское соглашение:",
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Вход выполнен.')
        show_menu(message)


@bot.message_handler(func=lambda message: message.text == "📄 Пользовательское соглашение")
def show_document(message):
    bot.send_document(message.chat.id, open('user_agreement.docx', 'rb'),
                      caption="📄 Пользовательское соглашение")


@bot.message_handler(func=lambda message: message.text == "✅ Принять" or message.text == 'Меню')
def show_menu(message):
    conn = create_connection()
    user_role = get_user_role(conn, message.chat.id)
    print(user_role)
    bot.send_message(message.chat.id, "👇 Выберите действие:",
                     reply_markup=menu_keyboard if user_role == 'пользователь' else admin_keyboard)


@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    conn = create_connection()
    if conn:
        user = get_user(conn, message.from_user.id)
        conn.close()
        if user:
            bot.send_message(message.chat.id,
                             f"Ваши балансы:"
                             f"\n\n<b>Активный:</b> {user[2]} {word_for_count(count=user[2])}\n"
                             f"<b>Пассивный:</b> {user[3]} {word_for_count(count=user[3])}\n\n"
                             f"<i><b>Активный счёт</b> используется для покупок в магазине или"
                             f" назначения награды за задания.\nЗарабатывайте Джоули и вырывайтесь в топ Рейтинга!\n\n"
                             f"<b>Пассивный счёт</b> используется для переводов другим пользователям, "
                             f"периодически он пополняется системой.</i>",
                             parse_mode='html')
        else:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")


@bot.message_handler(func=lambda message: message.text == "📋 Задания")
def tasks(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🗂 Перейти к заданиям", url="https://example.com/tasks"))
    bot.send_message(message.chat.id, "Задания доступны в нашем веб-приложении:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🔄 Перевод")
def transfer(message):
    under_keyboard = types.InlineKeyboardMarkup(row_width=1)
    cancel_button = types.InlineKeyboardButton('Отмена', callback_data='cancel')
    under_keyboard.add(cancel_button)
    msg = bot.send_message(message.chat.id,
                           "Введите <b>ссылку</b> на пользователя, <b>сумму перевода</b> "
                           "и комментарий (опционально) через пробел:\n\nПример: @username 100 Спасибо за помощь)",
                           parse_mode='html',
                           reply_markup=under_keyboard)
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

        elif sender[3] < amount:
            bot.send_message(message.chat.id, "❌ Недостаточно средств на пассивном балансе!")
            conn.close()
            return

        elif sender[0] == recipient[0]:
            bot.send_message(message.chat.id, "❌ Нельзя переводить самому себе!")
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
            f"Перевод для @{recipient[1]} на {amount} {word_for_count(count=amount)}.\n"
            f"Подтвердите:", reply_markup=markup)
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
        bot.send_message(sender[0], f"✅ Перевод @{recipient[1]} на {amount} {word_for_count(count=amount)} выполнен!")
        bot.send_message(recipient[0], f"💸 Вам перевели {amount} {word_for_count(count=amount)} от @{sender[1]}.")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        del transfers[user_id]


@bot.message_handler(func=lambda message: message.text == "🏆 Рейтинг")
def rating(message):
    conn = create_connection()
    if not conn:
        bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
        return

    top_users = get_top_users(conn, constants['rating_size'])
    user_rating_place = get_user_place_in_top(conn, message.chat.id)
    conn.close()

    if not top_users:
        bot.send_message(message.chat.id, "🏆 Рейтинг пока пуст!")
        return

    rating_text = "🏆 Топ пользователей:\n\n"
    for i, (username, balance) in enumerate(top_users, 1):
        rating_text += f"{i}. @{username} : <b>{balance}</b> {word_for_count(count=balance)}\n"

    rating_text += f'\n\n...Вы занимаете <b>{user_rating_place}</b> место в рейтинге.' \
        if user_rating_place > constants['rating_size'] else ''

    bot.send_message(message.chat.id, rating_text, parse_mode='html')


@bot.message_handler(func=lambda message: message.text == "🛒 Магазин")
def shop(message):
    markup = types.InlineKeyboardMarkup()
    for idx, product in enumerate(PRODUCTS):
        markup.add(
            types.InlineKeyboardButton(
                f"{product['name']} - {product['price']} {word_for_count(count=product['price'])}",
                callback_data=f"buy_{idx}"))
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
        bot.answer_callback_query(call.id,
                                  f"❌ Недостаточно средств! Нужно "
                                  f"{product['price']} {word_for_count(count=product['price'])}",
                                  show_alert=True)
        conn.close()
        return

    # Списание средств и запись покупки
    new_balance = user[2] - product['price']
    update_balance(conn, user_id, active_balance=new_balance)
    add_purchase(conn, user_id, product['name'], product['price'])

    bot.send_photo(
        call.message.chat.id,
        product['image'],
        caption=f"🎉 Вы купили {product['name']} за {product['price']}"
                f" {word_for_count(count=product['price'])}!\nОжидайте товар!"
    )
    conn.close()


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_action(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Действие отменено")


@bot.message_handler(func=lambda message: message.text == "😡 Выдать штраф")
def take_fine(message):
    conn = create_connection()
    user_role = get_user_role(conn, message.chat.id)

    if user_role == 'администратор':
        fine_keyboard = types.InlineKeyboardMarkup(row_width=1)
        cancel_button = types.InlineKeyboardButton('Отмена', callback_data='cancel')
        fine_keyboard.add(cancel_button)

        msg = bot.send_message(message.chat.id, 'Введите ссылку на пользователя, '
                                                'количество изымаемой валюты и комментарий через пробел.'
                                                '\n\nПример: @test 1000 Плохо себя вёл!', reply_markup=fine_keyboard)
        bot.register_next_step_handler(msg, take_fine_by_user_link)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к этому функционалу.',
                         reply_markup=menu_keyboard)


def take_fine_by_user_link(message):
    try:
        conn = create_connection()
        data = message.text.split() + ['']
        user_link, amount, comment = data[0].strip('@'), int(data[1]), data[2:]
        user = get_user_from_link(conn, user_link)
        comment = " ".join(comment)

        if not user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!",
                             reply_markup=admin_keyboard)
            conn.close()
            return

        update_balance(conn, user[0], active_balance=user[2] - amount)
        bot.send_message(message.chat.id,
                         f'Списание {amount} {word_for_count(count=amount)} со счёта {user[1]} успешно!',
                         reply_markup=admin_keyboard)
        bot.send_message(user[0],
                         f'<b>Вы оштрафованы администратором на {amount} {word_for_count(count=amount)}.</b> '
                         f'{"Комментарий: " + "<i>" + comment + "</i>" if comment.strip() else ""}',
                         parse_mode='html')

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неправильный формат ввода!"
                                          " Используйте: [@username] [сумма] [комментарий]")


@bot.message_handler(func=lambda message: message.text == "⏱️ Сменить время бонуса")
def change_bonus_time(message):
    change_keyboard = types.InlineKeyboardMarkup(row_width=1)
    cancel_button = types.InlineKeyboardButton('Отмена', callback_data='cancel')
    change_keyboard.add(cancel_button)

    word_minute = word_for_count("минута", "минуты", "минут", constants["fake_bonus_time"])

    bot.send_message(message.chat.id, f'Текущий период зачисления: {constants["fake_bonus_time"]} {word_minute}.'
                                      f'\n\nВведите новое время <b>в минутах</b> (число):',
                     reply_markup=change_keyboard,
                     parse_mode='html')
    bot.register_next_step_handler(message, do_change_time)


def do_change_time(message):
    try:
        constants['fake_bonus_time'] = int(message.text)
        word_minute = word_for_count("минута", "минуты", "минут", constants["fake_bonus_time"])
        bot.send_message(message.chat.id, f'Успешно! Теперь период зачисления бонуса: '
                                          f'<b>{constants["fake_bonus_time"]} '
                                          f'{word_minute}.</b>',
                         parse_mode='html')
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неправильный формат ввода! "
                                          "Введите число без дополнительных знаков.")


if __name__ == "__main__":
    bot.infinity_polling()
