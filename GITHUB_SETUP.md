# Настройка GitHub для ChatList

## Быстрая настройка

### 1. Замените плейсхолдеры

В следующих файлах замените `ваш-username` на ваш GitHub username:

- `docs/index.html` - в ссылках на релизы и репозиторий
- `release-template.md` - в ссылках на релизы
- `README.md` - в бейджах и ссылках
- `.github/workflows/release.yml` - если нужно настроить автоматизацию

### 2. Настройка GitHub Pages

1. Перейдите в **Settings** → **Pages** вашего репозитория
2. В разделе **Source** выберите:
   - **Branch**: `main` (или `gh-pages`)
   - **Folder**: `/docs`
3. Нажмите **Save**
4. Через несколько минут сайт будет доступен по адресу:
   `https://ваш-username.github.io/CHatList/`

### 3. Создание первого релиза

1. Обновите версию в `version.py`
2. Соберите исполняемый файл: `.\build.ps1`
3. Создайте инсталлятор: `python create_installer.py`
4. Создайте Git тег:
   ```powershell
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```
5. Перейдите на страницу **Releases** в GitHub
6. Нажмите **Draft a new release**
7. Выберите тег `v1.0.0`
8. Заполните описание (используйте `release-template.md`)
9. Загрузите файлы:
   - `installer\CHatList-Setup-1.0.0.exe`
   - `dist\CHatList-1.0.0.exe` (опционально)
10. Нажмите **Publish release**

## Автоматизация через GitHub Actions

### Настройка автоматического релиза

1. Убедитесь, что файл `.github/workflows/release.yml` существует
2. При создании тега (например, `v1.0.0`) GitHub Actions автоматически:
   - Соберет исполняемый файл
   - Создаст релиз
   - Загрузит файлы

**Примечание**: Для создания инсталлятора в CI нужен Inno Setup, что может быть сложно настроить. Рекомендуется создавать инсталлятор локально и загружать вручную.

### Настройка автоматической публикации GitHub Pages

1. Убедитесь, что файл `.github/workflows/pages.yml` существует
2. При изменении файлов в папке `docs/` GitHub Actions автоматически обновит сайт

## Структура файлов

```
CHatList/
├── .github/
│   └── workflows/
│       ├── release.yml      # Автоматическое создание релиза
│       └── pages.yml        # Автоматическая публикация GitHub Pages
├── docs/
│   └── index.html          # Лендинг для GitHub Pages
├── release-template.md     # Шаблон для релиз-нот
├── RELEASE.md              # Инструкция по публикации
└── GITHUB_SETUP.md         # Этот файл
```

## Полезные ссылки

- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [GitHub Pages](https://docs.github.com/en/pages)
- [GitHub Actions](https://docs.github.com/en/actions)
