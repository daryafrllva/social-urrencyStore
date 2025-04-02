import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import random
from database import get_or_create_user, update_user, get_all_users

# Инициализация бота
bot = AsyncTeleBot('YOUR_TELEGRAM_BOT_TOKEN')  # Замените на свой токен

# Фиксированные мемы
MEMES = {
    "meme1": {"image_url": "https://example.com/meme1.jpg", "price": 50, "caption": "Терапевт дуреет с этой прикормки"},
    "meme2": {"image_url": "https://example.com/meme2.jpg", "price": 75, "caption": "Когда выходишь из магазина без покупок"},
    "meme3": {"image_url": "https://example.com/meme3.jpg", "price": 100, "caption": "О Господи, это новая эмоция?!"},
    "meme4": {"image_url": "https://example.com/meme4.jpg", "price": 80, "caption": "Бу! Испугался?! Не бойся"},
}

# Словарь для хранения состояний пользователей
user_states = {}

# Команда /start
@bot.message_handler(commands=['start'])
async def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Баланс"), types.KeyboardButton("Задания"))
    markup.add(types.KeyboardButton("Перевод"), types.KeyboardButton("Рейтинг"))
    markup.add(types.KeyboardButton("Магазин"))

    await bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Обработка кнопок
@bot.message_handler(func=lambda message: True)
async def handle_buttons(message):
    user_id = message.from_user.id
    user_data = get_or_create_user(user_id)

    if message.text == "Баланс":
        active_balance = user_data["active_balance"]
        passive_balance = user_data["passive_balance"]
        await bot.send_message(message.chat.id, f"Активный счет: {active_balance} монет\nПассивный счет: {passive_balance} монет")

    elif message.text == "Задания":
        await bot.send_message(message.chat.id, "Тут что-то будет", reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Открыть задания", url="https://example.com")
        ))

    elif message.text == "Перевод":
        await bot.send_message(message.chat.id, "Введите ID получателя и сумму через пробел:")
        user_states[user_id] = "waiting_for_transfer"

    elif message.text == "Рейтинг":
        rating = get_all_users()
        rating.sort(key=lambda x: x["balance"], reverse=True)

        rating_message = "Топ пользователей по активным монеткам:\n"
        for i, user in enumerate(rating[:5], start=1):
            rating_message += f"{i}. {user['name']} - {user['balance']} монет\n"

        await bot.send_message(message.chat.id, rating_message)

    elif message.text == "Магазин":
        shop_message = "Доступные мемы:\n"
        for meme_id, meme_info in MEMES.items():
            shop_message += f"{meme_id}: {meme_info['caption']} - {meme_info['price']} монет\n"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for meme_id in MEMES.keys():
            markup.add(types.KeyboardButton(f"Купить {meme_id}"))
        markup.add(types.KeyboardButton("Выйти в меню"))
        markup.add(types.KeyboardButton("Посмотреть купленные мемы"))

        await bot.send_message(message.chat.id, shop_message, reply_markup=markup)

    elif message.text == "Выйти в меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Баланс"), types.KeyboardButton("Задания"))
        markup.add(types.KeyboardButton("Перевод"), types.KeyboardButton("Рейтинг"))
        markup.add(types.KeyboardButton("Магазин"))

        await bot.send_message(message.chat.id, "Вы вернулись в главное меню.", reply_markup=markup)

    elif message.text == "Посмотреть купленные мемы":
        purchased_memes = user_data.get("purchased_memes", [])
        if not purchased_memes:
            await bot.send_message(message.chat.id, "У вас пока нет купленных мемов.")
            return

        response = "Ваши купленные мемы:\n"
        for meme_id in purchased_memes:
            meme_info = MEMES[meme_id]
            response += f"- {meme_info['caption']}\n"

        await bot.send_message(message.chat.id, response)

# Обработка перевода между пользователями
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_transfer")
async def process_transfer(message):
    try:
        parts = message.text.split()
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
            await bot.send_message(message.chat.id, "Некорректный формат. Введите ID получателя и сумму через пробел.")
            return

        recipient_id = int(parts[0])
        amount = int(parts[1])

        sender_data = get_or_create_user(message.from_user.id)
        recipient_data = get_or_create_user(recipient_id)

        if sender_data["passive_balance"] >= amount > 0:
            sender_data["passive_balance"] -= amount
            recipient_data["active_balance"] += amount

            update_user(sender_data["user_id"], {"passive_balance": sender_data["passive_balance"]})
            update_user(recipient_data["user_id"], {"active_balance": recipient_data["active_balance"]})

            await bot.send_message(message.chat.id, f"Вы выполнили перевод {amount} монет пользователю {recipient_id}.")
            await bot.send_message(recipient_id, f"Вы получили перевод {amount} монет от пользователя {message.from_user.id}.")
        else:
            await bot.send_message(message.chat.id, "Недостаточно средств на пассивном счете или некорректная сумма.")
    except Exception as e:
        await bot.send_message(message.chat.id, "Ошибка при переводе. Попробуйте снова.")
    finally:
        user_states.pop(message.from_user.id, None)

# Покупка мемов
@bot.message_handler(func=lambda message: message.text.startswith("Купить "))
async def buy_meme(message):
    user_id = message.from_user.id
    user_data = get_or_create_user(user_id)

    meme_id = message.text.split()[1]
    if meme_id in MEMES:
        meme_price = MEMES[meme_id]["price"]
        if user_data["active_balance"] >= meme_price:
            user_data["active_balance"] -= meme_price
            purchased_memes = user_data["purchased_memes"]
            purchased_memes.append(meme_id)

            update_user(user_id, {
                "active_balance": user_data["active_balance"],
                "purchased_memes": purchased_memes
            })

            await bot.send_photo(
                message.chat.id,
                photo=MEMES[meme_id]["image_url"],
                caption=f"Вы успешно купили мем {meme_id} за {meme_price} монет!\n{MEMES[meme_id]['caption']}",
            )
            await bot.send_message(message.chat.id, "Спасибо за покупку! 😊")

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Выйти в меню"))
            await bot.send_message(message.chat.id, "Чтобы вернуться в главное меню, нажмите кнопку ниже.", reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, "Недостаточно средств на активном счете.")
    else:
        await bot.send_message(message.chat.id, "Такого мема нет в магазине.")

# Ежедневный бонус
async def daily_bonus():
    while True:
        all_users = get_all_users()
        for user in all_users:
            user_id = user["user_id"]
            user_data = get_or_create_user(user_id)

            if user_data["last_daily_bonus"] != str(asyncio.get_event_loop().time()):
                user_data["passive_balance"] += 100
                user_data["last_daily_bonus"] = str(asyncio.get_event_loop().time())

                update_user(user_id, {
                    "passive_balance": user_data["passive_balance"],
                    "last_daily_bonus": user_data["last_daily_bonus"]
                })

                await bot.send_message(user_id, "Вы получили регулярный подарок +100 монет на пассивный счет!")
        await asyncio.sleep(20)  # Каждые 20 секунд

# Запуск бота
async def main():
    await asyncio.gather(bot.infinity_polling(), daily_bonus())

if __name__ == "__main__":
    from database import create_users_table
    create_users_table()  # Создаем таблицу пользователей при запуске
    asyncio.run(main())