import json
import os
import urllib.request
from datetime import datetime

def handler(event: dict, context) -> dict:
    """Возвращает список новинок кино, сериалов и мультфильмов через OpenRouter."""

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

    current_date = datetime.now().strftime("%B %Y")

    payload = json.dumps({
        "model": "meta-llama/llama-3.3-70b-instruct",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты эксперт по кино. Отвечай ТОЛЬКО валидным JSON-массивом без markdown, "
                    "без ```json, без пояснений — только сырой JSON-массив. "
                    "Каждый объект имеет поля: "
                    "title (название на русском), "
                    "original_title (оригинальное название), "
                    "type (film/series/cartoon), "
                    "year (год выхода, число), "
                    "genre (жанр), "
                    "description (краткое описание 1-2 предложения на русском), "
                    "rating (строка, например '8.2/10' или 'ожидается')"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Сейчас {current_date}. Дай список из 9 реальных новинок 2024-2025 года: "
                    "3 фильма, 3 сериала и 3 мультфильма. Только JSON-массив, без лишнего текста."
                )
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://poehali.dev',
            'X-Title': 'poehali'
        },
        method='POST'
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))

    content = result['choices'][0]['message']['content'].strip()
    if content.startswith('```'):
        content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()

    items = json.loads(content)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({'items': items}, ensure_ascii=False)
    }