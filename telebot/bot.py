import logging
from threading import Thread
from time import sleep

import telebot
from telebot import types
from telebot.util import smart_split

from database import *
from keyboards import admin_keyboard, menu_keyboard, cancel_keyboard

bot = telebot.TeleBot("7755530646:AAEhxMZfz7laITd_Ephw61NpL5AfRgDGii4")
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Инициализация базы данных
init_db()

constants = {'rating_size': 5,  # определяет размер рейтингового списка
             'bonus_period': 10,  # определяет время периода выдачи бонуса
             'bonus_amount': 1000,
             'webapp_url': '8c60-115-37-139-49.ngrok-free.app'
             }

# Список товаров
PRODUCTS = [
    {
        "name": "🖊️ Премиум ручка",
        "description": "Эксклюзивная ручка с логотипом проекта",
        "price": 1500,
        "image": "https://brandmedia.su/wa-data/public/photos/73/06/673/673.970x0@2x.jpg"
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
        "image": "https://sun9-63.userapi.com/s/v1/ig2/HIcM9pHSmM-TSeUiPoDnDpxCU9UsHeH5"
                 "QtWql8IDwMxRleT1mo0WtqgSu5r4khDc7ywTB62fNdw5yabJBdJ_Vuuz.jpg?quality="
                 "95&as=32x43,48x64,72x96,108x144,160x213,240x320,360x480,480x639,540x719,"
                 "640x853,720x959,1080x1439,1201x1600&from=bu&u=xrd3D3CKlxxcapbeJULbXE202AJ"
                 "x__K9BbZtgldCDXY&cs=453x604"
    },
    {
        "name": "📖 Открытка на 23 февраля",
        "description": "Эксклюзивная открытка на 23 февраля ",
        "price": 50,
        "image": "https://mosballoon.ru/image/cache/catalog/photo/otkritka_mini_28-800x800.jpg"

    },
    {
        "name": "🏖 путёвка на Байкал",
        "description": "Типо отпуск",
        "price": 100000,
        "image": "https://baikalfoundation.ru/wp-content/uploads/2021/04/14-1400x933.png"
    }
]


def word_for_count(nominative_singular: str = 'Джоуль',
                   genitive: str = 'Джоуля',
                   nominative_plural: str = 'Джоулей',
                   count: int = 1):
    """Функция, возвращающая правильную форму слова для конкретного количества
    на вход: именительный падеж, родительный падеж, именительный падеж во множественном числе, количество

    Пример входных данных: собака, собаки, собак, 3
    Пример выходных данных: собаки"""

    if count % 100 in range(5, 21) or count % 10 in range(5, 10) or count % 10 == 0:
        return nominative_plural
    elif count % 10 in range(2, 5):
        return genitive
    else:
        return nominative_singular


# функция при запуске бота
@bot.message_handler(commands=['start'])
def start(message):
    conn = create_connection()
    bot.send_message(message.chat.id, open('greeting.txt', 'r', encoding='UTF-8').read(), parse_mode='html')
    if not get_user(conn, message.chat.id):
        add_user(conn, message.chat.id, message.from_user.username)
        update_balance(conn, message.chat.id, 100, 100)
        conn.close()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("📄 Пользовательское соглашение"))
        markup.add(types.KeyboardButton("✅ Принять"))

        bot.send_message(message.chat.id, "🔐 Для использования бота необходимо принять пользовательское соглашение:",
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Вход выполнен.')
        show_menu(message)


# функция при нажатии на соответствующую кнопку
@bot.message_handler(func=lambda message: message.text == "🆘 Помощь")
def show_document(message):
    bot.send_message(message.chat.id, open('instruction_for_buttem_help.txt', 'r', encoding='UTF-8').read(),
                     parse_mode='html')


# функция при нажатии на соответствующую кнопку
@bot.message_handler(func=lambda message: message.text == "📄 Пользовательское соглашение")
def show_document(message):
    bot.send_document(message.chat.id, open('user_agreement.docx', 'rb'),
                      caption="📄 Пользовательское соглашение")


# функция при нажатии на соответствующую кнопку или написании пользователем соотв. текстового сообщения
@bot.message_handler(func=lambda message: message.text == "✅ Принять" or message.text == 'Меню')
def show_menu(message):
    conn = create_connection()
    user_role = get_user_role(conn, message.chat.id)
    bot.send_message(message.chat.id, "👇 Выберите действие:",
                     reply_markup=menu_keyboard if user_role == 'пользователь' else admin_keyboard)


# функция при нажатии на соответствующую кнопку
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


# функция при нажатии на соответствующую кнопку
@bot.message_handler(func=lambda message: message.text == "🎮 Игры")
def tasks(message):
    webapp_url = f'https://{constants["webapp_url"]}?chat_id={message.chat.id}'

    tasks_keyboard = types.InlineKeyboardMarkup()
    tasks_keyboard.add(types.InlineKeyboardButton("🎮 Игры", web_app=types.WebAppInfo(url=webapp_url)))

    bot.send_message(message.chat.id, "Играйте и зарабатывайте! Тратьте Джоули на переводы и покупки в магазине!",
                     reply_markup=tasks_keyboard)


@bot.message_handler(func=lambda message: message.text == "🔄 Перевод")
def transfer(message):
    conn = create_connection()
    transfers_today = get_today_transfers_count(conn, message.chat.id)
    conn.close()

    if transfers_today >= 3:
        bot.send_message(message.chat.id,
                         "❌ Вы уже совершили максимальное количество переводов за сегодня (3).\n"
                         "Попробуйте завтра.",
                         reply_markup=menu_keyboard)
        return

    remaining = 3 - transfers_today
    word_transfer = word_for_count("перевод", "перевода", "переводов", remaining)

    msg = bot.send_message(message.chat.id,
                           f"Введите <b>ссылку</b> на пользователя, <b>сумму перевода</b> "
                           f"и комментарий (опционально) через пробел:\n\n"
                           f"Пример: @username 100 Спасибо за помощь)\n\n"
                           f"Осталось переводов сегодня: {remaining} {word_transfer}",
                           parse_mode='html',
                           reply_markup=cancel_keyboard)
    bot.register_next_step_handler(msg, process_transfer_amount)


def process_transfer_amount(message):
    try:
        # Проверяем количество переводов за сегодня
        conn = create_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Ошибка базы данных!")
            return

        transfers_today = get_today_transfers_count(conn, message.chat.id)
        if transfers_today >= 3:
            bot.send_message(message.chat.id,
                             "❌ Вы уже совершили максимальное количество переводов за сегодня (3).\n"
                             "Попробуйте завтра.",
                             reply_markup=menu_keyboard)
            conn.close()
            return

        data = message.text.split()
        if len(data) < 2:
            raise ValueError

        recipient_link = data[0]
        amount = int(data[1])
        comment = ' '.join(data[2:]) if len(data) > 2 else ''
        user_id = message.chat.id

        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            conn.close()
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

        # Сохраняем перевод в базу данных
        transfer_id = add_pending_transfer(conn, sender[0], recipient[0], amount, comment)
        conn.close()

        remaining_transfers = 3 - transfers_today - 1
        word_transfer = word_for_count("перевод", "перевода", "переводов", remaining_transfers)

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_transfer_{transfer_id}"),
            types.InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_transfer_{transfer_id}")
        )

        confirmation_message = f"Перевод для @{recipient[1]} на {amount} {word_for_count(count=amount)}."
        if comment:
            confirmation_message += f"\nКомментарий: {comment}"
        confirmation_message += f"\n\nОсталось переводов сегодня: {remaining_transfers} {word_transfer}"
        confirmation_message += "\nПодтвердите:"

        bot.send_message(
            message.chat.id,
            confirmation_message,
            reply_markup=markup)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неправильный формат! Используйте: @username сумма [комментарий]")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_transfer_'))
def confirm_transfer(call):
    transfer_id = call.data.split('_')[-1]
    conn = create_connection()
    if not conn:
        bot.answer_callback_query(call.id, "❌ Ошибка базы данных")
        return

    # Получаем данные о переводе из базы данных
    pending_transfer = get_pending_transfer(conn, transfer_id)
    if not pending_transfer:
        bot.answer_callback_query(call.id, "❌ Данные перевода утеряны")
        conn.close()
        return

    sender_id, recipient_id, amount, comment = pending_transfer[1], pending_transfer[2], pending_transfer[3], \
        pending_transfer[4]

    # Получаем данные пользователей
    sender = get_user(conn, sender_id)
    recipient = get_user(conn, recipient_id)

    if not sender or not recipient:
        bot.answer_callback_query(call.id, "❌ Один из пользователей не найден")
        conn.close()
        return

    # Выполняем перевод
    do_transfer(conn, sender, recipient, amount)

    # Записываем перевод в историю
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transfers (sender_id, recipient_id, amount)
    VALUES (?, ?, ?)
    ''', (sender_id, recipient_id, amount))
    conn.commit()

    # Удаляем временные данные
    delete_pending_transfer(conn, transfer_id)
    conn.close()

    # Сообщение отправителю
    sender_message = f"✅ Вы перевели @{recipient[1]} {amount} {word_for_count(count=amount)}"
    if comment:
        sender_message += f"\nКомментарий: {comment}"
    bot.send_message(sender[0], sender_message)

    # Сообщение получателю
    recipient_message = f"💸 Вам перевели {amount} {word_for_count(count=amount)} от @{sender[1]}"
    if comment:
        recipient_message += f"\nКомментарий: {comment}"
    bot.send_message(recipient[0], recipient_message)

    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_transfer_'))
def cancel_transfer(call):
    transfer_id = call.data.split('_')[-1]
    conn = create_connection()
    if conn:
        delete_pending_transfer(conn, transfer_id)
        conn.close()

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Перевод отменен")


# функция при нажатии на соответствующую кнопку
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


# функция при нажатии на соответствующую кнопку
@bot.message_handler(func=lambda message: message.text == "🛒 Магазин")
def shop(message):
    markup = types.InlineKeyboardMarkup()
    for idx, product in enumerate(PRODUCTS):
        markup.add(
            types.InlineKeyboardButton(
                f"{product['name']} - {product['price']} {word_for_count(count=product['price'])}",
                callback_data=f"buy_{idx}"))
    bot.send_message(message.chat.id, "🛍️ Выберите товар:", reply_markup=markup)


# функция показа карточки товара с кнопками купить и отменить
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
                callback_data="cancel_purchase"
            )
        )

        # Отправляем сообщение с товаром
        bot.send_photo(
            call.message.chat.id,
            product['image'],
            caption=(
                f"<b>{product['name']}</b>\n\n"
                f"{product['description']}\n\n"
                f"💵 Цена: {product['price']} активных {word_for_count(count=product['price'])}\n"
                f"💰 Ваш баланс: {user[2]} {word_for_count(count=product['price'])}"
            ),
            parse_mode="HTML",
            reply_markup=markup
        )

    except IndexError:
        bot.answer_callback_query(call.id, "❌ Товар не найден!")
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка!")


# функция при подтверждении покупки пользователем
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

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(
        call.message.chat.id,
        product['image'],
        caption=(
            f"🎉 Поздравляем с покупкой!\n\n"
            f"<b>{product['name']}</b>\n"
            f"💰 Потрачено: {product['price']} {word_for_count(count=product['price'])}\n"
            f"💳 Новый баланс: {new_balance} {word_for_count(count=new_balance)}\n\n"
            "🛍️ Ожидайте товар!"
        ),
        parse_mode="HTML"
    )
    conn.close()


# функция отмены покупки
@bot.callback_query_handler(func=lambda call: call.data == 'cancel_purchase')
def cancel_purchase(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Покупка отменена")


# универсальная функция отмены ввода каких-либо данных
@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_action(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Действие отменено")


# функция при отправке команды /history
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
        history_text += f"🛒 {item[0]} - {item[1]} {word_for_count(count=item[1])}\n"
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
            history_text += f"🛒 {item[0]} - {item[1]} {word_for_count(count=item[1])}\n"
            history_text += f"📅 {item[2]}\n\n"

    # Добавляем переводы
    if transfers:
        history_text += "💸 <b>Переводы:</b>\n"
        for item in transfers:
            direction = "Отправлен" if item[3] == "out" else "Получен"
            username = item[2] if item[2] else "пользователь"
            history_text += f"🔄 {direction} перевод {item[1]} баллов\n"
            history_text += f"👤 @{username}\n" if username != "пользователь" else f"👤 {username}\n"
            history_text += f"📅 {item[0]}\n\n"

    # Разбиваем сообщение на части, если оно слишком длинное
    for part in smart_split(history_text):
        bot.send_message(message.chat.id, part, parse_mode="HTML")


# функция при нажатии на соответствующую кнопку
@bot.message_handler(func=lambda message: message.text == "😡 Выдать штраф")
def take_fine(message):
    conn = create_connection()
    user_role = get_user_role(conn, message.chat.id)

    if user_role == 'администратор':
        msg = bot.send_message(message.chat.id, 'Введите ссылку на пользователя, '
                                                'количество изымаемой валюты и комментарий через пробел.'
                                                '\n\nПример: @test 1000 Плохо себя вёл!', reply_markup=cancel_keyboard)
        bot.register_next_step_handler(msg, take_fine_by_user_link)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к этому функционалу.',
                         reply_markup=menu_keyboard)


# функция изымания средств со счета пользователя по запросу администратора (штраф)
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


# функция при нажатии на соответствующую кнопку
@bot.message_handler(func=lambda message: message.text == "⏱️ Сменить время бонуса")
def change_bonus_time(message):
    word_minute = word_for_count("минута", "минуты", "минут", constants["bonus_period"])

    bot.send_message(message.chat.id, f'Текущий период зачисления: {constants["bonus_period"]} {word_minute}.'
                                      f'\n\nВведите новое время <b>в минутах</b> (число):',
                     reply_markup=cancel_keyboard,
                     parse_mode='html')
    bot.register_next_step_handler(message, do_change_time)


# функция изменения периодичности выдачи бонуса
def do_change_time(message):
    global thrd
    try:
        constants['bonus_period'] = int(message.text)
        word_minute = word_for_count("минута", "минуты", "минут", constants["bonus_period"])
        bot.send_message(message.chat.id, f'Успешно! Теперь период зачисления бонуса: '
                                          f'<b>{constants["bonus_period"]} '
                                          f'{word_minute}.</b>',
                         parse_mode='html')

        if thrd.is_alive():  # отмена создания нового потока, если он уже есть
            return
        else:
            thrd = Thread(target=periodic_bonus)  # создание новой задачи с другим периодом
            thrd.start()

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неправильный формат ввода! "
                                          "Введите число без дополнительных знаков.")
        return


# функция периодического начисления бонуса
def periodic_bonus():
    while constants['bonus_period']:
        conn = create_connection()
        user_ids = get_users(conn)
        for user in user_ids:
            update_balance(conn, user[0], passive_balance=user[3] + constants['bonus_amount'])
            bot.send_message(user[0], f'Вам зачислен бонус на пассивный счёт в размере {constants["bonus_amount"]} '
                                      f'{word_for_count(count=constants["bonus_amount"])}.')
        sleep(constants['bonus_period'] * 60)


# функция при нажатии на соответствующую кнопку
@bot.message_handler(func=lambda message: message.text == "🗿 Пользователи")
def get_users_for_admin(message):
    conn = create_connection()
    users = get_users(conn)
    list_string = '\n'.join(
        [f'ID: {user[0]}, ссылка: @{user[1]}, роль: {get_role_name(conn, user[4])}' for user in users])
    list_string = smart_split(list_string)
    for msg in list_string:
        bot.send_message(message.chat.id, msg)


# функция при нажатии на соответствующую кнопку
@bot.message_handler(func=lambda message: message.text == "📥 Новый администратор")
def make_admin(message):
    bot.send_message(message.chat.id, "Введите ссылку на пользователя:\n\n"
                                      "Пример: <b>@test</b>",
                     parse_mode='html',
                     reply_markup=cancel_keyboard)
    bot.register_next_step_handler(message, make_admin_by_link)


# выдача прав администратора пользователю, если все ок
def make_admin_by_link(message):
    conn = create_connection()
    result = make_user_admin(conn, message.text.strip('@'))
    bot.send_message(message.chat.id, result)
    if '❌' in result:
        return
    bot.send_message(get_user_from_link(conn, message.text.strip('@'))[0],
                     'Вам выдали права администратора! Напишите Меню, чтобы обновить клавиатуру меню.')


# запуск бота и периодического начисления бонуса
if __name__ == "__main__":
    thrd = Thread(target=periodic_bonus)  # отдельный поток для начислений бонусов
    thrd.start()
    bot.infinity_polling()
