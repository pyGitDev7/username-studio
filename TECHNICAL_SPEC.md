# Техническое задание / актуальная спецификация

## Цель

Скрипт должен генерировать, оценивать, хранить и безопасно проверять короткие Telegram username, а также помогать использовать найденные доступные username для каналов.

## Username policy

Обычные username Telegram в проекте:

- длина `5-6`;
- только латинские буквы `a-z`;
- без цифр;
- без подчёркиваний;
- без спецсимволов;
- без служебных слов из LLM-ответов.

## Генерация

Система должна сохранять баланс:

```text
brandable: 40%
russian_transliteration: 30%
multilingual: 30%
```

Генератор обязан:

- обращаться к LM Studio OpenAI-compatible API;
- устойчиво парсить ответы модели;
- использовать fallback при ошибке LM Studio;
- добирать недостающие username fallback-генератором;
- возвращать только валидные username.

## Парсинг LLM

Парсеры должны поддерживать:

- чистый JSON;
- markdown blocks;
- лишний текст до/после JSON;
- несколько JSON-блоков;
- массивы;
- объекты с `username`, `usernames`, `results`, `scores`, `items`;
- Python-like JSON с одинарными кавычками;
- частично грязные блоки, если из них можно достать валидные элементы.

## Оценка

Критерии:

```text
readability: 30%
brandability: 30%
meaning: 20%
rarity: 20%
```

Итоговый score сортируется по убыванию.

Fallback-оценка не должна завышать мусорные username.

## Telegram

Telegram-действия должны быть безопасными:

- не подключаться при простом старте меню;
- поддерживать `--no-telegram`;
- поддерживать `--dry-run`;
- проверять сначала лучших кандидатов;
- не отправлять в Telegram невалидные username;
- не создавать канал, если username заранее `used`, `invalid` или `checked_taken`;
- перед созданием канала спрашивать:
  ```text
  Использовать <username> (score: X)? (y/n)
  ```

Обрабатываемые ошибки:

- `FloodWaitError`;
- `UsernameInvalidError`;
- `UsernameOccupiedError`;
- `UsernamePurchaseAvailableError`;
- другие `RPCError`.

## Storage

Все запросы просмотра базы должны идти через `storage.py`.

Таблицы:

- `checked_usernames`;
- `used_usernames`;
- `scores`;
- `batches`;
- `batch_usernames`.

Хранить:

- checked;
- available;
- used;
- invalid/taken status;
- scores;
- generation_type;
- batch_num;
- checked_at;
- scored_at;
- channel_id/channel_name;
- notes.

Миграции только мягкие: добавление таблиц/полей без удаления существующих данных.

## CLI

Основное меню:

```text
1. Генерировать и оценить батч
2. Проверить доступность на Telegram
3. Создать канал для username
4. Статистика и просмотр базы
5. Переключить dry-run
6. Выход
```

Подменю статистики:

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

Фильтры:

- top N;
- min score;
- only available;
- only unchecked;
- only used;
- only last batch.

## Web-интерфейс

- Команды запуска не изменились: `python web_app.py` или запуск через `main.py`.
- `web_app.py` является тонкой совместимой точкой входа.
- HTTP handler находится в `web/handlers.py`.
- API payload helpers находятся в `web/payloads.py`.
- Telegram auth логика находится в `web/telegram_auth.py`.
- Background task state находится в `web/tasks.py`.
- `INDEX_HTML` и шаблон dashboard находятся в `web/templates.py`.
- Пользовательское поведение и внешний вид web-интерфейса не должны отличаться от прежней версии.

## Логи

Логи:

```text
logs/logs.txt
```

Требования:

- UTF-8;
- без `UnicodeEncodeError` в Windows;
- важные действия логировать;
- нормальные fallback-доборы не засорять warning-ами.

## Запрещено без отдельного подтверждения

- удалять `username_database.db`;
- удалять `telegram_session.session`;
- делать массовые Telegram-проверки;
- делать опасные `git reset/delete`;
- создавать канал без явного подтверждения.
