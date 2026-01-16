# Быстрый старт: Публикация релиза

## Шаг 1: Подготовка

1. Обновите версию в `version.py`:
   ```python
   __version__ = '1.0.0'  # Увеличьте версию
   ```

2. Соберите исполняемый файл:
   ```powershell
   .\build.ps1
   ```

3. Создайте инсталлятор:
   ```powershell
   python create_installer.py
   ```

## Шаг 2: Замените плейсхолдеры

Замените `ваш-username` на ваш GitHub username в следующих файлах:

- `docs/index.html` (4 места)
- `release-template.md` (2 места)
- `README.md` (2 места)

**Быстрая замена через PowerShell:**
```powershell
$username = "ваш-username"  # Замените на ваш username
Get-ChildItem -Recurse -Include *.html,*.md | ForEach-Object {
    (Get-Content $_.FullName) -replace 'ваш-username', $username | Set-Content $_.FullName
}
```

## Шаг 3: Создайте Git тег

```powershell
git add .
git commit -m "Подготовка к релизу v1.0.0"
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main
git push origin v1.0.0
```

## Шаг 4: Создайте GitHub Release

1. Перейдите на https://github.com/ваш-username/CHatList/releases
2. Нажмите **"Draft a new release"**
3. Выберите тег `v1.0.0`
4. Заполните:
   - **Title**: `ChatList v1.0.0`
   - **Description**: Скопируйте из `release-template.md`
5. Загрузите файлы:
   - `installer\CHatList-Setup-1.0.0.exe`
   - `dist\CHatList-1.0.0.exe` (опционально)
6. Нажмите **"Publish release"**

## Шаг 5: Настройте GitHub Pages

1. Перейдите в **Settings** → **Pages**
2. Выберите:
   - **Source**: `main` branch
   - **Folder**: `/docs`
3. Нажмите **Save**
4. Через несколько минут сайт будет доступен:
   `https://ваш-username.github.io/CHatList/`

## Готово! 🎉

Теперь у вас есть:
- ✅ GitHub Release с файлами для скачивания
- ✅ Лендинг на GitHub Pages
- ✅ Автоматизация через GitHub Actions (при следующем релизе)

## Что дальше?

- Обновите `release-template.md` для следующего релиза
- Добавьте скриншоты в `docs/index.html`
- Настройте автоматизацию в `.github/workflows/`

Подробные инструкции см. в [RELEASE.md](RELEASE.md) и [GITHUB_SETUP.md](GITHUB_SETUP.md).
