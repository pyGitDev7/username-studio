# Быстрый старт и примеры автоматизации

## Самые полезные команды

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

В web-интерфейсе можно открыть вкладку **Аккаунты** и добавить несколько Telegram-аккаунтов. Live-проверки используют только ротацию аккаунтов из `sessions/`; основной аккаунт из `.env` нужен только для создания каналов.

Без Telegram:

```powershell
python main.py --no-telegram --dry-run
```

Только статистика:

```powershell
python main.py --no-telegram --dry-run --stats
```

## Пример 1. Генерация и оценка без Telegram

Создайте `generate_only.py`:

```python
from main import UsernameGenerationSystem


def main():
    system = UsernameGenerationSystem(dry_run=True, no_telegram=True)
    batch = system.generate_batch(50)
    evaluated = system.evaluate_batch(batch["usernames"])

    for index, item in enumerate(evaluated[:20], 1):
        print(index, item["username"], round(item["total_score"], 2), item.get("generation_type"))


if __name__ == "__main__":
    main()
```

Запуск:

```powershell
python generate_only.py
```

## Пример 2. Посмотреть доступные username из базы

Создайте `show_available.py`:

```python
from storage import UsernameStorage


storage = UsernameStorage()
rows = storage.get_username_records(
    limit=50,
    status="available",
    valid_only=True,
)

for row in rows:
    print(row["username"], row.get("score"), row.get("checked_at"))
```

`valid_only=True` важен: он показывает только username, которые проходят текущий формат `5-6 [a-z]`.

## Пример 3. Preview кандидатов для Telegram-проверки

Создайте `preview_check_candidates.py`:

```python
import config
from storage import UsernameStorage


storage = UsernameStorage()
rows = storage.get_username_records(
    limit=30,
    min_score=config.SCORE_THRESHOLD,
    status="unchecked",
    valid_only=True,
)

for row in rows:
    print(row["username"], round(row["score"], 2), row.get("generation_type"))
```

Этот скрипт ничего не отправляет в Telegram.

## Пример 4. Автоматическая генерация, затем dry-run preview

```python
from main import UsernameGenerationSystem


system = UsernameGenerationSystem(dry_run=True, no_telegram=True)
batch = system.generate_batch(100)
evaluated = system.evaluate_batch(batch["usernames"])

print("Top:")
for row in evaluated[:10]:
    print(row["username"], round(row["total_score"], 2))
```

## Пример 5. Реальная проверка через код

Используйте осторожно. Скрипт делает Telegram-запросы.

```python
import asyncio
import config
from main import UsernameGenerationSystem


async def main():
    system = UsernameGenerationSystem(dry_run=False, no_telegram=False)
    try:
        candidates = system.storage.get_username_records(
            limit=5,
            min_score=config.SCORE_THRESHOLD,
            status="unchecked",
            valid_only=True,
        )
        results = await system.check_availability_batch(candidates)
        print(results)
    finally:
        await system.close_telegram()


if __name__ == "__main__":
    asyncio.run(main())
```

## Таблица команд

| Команда | Что делает | Telegram |
|---|---|---|
| `python main.py` | Полное меню | Только при пунктах 2/3 |
| `python main.py --no-telegram --dry-run` | Безопасный preview | Нет |
| `python main.py --no-telegram --dry-run --stats` | Статистика | Нет |
| `python generate_only.py` | Генерация/оценка | Нет |
| `python show_available.py` | Доступные валидные username | Нет |

## Мульти-аккаунты

1. Запустите `python main.py`.
2. Откройте вкладку **Аккаунты**.
3. Нажмите **+ Добавить**.
4. Введите `API ID`, `API HASH`, телефон, код из Telegram и 2FA-пароль, если он включен.
5. Аккаунт со статусом `active` сразу участвует в live-проверках. Основной аккаунт на вкладке **Telegram** в проверках не участвует и используется для создания каналов.

## Логи

```powershell
Get-Content logs\logs.txt -Tail 100
```
