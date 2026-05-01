# Summary

## Текущее состояние

Проект стабилизирован под генерацию коротких обычных Telegram username:

```text
5-6 символов
только [a-z]
без служебных слов LLM
```

## Что умеет

- Генерировать username трёх типов:
  - `brandable`;
  - `russian_transliteration`;
  - `multilingual`.
- Парсить сложные ответы LM Studio:
  - markdown;
  - лишний текст;
  - несколько JSON-блоков;
  - частично грязный JSON;
  - Python-like структуры.
- Оценивать username через LLM или fallback.
- Хранить оценки, проверки, доступность, использованные username и батчи в SQLite.
- Показывать расширенную статистику и списки базы.
- Безопасно запускаться без Telegram через dry-run.
- Проверять Telegram только после выбора соответствующего пункта меню.

## Главное меню

```text
1. Генерировать и оценить батч
2. Проверить доступность на Telegram
3. Создать канал для username
4. Статистика и просмотр базы
5. Переключить dry-run
6. Выход
```

## Просмотр базы

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

`Доступные username` показывает только валидные username, которые можно использовать:

- `available`;
- не `used`;
- текущий формат `5-6 [a-z]`.

## Команды

```powershell
python main.py
python main.py --no-telegram --dry-run
python main.py --no-telegram --dry-run --stats
```

## Изменённые ключевые файлы

- `main.py`
- `storage.py`
- `llm_generator.py`
- `llm_evaluator.py`
- `telegram_client.py`
- `utils.py`
- `config.py`
- документация `.md`

## База

Основная база:

```text
username_database.db
```

Не удалять:

```text
username_database.db
telegram_session.session
telegram_session.session-journal
```

## Проверки, которые должны проходить

```powershell
python main.py --no-telegram --dry-run --stats
```

Также проект проверялся на:

- синтаксис всех `.py`;
- импорты;
- dry-run запуск;
- парсинг LLM-ответов;
- фильтрацию username;
- storage-запросы.

## Актуализировано

2026-04-30.
