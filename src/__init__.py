"""Пакет ChatList - приложение для сравнения ответов нейросетей."""

import os
import importlib.util

# Импорт версии из корневого файла
_version_path = os.path.join(os.path.dirname(__file__), '..', 'version.py')
if os.path.exists(_version_path):
    spec = importlib.util.spec_from_file_location('version', _version_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    __version__ = version_module.__version__
else:
    __version__ = '1.0.0'  # Fallback
