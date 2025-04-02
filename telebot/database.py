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
    cursor = conn.cursor()
    return cursor.execute('''SELECT * FROM users WHERE username=?''', (user_link.strip('@'),)).fetchone()



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


def do_transfer(conn, user, recipient, amount):
    cur = conn.cursor()
    print(user, recipient, amount)
    cur.execute("""UPDATE users SET passive_balance=? WHERE user_id=?""", (user[3] - amount, user[0]))
    cur.execute("""UPDATE users SET active_balance=? WHERE user_id=?""", (recipient[2] + amount, recipient[0]))
    conn.commit()


def get_top_users(conn, limit=5):
    """Получаем топ пользователей по активному балансу"""
    cursor = conn.cursor()
    cursor.execute('SELECT username, active_balance FROM users ORDER BY active_balance DESC LIMIT ?', (limit,))
    return cursor.fetchall()
