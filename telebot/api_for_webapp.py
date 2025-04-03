from fastapi import FastAPI
from database import *

app = FastAPI()


@app.get('/users')
def get_users_all():
    conn = create_connection()
    return get_users(conn)


@app.get('/user/{user_id}')
def get_current_user(user_id: int):
    conn = create_connection()
    return get_user(conn, user_id)


@app.get('/user/{user_id}/balance')
def get_balance_from_user(user_id: int):
    conn = create_connection()
    return get_user(conn, user_id)[2]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)