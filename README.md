# Telegram Username Generator

Python-проект для генерации, оценки, фильтрации, проверки и учёта коротких Telegram username.

## Возможности

- Генерация username через LM Studio OpenAI-compatible API.
- Три типа генерации:
  - `brandable`;
  - `russian_transliteration`;
  - `multilingual`.
- Строгий текущий формат username: **5-6 символов**, только **`[a-z]`**.
- Устойчивый парсинг ответов LLM:
  - markdown;
  - лишний текст;
  - несколько JSON-блоков;
  - Python-like JSON;
  - частично грязные ответы.
- Fallback-генератор без LLM.
- LLM-оценка и fallback-оценка по критериям:
  - readability;
  - brandability;
  - meaning;
  - rarity.
- SQLite-хранилище статусов, оценок, батчей и использованных username.
- Безопасный `dry-run`/preview режим.
- Ленивое подключение Telegram: при старте меню Telegram не трогается.
- Подробная статистика и просмотр базы.

## Быстрый запуск

```powershell
cd "C:\path\to\telegram-username-generator"
.\venv\Scripts\Activate.ps1
python main.py
```

Без Telegram-действий:

```powershell
python main.py --no-telegram --dry-run
```

Только статистика:

```powershell
python main.py --no-telegram --dry-run --stats
```

## Установка

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Заполните `.env`:

```env
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_PHONE=

LM_STUDIO_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=local-model
LLM_TEMPERATURE=0.95
LLM_MAX_TOKENS=2000

TELEGRAM_DRY_RUN=0
```

## LM Studio

1. Установите LM Studio.
2. Загрузите модель.
3. Запустите OpenAI-compatible server.
4. URL по умолчанию:
   ```text
   http://localhost:1234/v1
   ```

Если LM Studio недоступен, генерация и оценка используют fallback-логику.

## Telegram

API-ключи берутся на https://my.telegram.org/.

Telegram-действия происходят только в пунктах:

- `2. Проверить доступность на Telegram`;
- `3. Создать канал для username`.

Перед созданием канала система:

- проверяет локальную валидность username;
- смотрит статус в базе;
- не создаёт канал, если username уже `used`, `invalid` или `checked_taken`;
- спрашивает подтверждение.

## Меню

```text
1. Генерировать и оценить батч
2. Проверить доступность на Telegram
3. Создать канал для username
4. Статистика и просмотр базы
5. Переключить dry-run
6. Выход
```

Проверка Telegram сначала использует свежий последний батч. Если свежего батча нет или там нечего проверять, берутся лучшие unchecked username из базы.

## Статистика и просмотр базы

Подменю `4`:

```text
1. Общая статистика
2. Доступные username
3. Уже проверенные username
4. Использованные username
5. Топ username по score
6. Username из последнего батча
7. Не проверялись в Telegram
8. Занятые/невалидные
9. Фильтрованный просмотр
0. Назад
```

Для каждой записи показывается:

- username;
- score;
- status;
- checked_at;
- scored_at;
- generation_type;
- channel_id/channel_name для `used`;
- notes.

`Доступные username` показывает только валидные и реально пригодные к использованию username со статусом `available`.

## Статусы

- `unchecked` - есть оценка/батч, но Telegram ещё не проверялся.
- `checked_taken` - Telegram показал, что username занят или недоступен.
- `available` - Telegram показал, что username доступен.
- `used` - username уже использован для канала.
- `invalid` - Telegram или локальный фильтр признал username невалидным.
- `error` - ошибка проверки, например после FloodWait retries.

## SQLite

Основные таблицы:

- `checked_usernames`;
- `used_usernames`;
- `scores`;
- `batches`;
- `batch_usernames`.

Миграции выполняются мягко: добавляются новые поля/таблицы без удаления старых данных.

## Логи

```text
logs/logs.txt
```

В Windows логгер настроен на UTF-8 и не должен падать с `UnicodeEncodeError`.

## Важные файлы

- `main.py` - CLI и основной workflow.
- `llm_generator.py` - генерация и парсинг LLM.
- `llm_evaluator.py` - оценка и парсинг LLM.
- `telegram_client.py` - Telegram API.
- `storage.py` - SQLite-запросы и статистика.
- `config.py` - настройки.
- `username_database.db` - база, не удалять.
- `telegram_session.session` - Telegram-сессия, не удалять.

## Версия

Актуализировано: 2026-04-30.

