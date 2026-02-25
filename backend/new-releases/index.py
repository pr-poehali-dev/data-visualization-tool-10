import json
import os
from openai import OpenAI
from datetime import datetime

def handler(event: dict, context) -> dict:
    """Возвращает список новинок кино, сериалов и мультфильмов через OpenAI."""

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }

    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    current_date = datetime.now().strftime("%B %Y")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты эксперт по кино. Отвечай ТОЛЬКО валидным JSON без markdown и лишнего текста. "
                    "Формат ответа: массив объектов с полями: "
                    "title (название на русском), "
                    "original_title (оригинальное название), "
                    "type (film/series/cartoon), "
                    "year (год выхода), "
                    "genre (жанр), "
                    "description (краткое описание 1-2 предложения на русском), "
                    "rating (рейтинг IMDb или ожидаемый, строка типа '8.2/10')"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Сейчас {current_date}. Дай список из 9 самых ожидаемых или недавно вышедших "
                    "новинок: 3 фильма, 3 сериала и 3 мультфильма. "
                    "Включай реальные тайтлы 2024-2025 года. Только JSON-массив."
                )
            }
        ],
        temperature=0.7,
        max_tokens=2000
    )

    content = response.choices[0].message.content.strip()
    items = json.loads(content)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({'items': items}, ensure_ascii=False)
    }
