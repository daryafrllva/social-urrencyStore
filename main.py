from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.0.38"],  # Укажите адрес фронтенда
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Явно разрешаем OPTIONS
    allow_headers=["*"],
    expose_headers=["*"]
)

# Конфигурация
ALLOWED_TOPICS = ['Животные','Наука','История', 'География', 'Искусство','Спорт']
PROHIBITED_TOPICS = ["политика", "насилие", "18+", "смерть"]

client = OpenAI(
    base_url="http://192.168.0.38:1234/v1",
    api_key="lm-studio"
)

class QuizRequest(BaseModel):
    category: str

@app.post("/api/generate-quiz")
async def generate_quiz(request: QuizRequest):
    try:
        # Проверка допустимости темы
        if request.category.lower() in PROHIBITED_TOPICS:
            raise HTTPException(status_code=400, detail="Запрещенная тема")

        prompt = f"""Ты - генератор викторинных вопросов. Строго следуй инструкциям:

Формат ВХОДА:
{{
  "topic": "{request.category}",
  "language": "ru"
}}

Формат ВЫХОДА (строго соблюдай):
{{
  "text": "текст вопроса",
  "options": ["вариант1", "вариант2", "вариант3", "вариант4"],
  "answer": "правильный вариант",
  "explanation": "объяснение"
}}

ПРАВИЛА:
1. Только 1 вопрос за запрос
2. Только указанные темы: {", ".join(ALLOWED_TOPICS)}
3. Запрещенные темы: {", ".join(PROHIBITED_TOPICS)}
4. Возвращай ТОЛЬКО JSON без комментариев

Пример правильного ответа:
{{
  "text": "Какое животное считается национальным символом Австралии?",
  "options": ["Кенгуру", "Коала", "Вомбат", "Ехидна"],
  "answer": "Кенгуру",
  "explanation": "Кенгуру изображен на гербе Австралии"
}}

ТЕПЕРЬ СОЗДАЙ ВОПРОС НА ТЕМУ: {request.category}"""  

        response = client.chat.completions.create(
            model="local-model",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Уменьшаем случайность
            max_tokens=500
        )

        content = response.choices[0].message.content
        
        # Извлекаем JSON из ответа
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        question = json.loads(content[json_start:json_end])

        # Валидация
        if not all(k in question for k in ["text", "options", "answer", "explanation"]):
            raise ValueError("Неполная структура вопроса")
            
        if len(question["options"]) != 4:
            raise ValueError("Должно быть 4 варианта ответа")

        return question

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка формата ответа")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))