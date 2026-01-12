# Схема базы данных ChatList

## Общая информация

База данных использует SQLite и состоит из четырёх основных таблиц:
- `prompts` - хранение промтов (запросов)
- `models` - хранение информации о нейросетях
- `results` - хранение сохранённых результатов
- `settings` - хранение настроек приложения

## Таблица: prompts

Хранит промты (запросы), которые пользователь отправляет в нейросети.

### Структура

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор промта |
| `date` | TEXT | NOT NULL | Дата создания промта (ISO формат: YYYY-MM-DD HH:MM:SS) |
| `prompt` | TEXT | NOT NULL | Текст промта |
| `tags` | TEXT | NULL | Теги промта (JSON массив или строка, разделённая запятыми) |

### Индексы

- `idx_prompts_date` на поле `date` (для сортировки и поиска по дате)
- `idx_prompts_tags` на поле `tags` (для поиска по тегам)

### Пример данных

```sql
INSERT INTO prompts (date, prompt, tags) VALUES 
('2024-01-15 10:30:00', 'Объясни квантовую физику простыми словами', '["наука", "физика"]'),
('2024-01-15 11:00:00', 'Напиши код на Python для сортировки списка', '["программирование", "python"]');
```

## Таблица: models

Хранит информацию о нейросетях (моделях), к которым можно отправлять запросы.

### Структура

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор модели |
| `name` | TEXT | NOT NULL UNIQUE | Название модели (например, "GPT-4", "DeepSeek Chat") |
| `api_url` | TEXT | NOT NULL | URL API для отправки запросов |
| `api_key_env` | TEXT | NOT NULL | Имя переменной окружения, где хранится API-ключ (например, "OPENAI_API_KEY") |
| `is_active` | INTEGER | NOT NULL DEFAULT 1 | Флаг активности (1 - активна, 0 - неактивна) |
| `model_type` | TEXT | NOT NULL | Тип провайдера API (openai, deepseek, groq и т.д.) |
| `model_name` | TEXT | NULL | Имя конкретной модели в API (например, "gpt-4", "deepseek-chat") |

### Индексы

- `idx_models_is_active` на поле `is_active` (для быстрого получения активных моделей)
- `idx_models_type` на поле `model_type` (для фильтрации по типу)

### Пример данных

```sql
INSERT INTO models (name, api_url, api_key_env, is_active, model_type, model_name) VALUES 
('GPT-4', 'https://api.openai.com/v1/chat/completions', 'OPENAI_API_KEY', 1, 'openai', 'gpt-4'),
('DeepSeek Chat', 'https://api.deepseek.com/v1/chat/completions', 'DEEPSEEK_API_KEY', 1, 'deepseek', 'deepseek-chat'),
('Groq Llama', 'https://api.groq.com/openai/v1/chat/completions', 'GROQ_API_KEY', 0, 'groq', 'llama-3-70b');
```

### Примечания

- API-ключи хранятся в файле `.env`, а не в базе данных
- Поле `api_key_env` содержит имя переменной окружения, из которой нужно брать ключ
- Поле `model_name` может отличаться от `name` (например, в API используется "gpt-4", а пользователю показывается "GPT-4")

## Таблица: results

Хранит сохранённые результаты ответов нейросетей.

### Структура

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор результата |
| `prompt_id` | INTEGER | NOT NULL | Ссылка на промт (FK к prompts.id) |
| `model_id` | INTEGER | NOT NULL | Ссылка на модель (FK к models.id) |
| `response_text` | TEXT | NOT NULL | Текст ответа от нейросети |
| `created_at` | TEXT | NOT NULL | Дата и время создания результата (ISO формат) |
| `tokens_used` | INTEGER | NULL | Количество использованных токенов (если доступно) |
| `response_time` | REAL | NULL | Время ответа в секундах |

### Индексы

- `idx_results_prompt_id` на поле `prompt_id` (для поиска результатов по промту)
- `idx_results_model_id` на поле `model_id` (для поиска результатов по модели)
- `idx_results_created_at` на поле `created_at` (для сортировки по дате)

### Внешние ключи

- `prompt_id` → `prompts(id)` ON DELETE CASCADE
- `model_id` → `models(id)` ON DELETE RESTRICT

### Пример данных

```sql
INSERT INTO results (prompt_id, model_id, response_text, created_at, tokens_used, response_time) VALUES 
(1, 1, 'Квантовая физика изучает поведение частиц на атомном уровне...', '2024-01-15 10:31:00', 150, 2.3),
(1, 2, 'Квантовая механика - это раздел физики, который описывает...', '2024-01-15 10:31:05', 180, 1.8);
```

## Таблица: settings

Хранит настройки приложения в формате ключ-значение.

### Структура

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `key` | TEXT | PRIMARY KEY | Ключ настройки |
| `value` | TEXT | NOT NULL | Значение настройки (может быть JSON) |

### Пример данных

```sql
INSERT INTO settings (key, value) VALUES 
('default_timeout', '30'),
('max_results_per_prompt', '10'),
('auto_save_prompts', 'true'),
('theme', 'light'),
('language', 'ru');
```

## Связи между таблицами

```
prompts (1) ──< (N) results
models  (1) ──< (N) results
```

- Один промт может иметь множество результатов (от разных моделей)
- Одна модель может иметь множество результатов (для разных промтов)
- Результат всегда связан с одним промтом и одной моделью

## SQL скрипт создания базы данных

```sql
-- Таблица промтов
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    prompt TEXT NOT NULL,
    tags TEXT
);

CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date);
CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags);

-- Таблица моделей
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_url TEXT NOT NULL,
    api_key_env TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    model_type TEXT NOT NULL,
    model_name TEXT
);

CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active);
CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type);

-- Таблица результатов
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
);

CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id);
CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id);
CREATE INDEX IF NOT EXISTS idx_results_created_at ON results(created_at);

-- Таблица настроек
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

## Запросы для работы с данными

### Получить все активные модели

```sql
SELECT * FROM models WHERE is_active = 1 ORDER BY name;
```

### Получить результаты для конкретного промта

```sql
SELECT r.*, m.name as model_name, p.prompt 
FROM results r
JOIN models m ON r.model_id = m.id
JOIN prompts p ON r.prompt_id = p.id
WHERE r.prompt_id = ?
ORDER BY r.created_at;
```

### Поиск промтов по тегам

```sql
SELECT * FROM prompts 
WHERE tags LIKE '%?%' 
ORDER BY date DESC;
```

### Получить статистику по моделям

```sql
SELECT m.name, COUNT(r.id) as result_count, AVG(r.response_time) as avg_time
FROM models m
LEFT JOIN results r ON m.id = r.model_id
GROUP BY m.id
ORDER BY result_count DESC;
```
