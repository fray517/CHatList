"""Модуль для работы с моделями нейросетей."""

import os
from typing import Optional, List, Dict, Any, Tuple

from dotenv import load_dotenv

from src import db


# Загружаем переменные окружения
load_dotenv()


class Model:
    """Класс для представления модели нейросети."""

    def __init__(
        self,
        id: int,
        name: str,
        api_url: str,
        api_key_env: str,
        is_active: int,
        model_type: str,
        model_name: Optional[str] = None
    ):
        """Инициализация модели."""
        self.id = id
        self.name = name
        self.api_url = api_url
        self.api_key_env = api_key_env
        self.is_active = is_active
        self.model_type = model_type
        self.model_name = model_name or name.lower().replace(' ', '-')

    def get_api_key(self) -> Optional[str]:
        """Получить API-ключ из переменной окружения."""
        return os.getenv(self.api_key_env)

    def validate(self) -> tuple[bool, Optional[str]]:
        """Проверить корректность данных модели."""
        if not self.name:
            return False, 'Название модели не может быть пустым'

        if not self.api_url:
            return False, 'URL API не может быть пустым'

        if not self.api_key_env:
            return False, 'Имя переменной окружения для API-ключа не может быть пустым'

        if not self.get_api_key():
            return False, f'API-ключ не найден в переменной окружения {self.api_key_env}'

        if not self.model_type:
            return False, 'Тип модели не может быть пустым'

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать модель в словарь."""
        return {
            'id': self.id,
            'name': self.name,
            'api_url': self.api_url,
            'api_key_env': self.api_key_env,
            'is_active': self.is_active,
            'model_type': self.model_type,
            'model_name': self.model_name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """Создать модель из словаря."""
        return cls(
            id=data['id'],
            name=data['name'],
            api_url=data['api_url'],
            api_key_env=data['api_key_env'],
            is_active=data['is_active'],
            model_type=data['model_type'],
            model_name=data.get('model_name')
        )


def load_models() -> List[Model]:
    """Загрузить все модели из базы данных."""
    models_data = db.get_models()
    return [Model.from_dict(m) for m in models_data]


def get_active_models() -> List[Model]:
    """Получить список активных моделей."""
    models_data = db.get_active_models()
    return [Model.from_dict(m) for m in models_data]


def add_default_models() -> None:
    """Добавить модели по умолчанию в базу данных."""
    default_models = [
        {
            'name': 'qwen/qwen3-coder:free',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_key_env': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'model_name': 'qwen/qwen3-coder:free',
            'is_active': 1
        },
        {
            'name': 'deepseek/deepseek-r1-0528:free',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_key_env': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'model_name': 'deepseek/deepseek-r1-0528:free',
            'is_active': 1
        },
        {
            'name': 'mistralai/devstral-2512:free',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_key_env': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'model_name': 'mistralai/devstral-2512:free',
            'is_active': 1
        },
        {
            'name': 'allenai/molmo-2-8b:free',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_key_env': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'model_name': 'allenai/molmo-2-8b:free',
            'is_active': 1
        }
    ]

    existing_models = db.get_models()
    existing_names = {m['name'] for m in existing_models}

    for model_data in default_models:
        if model_data['name'] not in existing_names:
            db.create_model(
                name=model_data['name'],
                api_url=model_data['api_url'],
                api_key_env=model_data['api_key_env'],
                model_type=model_data['model_type'],
                model_name=model_data['model_name'],
                is_active=model_data['is_active']
            )
