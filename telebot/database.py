import sqlite3
from sqlite3 import Error

def create_connection():
    """Создаём подключение к SQLite базе данных"""
    conn = None
    try:
        conn = sqlite3.connect('bot_database.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Создаём таблицы, если их нет"""
    try:
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            active_balance INTEGER DEFAULT 0,
            passive_balance INTEGER DEFAULT 0
        )
        ''')

        # Таблица покупок
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT,
            product_price INTEGER,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')

        conn.commit()
    except Error as e:
        print(e)

def init_db():
    """Инициализация базы данных"""
    conn = create_connection()
    if conn:
        create_tables(conn)
        conn.close()

def get_user(conn, user_id):
    """Получаем данные пользователя"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def get_user_from_link(conn, user_link):
    """Получаем пользователя по username (ссылке)"""
    cursor = conn.cursor()
    return cursor.execute('SELECT * FROM users WHERE username=?', (user_link.strip('@'),)).fetchone()

def add_user(conn, user_id, username):
    """Добавляем нового пользователя"""
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
    ''', (user_id, username))
    conn.commit()

def update_balance(conn, user_id, active_balance=None, passive_balance=None):
    """Обновляем баланс пользователя"""
    cursor = conn.cursor()
    if active_balance is not None:
        cursor.execute('UPDATE users SET active_balance = ? WHERE user_id = ?', (active_balance, user_id))
    if passive_balance is not None:
        cursor.execute('UPDATE users SET passive_balance = ? WHERE user_id = ?', (passive_balance, user_id))
    conn.commit()

def do_transfer(conn, sender, recipient, amount):
    """Выполняем перевод средств между пользователями"""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET passive_balance=? WHERE user_id=?", (sender[3] - amount, sender[0]))
    cursor.execute("UPDATE users SET active_balance=? WHERE user_id=?", (recipient[2] + amount, recipient[0]))
    conn.commit()

def get_top_users(conn, limit=5):
    """Получаем топ пользователей по активному балансу"""
    cursor = conn.cursor()
    cursor.execute('SELECT username, active_balance FROM users ORDER BY active_balance DESC LIMIT ?', (limit,))
    return cursor.fetchall()

def add_purchase(conn, user_id, product_name, product_price):
    """Добавляем запись о покупке"""
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO purchases (user_id, product_name, product_price)
    VALUES (?, ?, ?)
    ''', (user_id, product_name, product_price))
    conn.commit()

def get_purchase_history(conn, user_id, limit=5):
    """Получаем историю покупок пользователя"""
    cursor = conn.cursor()
    cursor.execute('''
    SELECT product_name, product_price, purchase_date 
    FROM purchases 
    WHERE user_id = ?
    ORDER BY purchase_date DESC
    LIMIT ?
    ''', (user_id, limit))
    return cursor.fetchall()