from telebot.types import KeyboardButton, ReplyKeyboardMarkup

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(
    KeyboardButton("💰 Баланс"),
    KeyboardButton("📋 Задания"),
    KeyboardButton("🔄 Перевод"),
    KeyboardButton("🏆 Рейтинг"),
    KeyboardButton("🛒 Магазин"),
    KeyboardButton("📜 История")
)

admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(
    KeyboardButton("💰 Баланс"),
    KeyboardButton("📋 Задания"),
    KeyboardButton("🔄 Перевод"),
    KeyboardButton("🏆 Рейтинг"),
    KeyboardButton("🛒 Магазин"),
    KeyboardButton("📜 История"),
    KeyboardButton("😡 Выдать штраф"),
    KeyboardButton("⏱️ Сменить время бонуса")
)
