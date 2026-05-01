# Структура проекта

Папка:

```text
C:\path\to\telegram-username-generator
```

## Основные модули

| Файл | Назначение |
|---|---|
| `main.py` | CLI, меню, workflow генерации/оценки/проверки/создания |
| `config.py` | Настройки Telegram, LM Studio, фильтров, score и лимитов |
| `llm_generator.py` | Генерация username и устойчивый парсинг LLM-ответов |
| `llm_evaluator.py` | Оценка username и восстановление оценок из грязного JSON |
| `telegram_client.py` | Telethon-клиент, проверка доступности, создание каналов |
| `username_filter.py` | Фильтрация username перед оценкой/проверкой |
| `storage.py` | SQLite-схема, миграции, статистика, запросы просмотра |
| `utils.py` | Нормализация, валидация, эвристики, fallback helpers |
| `logger.py` | Логи в консоль и `logs/logs.txt` |
| `web_app.py` | Тонкий launcher web-интерфейса. `python web_app.py` работает как раньше |
| `web/server.py` | Запуск `ThreadingHTTPServer`, host/port и browser heartbeat/shutdown |
| `web/handlers.py` | `UsernameDashboardHandler`, `do_GET`, `do_POST`, JSON/HTML helpers |
| `web/payloads.py` | API payload helpers, lazy storage/account manager, чистые helpers |
| `web/telegram_auth.py` | Telegram auth flow, `.env` config save/reset, guard-функции |
| `web/tasks.py` | Background task state и task runners |
| `web/templates.py` | `INDEX_HTML` для dashboard |

## Документация

| Файл | Назначение |
|---|---|
| `START_HERE.md` | Самый короткий вход в проект |
| `README.md` | Общее описание возможностей |
| `INSTRUCTIONS.md` | Подробная инструкция запуска |
| `QUICK_START.md` | Примеры автоматизации |
| `PROJECT_STRUCTURE.md` | Этот файл |
| `SUMMARY.md` | Краткое состояние проекта |
| `TECHNICAL_SPEC.md` | Текущее ТЗ/спецификация |

## Данные и локальные файлы

| Файл/папка | Назначение |
|---|---|
| `username_database.db` | SQLite-база. Не удалять |
| `telegram_session.session` | Telegram-сессия Telethon. Не удалять |
| `telegram_session.session-journal` | SQLite journal сессии. Не удалять вручную |
| `logs/logs.txt` | Логи |
| `.env` | Локальные секреты и настройки |
| `.env.example` | Шаблон настроек |
| `venv/` | Виртуальное окружение |

## Архитектура

```text
main.py
  в"њв"Ђ LLMUsernameGenerator
  в"'    в"њв"Ђ LM Studio API
  в"'    в""в"Ђ fallback generation
  в"њв"Ђ UsernameFilter
  в"'    в""в"Ђ strict 5-6 [a-z] validation
  в"њв"Ђ LLMUsernameEvaluator
  в"'    в"њв"Ђ LM Studio API
  в"'    в""в"Ђ fallback scoring
  в"њв"Ђ UsernameStorage
  в"'    в""в"Ђ SQLite
  в""в"Ђ TelegramChannelManager
       в""в"Ђ Telethon
```

Web-интерфейс запускается прежними командами `python main.py` или `python web_app.py`. Пользовательское поведение не менялось: `web_app.py` остался совместимой точкой входа, а реализация dashboard разнесена по модулям в `web/`.

## SQLite

### `checked_usernames`

Хранит результаты Telegram-проверки.

```text
id
username
available
score
generation_type
checked_at
notes
status
batch_num
```

### `used_usernames`

Хранит username, для которых создан канал.

```text
id
username
channel_id
channel_name
created_at
notes
```

### `scores`

Хранит последнюю оценку username.

```text
id
username
readability
brandability
meaning
rarity
total_score
scored_at
generation_type
batch_num
```

### `batches`

Хранит батчи.

```text
id
batch_num
total_usernames
available_count
generation_type
created_at
```

### `batch_usernames`

Хранит состав новых батчей.

```text
id
batch_num
username
generation_type
created_at
```

Примечание: старые батчи могли не иметь состава, поэтому `batch_usernames` заполняется для новых батчей после миграции.

## Статусы username

```text
unchecked
checked_taken
available
used
invalid
error
```

## Основной workflow

```text
1. Генерация
   brandable / russian_transliteration / multilingual

2. Парсинг LLM
   JSON, markdown, dirty JSON, fallback extraction

3. Фильтрация
   5-6 символов, только [a-z], blacklist, blocked service words

4. Оценка
   readability, brandability, meaning, rarity

5. Сохранение
   scores, batches, batch_usernames

6. Проверка Telegram
   только лучшие unchecked кандидаты, safe limits, FloodWait handling

7. Создание канала
   только после подтверждения пользователя
```

## CLI

```text
1. Генерировать и оценить батч
2. Проверить доступность на Telegram
3. Создать канал для username
4. Статистика и просмотр базы
5. Переключить dry-run
6. Выход
```

## Безопасность

- Telegram не подключается при простом старте меню.
- `--no-telegram --dry-run` полностью отключает Telegram-действия.
- Проверка кандидатов фильтрует старые невалидные записи.
- Создание канала блокируется для `used`, `invalid`, `checked_taken`.
- FloodWait обрабатывается с ограничением повторов.
