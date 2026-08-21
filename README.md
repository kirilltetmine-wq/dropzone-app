# Dropzone

Десктопное приложение для проведения розыгрышей и лотерей на стримах YouTube и Twitch.

## Возможности

- **Лотерея** — сбор участников по ключевому слову из чата, автоматический розыгрыш, чёрный/белый списки
- **Колесо фортуны** — настраиваемые секторы, анимация вращения, логи розыгрышей
- **Кейсы** — анимированное открытие кейсов с предметами
- **Интеграция с YouTube** — подключение к live-чату через YouTube Data API v3
- **Интеграция с Twitch** — подключение к Twitch-чату через IRC
- **Чат-виджет** — отображение сообщений, модерация, бейджи платформ
- **Кости** — встроенный виджет броска кубиков
- **Тёмная тема** — настраиваемый акцентный цвет, прозрачность окна
- **Обучение** — встроенный туториал при первом запуске

## Установка

### Исходный код

```bash
pip install -r requirements.txt
python main.py
```

### Скомпилированный .exe

```
dist/Dropzone.exe
```

## Настройка

### YouTube API

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите **YouTube Data API v3**
3. Создайте OAuth 2.0 Client ID (тип — Desktop application)
4. Скачайте `client_secret.json` и поместите в папку `data/`

### Twitch

1. Получите OAuth-токен на https://twitchtokengenerator.com/
2. Укажите Client ID и токен в настройках приложения

## Сборка .exe

```bash
python -m PyInstaller Dropzone.spec
```

Готовый файл появится в `dist/Dropzone.exe`.

## Структура проекта

```
├── main.py              # Точка входа
├── app/                 # Основная логика приложения
├── core/                # Конфигурация, тема, хранилище
├── gui/                 # Интерфейс (виджеты, диалоги, шаблоны)
├── ui_kit/              # Библиотека компонентов
├── services/            # Внешние сервисы (YouTube, Twitch)
├── data/                # Данные и client_secret.json
├── resources/           # Иконки, шрифты, изображения
└── requirements.txt     # Зависимости
```

## Зависимости

- PyQt6 — GUI-фреймворк
- requests — HTTP-запросы
- google-api-python-client — YouTube Data API
- google-auth-oauthlib — Google OAuth 2.0