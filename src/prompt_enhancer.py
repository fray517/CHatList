"""Модуль для улучшения промтов с помощью AI."""

import json
import logging
from typing import Dict, Any, List, Optional

from src.models import Model
from src.network import send_prompt_to_model


logger = logging.getLogger(__name__)


# Промпты-шаблоны для разных типов улучшения
ENHANCE_PROMPT_TEMPLATE = """Ты - эксперт по созданию эффективных промптов для AI-моделей.

Исходный промпт пользователя:
{prompt}

Задача:
1. Улучши этот промпт, сделав его более четким, конкретным и эффективным.
2. Сохрани основную идею и цель промпта.
3. Добавь необходимый контекст, если его не хватает.
4. Улучши структуру и читаемость.

Верни ТОЛЬКО улучшенную версию промпта, без дополнительных комментариев."""

ALTERNATIVES_PROMPT_TEMPLATE = """Ты - эксперт по созданию эффективных промптов для AI-моделей.

Исходный промпт пользователя:
{prompt}

Задача:
Создай 3 альтернативных варианта переформулировки этого промпта. Каждый вариант должен:
- Сохранять основную цель и смысл
- Использовать разные формулировки и подходы
- Быть эффективным для получения хороших результатов от AI

Верни результат в формате JSON:
{{
  "alternatives": [
    "Вариант 1",
    "Вариант 2",
    "Вариант 3"
  ]
}}"""

ADAPT_CODE_PROMPT_TEMPLATE = """Ты - эксперт по созданию промптов для программирования и работы с кодом.

Исходный промпт пользователя:
{prompt}

Задача:
Адаптируй этот промпт специально для задач программирования и работы с кодом. Добавь:
- Конкретные требования к формату кода
- Указания на язык программирования (если применимо)
- Требования к стилю и документации
- Примеры использования (если нужно)

Верни ТОЛЬКО адаптированную версию промпта, без дополнительных комментариев."""

ADAPT_ANALYSIS_PROMPT_TEMPLATE = """Ты - эксперт по созданию промптов для аналитических задач.

Исходный промпт пользователя:
{prompt}

Задача:
Адаптируй этот промпт специально для аналитических задач. Добавь:
- Требования к структуре анализа
- Указания на формат вывода (списки, таблицы, выводы)
- Требования к глубине анализа
- Критерии оценки (если применимо)

Верни ТОЛЬКО адаптированную версию промпта, без дополнительных комментариев."""

ADAPT_CREATIVE_PROMPT_TEMPLATE = """Ты - эксперт по созданию промптов для креативных задач.

Исходный промпт пользователя:
{prompt}

Задача:
Адаптируй этот промпт специально для креативных задач (написание текстов, генерация идей, творчество). Добавь:
- Требования к стилю и тону
- Указания на жанр или формат (если применимо)
- Требования к оригинальности и креативности
- Дополнительные вдохновляющие элементы

Верни ТОЛЬКО адаптированную версию промпта, без дополнительных комментариев."""


def enhance_prompt(prompt: str, model: Model) -> Dict[str, Any]:
    """Улучшить промт с помощью AI."""
    try:
        enhanced_prompt_text = ENHANCE_PROMPT_TEMPLATE.format(prompt=prompt)
        result = send_prompt_to_model(enhanced_prompt_text, model)

        if result['success']:
            enhanced_prompt = result.get('response_text', '').strip()
            return {
                'success': True,
                'enhanced_prompt': enhanced_prompt,
                'original_prompt': prompt
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Неизвестная ошибка')
            }

    except Exception as e:
        logger.error(f'Ошибка при улучшении промта: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def generate_alternatives(prompt: str, model: Model) -> Dict[str, Any]:
    """Сгенерировать альтернативные варианты промта."""
    try:
        alternatives_prompt_text = ALTERNATIVES_PROMPT_TEMPLATE.format(
            prompt=prompt
        )
        result = send_prompt_to_model(alternatives_prompt_text, model)

        if result['success']:
            response_text = result.get('response_text', '').strip()

            # Парсинг JSON ответа
            try:
                # Пытаемся найти JSON в ответе
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    parsed = json.loads(json_text)
                    alternatives = parsed.get('alternatives', [])

                    # Если получили меньше 3 вариантов, дополняем
                    while len(alternatives) < 3:
                        alternatives.append('')

                    return {
                        'success': True,
                        'alternatives': alternatives[:3]
                    }
                else:
                    # Если JSON не найден, пытаемся извлечь варианты из текста
                    lines = [
                        line.strip()
                        for line in response_text.split('\n')
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    alternatives = [line for line in lines if line][:3]

                    # Дополняем до 3 вариантов
                    while len(alternatives) < 3:
                        alternatives.append('')

                    return {
                        'success': True,
                        'alternatives': alternatives[:3]
                    }

            except json.JSONDecodeError:
                # Если не удалось распарсить JSON, извлекаем варианты из текста
                lines = [
                    line.strip()
                    for line in response_text.split('\n')
                    if line.strip() and not line.strip().startswith('#')
                ]
                alternatives = [line for line in lines if line][:3]

                while len(alternatives) < 3:
                    alternatives.append('')

                return {
                    'success': True,
                    'alternatives': alternatives[:3]
                }

        else:
            return {
                'success': False,
                'error': result.get('error', 'Неизвестная ошибка')
            }

    except Exception as e:
        logger.error(f'Ошибка при генерации альтернатив: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def adapt_prompt_for_type(
    prompt: str,
    model_type: str,
    model: Model
) -> Dict[str, Any]:
    """Адаптировать промт под определенный тип задачи."""
    templates = {
        'code': ADAPT_CODE_PROMPT_TEMPLATE,
        'analysis': ADAPT_ANALYSIS_PROMPT_TEMPLATE,
        'creative': ADAPT_CREATIVE_PROMPT_TEMPLATE
    }

    template = templates.get(model_type.lower())
    if not template:
        return {
            'success': False,
            'error': f'Неизвестный тип адаптации: {model_type}'
        }

    try:
        adapted_prompt_text = template.format(prompt=prompt)
        result = send_prompt_to_model(adapted_prompt_text, model)

        if result['success']:
            adapted_prompt = result.get('response_text', '').strip()
            return {
                'success': True,
                'adapted_prompt': adapted_prompt,
                'type': model_type
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Неизвестная ошибка')
            }

    except Exception as e:
        logger.error(f'Ошибка при адаптации промта: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def enhance_prompt_full(
    prompt: str,
    model: Model,
    include_alternatives: bool = True,
    include_adaptations: bool = True
) -> Dict[str, Any]:
    """Полное улучшение промта со всеми вариантами."""
    results = {
        'original_prompt': prompt,
        'enhanced_prompt': None,
        'alternatives': [],
        'adaptations': {}
    }

    # Улучшение основного промта
    enhance_result = enhance_prompt(prompt, model)
    if enhance_result['success']:
        results['enhanced_prompt'] = enhance_result['enhanced_prompt']
    else:
        results['error'] = enhance_result.get('error', 'Ошибка улучшения')

    # Генерация альтернатив
    if include_alternatives:
        alternatives_result = generate_alternatives(prompt, model)
        if alternatives_result['success']:
            results['alternatives'] = alternatives_result['alternatives']
        else:
            if 'error' not in results:
                results['error'] = alternatives_result.get('error')

    # Адаптация под разные типы
    if include_adaptations:
        for adapt_type in ['code', 'analysis', 'creative']:
            adapt_result = adapt_prompt_for_type(prompt, adapt_type, model)
            if adapt_result['success']:
                results['adaptations'][adapt_type] = adapt_result[
                    'adapted_prompt'
                ]
            else:
                results['adaptations'][adapt_type] = None

    return results
