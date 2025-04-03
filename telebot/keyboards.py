from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(
    KeyboardButton("💰 Баланс"),
    KeyboardButton("🎮 Игры"),
    KeyboardButton("🔄 Перевод"),
    KeyboardButton("🏆 Рейтинг"),
    KeyboardButton("🛒 Магазин"),
    KeyboardButton("📜 История"),
    KeyboardButton("Help🆘")
)

admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(
    KeyboardButton("💰 Баланс"),
    KeyboardButton("🎮 Игры"),
    KeyboardButton("🔄 Перевод"),
    KeyboardButton("🏆 Рейтинг"),
    KeyboardButton("🛒 Магазин"),
    KeyboardButton("📜 История"),
    KeyboardButton("Help🆘"),
    KeyboardButton("😡 Выдать штраф"),
    KeyboardButton("⏱️ Сменить время бонуса")
)
admin_keyboard.add(KeyboardButton("📥 Новый администратор"))
admin_keyboard.add(KeyboardButton("🗿 Пользователи"))


cancel_keyboard = InlineKeyboardMarkup(row_width=1)
cancel_keyboard.add(InlineKeyboardButton('Отмена', callback_data='cancel'))
