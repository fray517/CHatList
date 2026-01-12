"""Модуль для работы с базой данных SQLite."""

import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple


DB_PATH = 'chatlist.db'


def get_connection() -> sqlite3.Connection:
    """Получить соединение с базой данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Инициализация базы данных - создание всех таблиц и индексов."""
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица промтов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            prompt TEXT NOT NULL,
            tags TEXT
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags)
    ''')

    # Таблица моделей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            api_url TEXT NOT NULL,
            api_key_env TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            model_type TEXT NOT NULL,
            model_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type)
    ''')

    # Таблица результатов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER NOT NULL,
            model_id INTEGER NOT NULL,
            response_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            tokens_used INTEGER,
            response_time REAL,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
            FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE RESTRICT
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_results_created_at ON results(created_at)
    ''')

    # Таблица настроек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# ========== CRUD операции для prompts ==========

def create_prompt(prompt: str, tags: Optional[str] = None) -> int:
    """Создать новый промт."""
    conn = get_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if tags and isinstance(tags, list):
        tags = json.dumps(tags, ensure_ascii=False)

    cursor.execute(
        'INSERT INTO prompts (date, prompt, tags) VALUES (?, ?, ?)',
        (date, prompt, tags)
    )
    prompt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prompt_id


def get_prompts(
    limit: Optional[int] = None,
    order_by: str = 'date DESC'
) -> List[Dict[str, Any]]:
    """Получить список промтов."""
    conn = get_connection()
    cursor = conn.cursor()

    query = f'SELECT * FROM prompts ORDER BY {order_by}'
    if limit:
        query += f' LIMIT {limit}'

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_prompt_by_id(prompt_id: int) -> Optional[Dict[str, Any]]:
    """Получить промт по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM prompts WHERE id = ?', (prompt_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def update_prompt(
    prompt_id: int,
    prompt: Optional[str] = None,
    tags: Optional[str] = None
) -> bool:
    """Обновить промт."""
    conn = get_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if prompt is not None:
        updates.append('prompt = ?')
        params.append(prompt)

    if tags is not None:
        if isinstance(tags, list):
            tags = json.dumps(tags, ensure_ascii=False)
        updates.append('tags = ?')
        params.append(tags)

    if not updates:
        conn.close()
        return False

    params.append(prompt_id)
    query = f'UPDATE prompts SET {", ".join(updates)} WHERE id = ?'
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def delete_prompt(prompt_id: int) -> bool:
    """Удалить промт."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ========== CRUD операции для models ==========

def create_model(
    name: str,
    api_url: str,
    api_key_env: str,
    model_type: str,
    model_name: Optional[str] = None,
    is_active: int = 1
) -> int:
    """Создать новую модель."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''INSERT INTO models (name, api_url, api_key_env, is_active, 
           model_type, model_name) VALUES (?, ?, ?, ?, ?, ?)''',
        (name, api_url, api_key_env, is_active, model_type, model_name)
    )
    model_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return model_id


def get_models(active_only: bool = False) -> List[Dict[str, Any]]:
    """Получить список моделей."""
    conn = get_connection()
    cursor = conn.cursor()

    if active_only:
        cursor.execute(
            'SELECT * FROM models WHERE is_active = 1 ORDER BY name'
        )
    else:
        cursor.execute('SELECT * FROM models ORDER BY name')

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_active_models() -> List[Dict[str, Any]]:
    """Получить список активных моделей."""
    return get_models(active_only=True)


def update_model(
    model_id: int,
    name: Optional[str] = None,
    api_url: Optional[str] = None,
    api_key_env: Optional[str] = None,
    model_type: Optional[str] = None,
    model_name: Optional[str] = None,
    is_active: Optional[int] = None
) -> bool:
    """Обновить модель."""
    conn = get_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if name is not None:
        updates.append('name = ?')
        params.append(name)

    if api_url is not None:
        updates.append('api_url = ?')
        params.append(api_url)

    if api_key_env is not None:
        updates.append('api_key_env = ?')
        params.append(api_key_env)

    if model_type is not None:
        updates.append('model_type = ?')
        params.append(model_type)

    if model_name is not None:
        updates.append('model_name = ?')
        params.append(model_name)

    if is_active is not None:
        updates.append('is_active = ?')
        params.append(is_active)

    if not updates:
        conn.close()
        return False

    params.append(model_id)
    query = f'UPDATE models SET {", ".join(updates)} WHERE id = ?'
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def toggle_model_active(model_id: int) -> bool:
    """Переключить активность модели."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE models SET is_active = NOT is_active WHERE id = ?',
        (model_id,)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


# ========== CRUD операции для results ==========

def save_results(results: List[Dict[str, Any]]) -> None:
    """Сохранить список результатов."""
    conn = get_connection()
    cursor = conn.cursor()

    for result in results:
        cursor.execute(
            '''INSERT INTO results (prompt_id, model_id, response_text, 
               created_at, tokens_used, response_time) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                result['prompt_id'],
                result['model_id'],
                result['response_text'],
                result.get('created_at', datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S'
                )),
                result.get('tokens_used'),
                result.get('response_time')
            )
        )

    conn.commit()
    conn.close()


def get_results(
    prompt_id: Optional[int] = None,
    model_id: Optional[int] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Получить список результатов."""
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if prompt_id is not None:
        conditions.append('prompt_id = ?')
        params.append(prompt_id)

    if model_id is not None:
        conditions.append('model_id = ?')
        params.append(model_id)

    query = 'SELECT * FROM results'
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    query += ' ORDER BY created_at DESC'

    if limit:
        query += f' LIMIT {limit}'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_results_by_prompt(prompt_id: int) -> List[Dict[str, Any]]:
    """Получить результаты для конкретного промта."""
    return get_results(prompt_id=prompt_id)


# ========== CRUD операции для settings ==========

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Получить значение настройки."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()

    return row['value'] if row else default


def set_setting(key: str, value: str) -> None:
    """Установить значение настройки."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
        (key, value)
    )
    conn.commit()
    conn.close()


# ========== Поиск и сортировка ==========

def search_prompts(
    query: str,
    search_in_tags: bool = True
) -> List[Dict[str, Any]]:
    """Поиск промтов по тексту и тегам."""
    conn = get_connection()
    cursor = conn.cursor()

    search_term = f'%{query}%'
    conditions = ['prompt LIKE ?']
    params = [search_term]

    if search_in_tags:
        conditions.append('tags LIKE ?')
        params.append(search_term)

    sql = f'''
        SELECT * FROM prompts 
        WHERE {' OR '.join(conditions)}
        ORDER BY date DESC
    '''

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def search_results(query: str) -> List[Dict[str, Any]]:
    """Поиск результатов по тексту ответа."""
    conn = get_connection()
    cursor = conn.cursor()

    search_term = f'%{query}%'
    cursor.execute(
        'SELECT * FROM results WHERE response_text LIKE ? ORDER BY created_at DESC',
        (search_term,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
