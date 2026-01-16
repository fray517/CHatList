"""Скрипт для создания инсталлятора ChatList."""

import os
import sys
import shutil
from pathlib import Path

# Импорт версии
sys.path.insert(0, os.path.dirname(__file__))
from version import __version__

def find_inno_setup():
    """Поиск Inno Setup Compiler."""
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def update_setup_iss(version, exe_name):
    """Обновление setup.iss с актуальной версией."""
    iss_path = "setup.iss"
    if not os.path.exists(iss_path):
        print(f"Ошибка: файл {iss_path} не найден!")
        return False
    
    with open(iss_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Замена версии
    import re
    content = re.sub(
        r'(#define MyAppVersion ")[^"]+(")',
        f'\\g<1>{version}\\g<2>',
        content
    )
    content = re.sub(
        r'(#define MyAppExeName ")[^"]+(")',
        f'\\g<1>{exe_name}\\g<2>',
        content
    )
    
    with open(iss_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Основная функция."""
    print("Создание инсталлятора ChatList...")
    print()
    
    # Получение версии
    version = __version__
    print(f"Версия приложения: {version}")
    
    # Проверка наличия исполняемого файла
    exe_name = f"CHatList-{version}.exe"
    exe_path = os.path.join("dist", exe_name)
    
    if not os.path.exists(exe_path):
        exe_path = os.path.join("dist", "CHatList.exe")
        if not os.path.exists(exe_path):
            print("Ошибка: Исполняемый файл не найден в dist/")
            print(f"Ожидаемые файлы:")
            print(f"  - dist/CHatList-{version}.exe")
            print(f"  - dist/CHatList.exe")
            print("Сначала выполните сборку: .\\build.ps1")
            return 1
        
        exe_name = "CHatList.exe"
        print(f"Используется файл: {exe_name} (без версии в имени)")
    else:
        print(f"Найден файл: {exe_name}")
    
    # Обновление setup.iss
    print("Обновление setup.iss...")
    if not update_setup_iss(version, exe_name):
        return 1
    
    # Поиск Inno Setup
    print("Поиск Inno Setup...")
    iscc_path = find_inno_setup()
    
    if not iscc_path:
        print()
        print("Ошибка: Inno Setup не найден!")
        print("Установите Inno Setup 6 из https://jrsoftware.org/isdl.php")
        print("Или укажите путь к ISCC.exe вручную")
        print()
        print("После установки Inno Setup запустите скрипт снова.")
        return 1
    
    print(f"Найден Inno Setup: {iscc_path}")
    
    # Создание папки installer
    installer_dir = "installer"
    if not os.path.exists(installer_dir):
        os.makedirs(installer_dir)
    
    # Компиляция инсталлятора
    print("Компиляция инсталлятора...")
    import subprocess
    
    try:
        result = subprocess.run(
            [iscc_path, "setup.iss"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print()
            print("Инсталлятор успешно создан!")
            installer_path = os.path.join(
                installer_dir,
                f"CHatList-Setup-{version}.exe"
            )
            print(f"Файл находится в: {installer_path}")
            return 0
        else:
            print()
            print("Ошибка при создании инсталлятора!")
            if result.stdout:
                print("Вывод:")
                print(result.stdout)
            if result.stderr:
                print("Ошибки:")
                print(result.stderr)
            return 1
    
    except Exception as e:
        print(f"Ошибка при запуске Inno Setup: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
