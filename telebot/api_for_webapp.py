from fastapi import FastAPI
from database import *

app = FastAPI()
init_db()


@app.post("/api/update_balance")
def update_balance_for_current_user(user_id: int, amount: int):
    conn = create_connection()
    user = get_user(conn, user_id)
    if user:
        update_balance(conn, user_id, active_balance=user[2] + amount)
    else:
        print(f'User {user_id} not found.')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
