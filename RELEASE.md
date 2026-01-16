# Инструкция по публикации релиза ChatList

## Подготовка к релизу

### 1. Обновление версии

Перед созданием релиза обновите версию в файле `version.py`:

```python
__version__ = '1.0.0'  # Увеличьте версию (например, 1.0.1, 1.1.0, 2.0.0)
```

### 2. Сборка исполняемого файла

```powershell
.\build.ps1
```

Проверьте, что файл создан: `dist\CHatList-{version}.exe`

### 3. Создание инсталлятора

```powershell
python create_installer.py
```

Проверьте, что инсталлятор создан: `installer\CHatList-Setup-{version}.exe`

### 4. Подготовка релиз-нот

Создайте файл `RELEASE_NOTES.md` с описанием изменений или используйте шаблон из `release-template.md`.

## Публикация на GitHub Release

### Способ 1: Через веб-интерфейс GitHub

1. Перейдите на страницу репозитория: `https://github.com/ваш-username/CHatList`

2. Нажмите на **"Releases"** в правой части страницы

3. Нажмите **"Draft a new release"** или **"Create a new release"**

4. Заполните форму:
   - **Tag version**: `v1.0.0` (используйте формат `v{version}`)
   - **Release title**: `ChatList v1.0.0` или краткое описание
   - **Description**: Скопируйте содержимое из `release-template.md` или `RELEASE_NOTES.md`
   - Отметьте **"Set as the latest release"** (если это последний релиз)

5. Загрузите файлы:
   - Перетащите `installer\CHatList-Setup-{version}.exe` в область "Attach binaries"
   - Опционально: `dist\CHatList-{version}.exe` (портативная версия)

6. Нажмите **"Publish release"**

### Способ 2: Через GitHub CLI

```powershell
# Установите GitHub CLI, если еще не установлен
# https://cli.github.com/

# Авторизация
gh auth login

# Создание релиза
gh release create v1.0.0 `
  --title "ChatList v1.0.0" `
  --notes-file release-template.md `
  installer\CHatList-Setup-1.0.0.exe `
  dist\CHatList-1.0.0.exe
```

### Способ 3: Через GitHub Actions (автоматизация)

См. файл `.github/workflows/release.yml` для автоматической публикации при создании тега.

## Публикация на GitHub Pages

### Способ 1: Через веб-интерфейс

1. Перейдите в **Settings** → **Pages** вашего репозитория

2. В разделе **Source** выберите:
   - **Branch**: `gh-pages` (или `main`)
   - **Folder**: `/docs` (или `/root`)

3. Нажмите **Save**

4. Скопируйте файл `index.html` в папку `docs/` (если выбрали `/docs`) или в корень (если выбрали `/root`)

5. Закоммитьте и запушьте изменения:
   ```powershell
   git add docs/index.html
   git commit -m "Добавлен лендинг для GitHub Pages"
   git push
   ```

6. Через несколько минут сайт будет доступен по адресу:
   `https://ваш-username.github.io/CHatList/`

### Способ 2: Через GitHub Actions

См. файл `.github/workflows/pages.yml` для автоматической публикации.

## Структура файлов для релиза

```
CHatList/
├── dist/
│   └── CHatList-1.0.0.exe          # Портативная версия
├── installer/
│   └── CHatList-Setup-1.0.0.exe   # Инсталлятор
├── docs/
│   └── index.html                  # Лендинг для GitHub Pages
├── release-template.md             # Шаблон релиз-нот
└── RELEASE_NOTES.md                # Текущие релиз-ноты
```

## Чеклист перед релизом

- [ ] Версия обновлена в `version.py`
- [ ] Исполняемый файл собран и протестирован
- [ ] Инсталлятор создан и протестирован
- [ ] Релиз-ноты подготовлены
- [ ] README.md обновлен (если нужно)
- [ ] CHANGELOG.md обновлен (если используется)
- [ ] Теги созданы в Git: `git tag v1.0.0`
- [ ] Теги запушены: `git push origin v1.0.0`
- [ ] GitHub Release создан
- [ ] GitHub Pages обновлен (если нужно)

## Создание Git тега

```powershell
# Создание тега
git tag -a v1.0.0 -m "Release version 1.0.0"

# Отправка тега на GitHub
git push origin v1.0.0

# Или отправить все теги
git push origin --tags
```

## Удаление тега (если нужно)

```powershell
# Удаление локального тега
git tag -d v1.0.0

# Удаление тега на GitHub
git push origin :refs/tags/v1.0.0
```
