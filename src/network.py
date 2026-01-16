"""Модуль для отправки сетевых запросов к API нейросетей."""

import json
import logging
import os
import sys
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import requests

from src.models import Model

# Импорт версии
_version_path = os.path.join(os.path.dirname(__file__), '..', 'version.py')
if os.path.exists(_version_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('version', _version_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    __version__ = version_module.__version__
else:
    __version__ = '1.0.0'  # Fallback


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s - ChatList v{__version__} - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class BaseAPIProvider(ABC):
    """Базовый класс для провайдеров API."""

    def __init__(self, model: Model, timeout: int = DEFAULT_TIMEOUT):
        """Инициализация провайдера."""
        self.model = model
        self.timeout = timeout

    @abstractmethod
    def send_request(self, prompt: str) -> Dict[str, Any]:
        """Отправить запрос к API."""
        pass

    def _make_request(
        self,
        url: str,
        headers: Dict[str, str],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнить HTTP-запрос с обработкой ошибок."""
        try:
            start_time = time.time()
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response_time = time.time() - start_time

            response.raise_for_status()
            result = response.json()

            logger.info(
                f'Запрос к {self.model.name} выполнен за {response_time:.2f}с'
            )

            return {
                'success': True,
                'data': result,
                'response_time': response_time
            }

        except requests.exceptions.Timeout:
            logger.error(f'Таймаут при запросе к {self.model.name}')
            return {
                'success': False,
                'error': 'Превышено время ожидания ответа'
            }

        except requests.exceptions.RequestException as e:
            logger.error(f'Ошибка при запросе к {self.model.name}: {e}')
            return {
                'success': False,
                'error': str(e)
            }

        except Exception as e:
            logger.error(f'Неожиданная ошибка при запросе к {self.model.name}: {e}')
            return {
                'success': False,
                'error': f'Неожиданная ошибка: {str(e)}'
            }


class OpenAIProvider(BaseAPIProvider):
    """Провайдер для OpenAI API."""

    def send_request(self, prompt: str) -> Dict[str, Any]:
        """Отправить запрос к OpenAI API."""
        api_key = self.model.get_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'API-ключ не найден'
            }

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model.model_name,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7
        }

        result = self._make_request(self.model.api_url, headers, data)

        if result['success']:
            try:
                response_text = result['data']['choices'][0]['message']['content']
                tokens_used = result['data'].get('usage', {}).get('total_tokens')
                result['response_text'] = response_text
                result['tokens_used'] = tokens_used
            except (KeyError, IndexError) as e:
                logger.error(f'Ошибка парсинга ответа OpenAI: {e}')
                result['success'] = False
                result['error'] = 'Неверный формат ответа от API'

        return result


class DeepSeekProvider(BaseAPIProvider):
    """Провайдер для DeepSeek API."""

    def send_request(self, prompt: str) -> Dict[str, Any]:
        """Отправить запрос к DeepSeek API."""
        api_key = self.model.get_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'API-ключ не найден'
            }

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model.model_name,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7
        }

        result = self._make_request(self.model.api_url, headers, data)

        if result['success']:
            try:
                response_text = result['data']['choices'][0]['message']['content']
                tokens_used = result['data'].get('usage', {}).get('total_tokens')
                result['response_text'] = response_text
                result['tokens_used'] = tokens_used
            except (KeyError, IndexError) as e:
                logger.error(f'Ошибка парсинга ответа DeepSeek: {e}')
                result['success'] = False
                result['error'] = 'Неверный формат ответа от API'

        return result


class GroqProvider(BaseAPIProvider):
    """Провайдер для Groq API."""

    def send_request(self, prompt: str) -> Dict[str, Any]:
        """Отправить запрос к Groq API."""
        api_key = self.model.get_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'API-ключ не найден'
            }

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model.model_name,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7
        }

        result = self._make_request(self.model.api_url, headers, data)

        if result['success']:
            try:
                response_text = result['data']['choices'][0]['message']['content']
                tokens_used = result['data'].get('usage', {}).get('total_tokens')
                result['response_text'] = response_text
                result['tokens_used'] = tokens_used
            except (KeyError, IndexError) as e:
                logger.error(f'Ошибка парсинга ответа Groq: {e}')
                result['success'] = False
                result['error'] = 'Неверный формат ответа от API'

        return result


class OpenRouterProvider(BaseAPIProvider):
    """Провайдер для OpenRouter API."""

    def send_request(self, prompt: str) -> Dict[str, Any]:
        """Отправить запрос к OpenRouter API."""
        api_key = self.model.get_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'API-ключ не найден'
            }

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com',  # Опционально, для отслеживания
            'X-Title': 'ChatList'  # Опционально, название приложения
        }

        data = {
            'model': self.model.model_name,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7
        }

        result = self._make_request(self.model.api_url, headers, data)

        if result['success']:
            try:
                response_text = result['data']['choices'][0]['message']['content']
                tokens_used = result['data'].get('usage', {}).get('total_tokens')
                result['response_text'] = response_text
                result['tokens_used'] = tokens_used
            except (KeyError, IndexError) as e:
                logger.error(f'Ошибка парсинга ответа OpenRouter: {e}')
                result['success'] = False
                result['error'] = 'Неверный формат ответа от API'

        return result


def get_provider(model_type: str, model: Model) -> BaseAPIProvider:
    """Фабрика для создания провайдера по типу модели."""
    providers = {
        'openai': OpenAIProvider,
        'deepseek': DeepSeekProvider,
        'groq': GroqProvider,
        'openrouter': OpenRouterProvider,
        'qwen': OpenRouterProvider,  # Все модели через OpenRouter
        'llama': OpenRouterProvider,
        'mistral': OpenRouterProvider
    }

    provider_class = providers.get(model_type.lower())
    if not provider_class:
        # По умолчанию используем OpenRouter для неизвестных типов
        logger.warning(
            f'Неизвестный тип провайдера: {model_type}, '
            'используется OpenRouter'
        )
        provider_class = OpenRouterProvider

    return provider_class(model)


def send_prompt_to_model(prompt: str, model: Model) -> Dict[str, Any]:
    """Отправить промт к модели и получить ответ."""
    try:
        provider = get_provider(model.model_type, model)
        result = provider.send_request(prompt)

        if result['success']:
            logger.info(f'Успешный ответ от {model.name}')
        else:
            logger.warning(f'Ошибка от {model.name}: {result.get("error")}')

        return result

    except Exception as e:
        logger.error(f'Ошибка при отправке запроса к {model.name}: {e}')
        return {
            'success': False,
            'error': str(e)
        }
