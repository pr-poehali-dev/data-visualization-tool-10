import json
import os
import requests
from datetime import datetime

TMDB_BASE = 'https://api.themoviedb.org/3'

def tmdb_get(path: str, params: dict) -> dict:
    params['language'] = 'ru-RU'
    resp = requests.get(
        f"{TMDB_BASE}{path}",
        params=params,
        headers={
            'Authorization': f"Bearer {os.environ['TMDB_API_KEY']}",
            'Accept': 'application/json'
        },
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()

def handler(event: dict, context) -> dict:
    """Возвращает список новинок кино, сериалов и мультфильмов через TMDB."""

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

    today = datetime.now().strftime('%Y-%m-%d')
    year = datetime.now().year
    date_from = f"{year}-01-01"

    films_data = tmdb_get('/discover/movie', {
        'sort_by': 'popularity.desc',
        'primary_release_date.gte': date_from,
        'primary_release_date.lte': today,
        'without_genres': '16',
        'page': '1'
    })

    cartoons_data = tmdb_get('/discover/movie', {
        'sort_by': 'popularity.desc',
        'primary_release_date.gte': date_from,
        'primary_release_date.lte': today,
        'with_genres': '16',
        'page': '1'
    })

    series_data = tmdb_get('/discover/tv', {
        'sort_by': 'popularity.desc',
        'first_air_date.gte': date_from,
        'first_air_date.lte': today,
        'page': '1'
    })

    def map_movie(m, type_):
        genres_map = {
            28: 'Экшн', 12: 'Приключения', 16: 'Мультфильм', 35: 'Комедия',
            80: 'Криминал', 99: 'Документальный', 18: 'Драма', 10751: 'Семейный',
            14: 'Фэнтези', 36: 'История', 27: 'Ужасы', 10402: 'Музыка',
            9648: 'Детектив', 10749: 'Романтика', 878: 'Фантастика',
            10770: 'ТВ-фильм', 53: 'Триллер', 10752: 'Война', 37: 'Вестерн'
        }
        genre_ids = m.get('genre_ids', [])
        genre = genres_map.get(genre_ids[0], 'Кино') if genre_ids else 'Кино'
        rating = m.get('vote_average', 0)
        return {
            'title': m.get('title') or m.get('name', ''),
            'original_title': m.get('original_title') or m.get('original_name', ''),
            'type': type_,
            'year': (m.get('release_date') or m.get('first_air_date') or '')[:4],
            'genre': genre,
            'description': m.get('overview') or 'Описание отсутствует.',
            'rating': f"{rating}/10" if rating else 'нет оценки',
            'poster': f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get('poster_path') else None
        }

    def map_series(s):
        genres_map = {
            10759: 'Экшн', 16: 'Мультфильм', 35: 'Комедия', 80: 'Криминал',
            99: 'Документальный', 18: 'Драма', 10751: 'Семейный', 10762: 'Детский',
            9648: 'Детектив', 10763: 'Новости', 10764: 'Реалити', 878: 'Фантастика',
            10765: 'Фантастика', 10766: 'Мыльная опера', 10767: 'Ток-шоу', 10768: 'Война'
        }
        genre_ids = s.get('genre_ids', [])
        genre = genres_map.get(genre_ids[0], 'Сериал') if genre_ids else 'Сериал'
        rating = s.get('vote_average', 0)
        return {
            'title': s.get('name', ''),
            'original_title': s.get('original_name', ''),
            'type': 'series',
            'year': (s.get('first_air_date') or '')[:4],
            'genre': genre,
            'description': s.get('overview') or 'Описание отсутствует.',
            'rating': f"{rating}/10" if rating else 'нет оценки',
            'poster': f"https://image.tmdb.org/t/p/w500{s['poster_path']}" if s.get('poster_path') else None
        }

    films = [map_movie(m, 'film') for m in films_data.get('results', [])[:3]]
    cartoons = [map_movie(m, 'cartoon') for m in cartoons_data.get('results', [])[:3]]
    series = [map_series(s) for s in series_data.get('results', [])[:3]]

    items = films + series + cartoons

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({'items': items}, ensure_ascii=False)
    }