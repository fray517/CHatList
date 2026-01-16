# Скрипт для создания инсталлятора с помощью Inno Setup

Write-Host "Создание инсталлятора ChatList..." -ForegroundColor Green

# Проверка наличия Inno Setup
$innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoSetupPath)) {
    $innoSetupPath = "C:\Program Files\Inno Setup 6\ISCC.exe"
}
if (-not (Test-Path $innoSetupPath)) {
    Write-Host "Ошибка: Inno Setup не найден!" -ForegroundColor Red
    Write-Host "Установите Inno Setup 6 из https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host "Или укажите путь к ISCC.exe в переменной `$innoSetupPath`" -ForegroundColor Yellow
    exit 1
}

# Получение версии из version.py
$version = "1.0.0"
$versionLines = Get-Content "version.py"
foreach ($line in $versionLines) {
    if ($line.Contains("__version__")) {
        $parts = $line.Split("=")
        if ($parts.Length -gt 1) {
            $versionPart = $parts[1].Trim()
            $version = $versionPart.Trim("'").Trim('"').Trim()
            break
        }
    }
}
Write-Host "Версия приложения: $version" -ForegroundColor Cyan

# Проверка наличия исполняемого файла
$exeName = "CHatList-$version.exe"
$exePath = "dist\$exeName"
if (-not (Test-Path $exePath)) {
    # Пробуем найти файл без версии
    $exePath = "dist\CHatList.exe"
    if (-not (Test-Path $exePath)) {
        Write-Host "Ошибка: Исполняемый файл не найден в dist\" -ForegroundColor Red
        Write-Host "Ожидаемые файлы:" -ForegroundColor Yellow
        Write-Host "  - dist\CHatList-$version.exe" -ForegroundColor Yellow
        Write-Host "  - dist\CHatList.exe" -ForegroundColor Yellow
        Write-Host "Сначала выполните сборку: .\build.ps1" -ForegroundColor Yellow
        exit 1
    }
    $exeName = "CHatList.exe"
    Write-Host "Используется файл: $exeName (без версии в имени)" -ForegroundColor Yellow
} else {
    Write-Host "Найден файл: $exeName" -ForegroundColor Green
}

# Обновление setup.iss с актуальной версией
Write-Host "Обновление setup.iss..." -ForegroundColor Yellow
$issContent = Get-Content "setup.iss" -Raw -Encoding UTF8

# Замена версии в setup.iss
$issContent = $issContent -replace '(#define MyAppVersion ")[^"]+(")', "`$1$version`$2"
$issContent = $issContent -replace '(#define MyAppExeName ")[^"]+(")', "`$1$exeName`$2"

# Создание папки installer, если её нет
if (-not (Test-Path "installer")) {
    New-Item -ItemType Directory -Path "installer" | Out-Null
}

# Сохранение обновленного setup.iss
$issContent | Set-Content "setup.iss" -Encoding UTF8

# Компиляция инсталлятора
Write-Host "Компиляция инсталлятора..." -ForegroundColor Yellow
& $innoSetupPath "setup.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Инсталлятор успешно создан!" -ForegroundColor Green
    $installerPath = "installer\CHatList-Setup-$version.exe"
    Write-Host "Файл находится в: $installerPath" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Ошибка при создании инсталлятора!" -ForegroundColor Red
    exit 1
}
