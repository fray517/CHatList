"""Модуль для экспорта результатов."""

import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from PyQt5.QtWidgets import QFileDialog, QMessageBox


def export_to_markdown(
    results: List[Dict[str, Any]],
    prompt_text: str,
    parent=None
) -> bool:
    """Экспортировать результаты в Markdown формат."""
    filename, _ = QFileDialog.getSaveFileName(
        parent,
        'Сохранить как Markdown',
        f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
        'Markdown Files (*.md);;All Files (*)'
    )

    if not filename:
        return False

    try:
        content = f"# Результаты сравнения моделей\n\n"
        content += f"**Промт:** {prompt_text}\n\n"
        content += f"**Дата экспорта:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "---\n\n"

        for i, result in enumerate(results, 1):
            model_name = result.get('model_name', 'Неизвестная модель')
            response_text = result.get('response_text', '')
            created_at = result.get('created_at', '')

            content += f"## {i}. {model_name}\n\n"
            if created_at:
                content += f"*Дата: {created_at}*\n\n"
            content += f"{response_text}\n\n"
            content += "---\n\n"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        QMessageBox.information(
            parent,
            'Успех',
            f'Результаты экспортированы в:\n{filename}'
        )
        return True

    except Exception as e:
        QMessageBox.critical(
            parent,
            'Ошибка',
            f'Ошибка при экспорте:\n{str(e)}'
        )
        return False


def export_to_json(
    results: List[Dict[str, Any]],
    prompt_text: str,
    parent=None
) -> bool:
    """Экспортировать результаты в JSON формат."""
    filename, _ = QFileDialog.getSaveFileName(
        parent,
        'Сохранить как JSON',
        f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
        'JSON Files (*.json);;All Files (*)'
    )

    if not filename:
        return False

    try:
        data = {
            'prompt': prompt_text,
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        QMessageBox.information(
            parent,
            'Успех',
            f'Результаты экспортированы в:\n{filename}'
        )
        return True

    except Exception as e:
        QMessageBox.critical(
            parent,
            'Ошибка',
            f'Ошибка при экспорте:\n{str(e)}'
        )
        return False
