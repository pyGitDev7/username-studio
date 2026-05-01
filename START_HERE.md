# START HERE

## Web interface

Обычный запуск теперь открывает локальный веб-интерфейс:

```powershell
python main.py
```

Если нужен старый консольный режим:

```powershell
python main.py --cli
```

Веб-интерфейс также можно запустить напрямую:

```powershell
python web_app.py
```

Короткая инструкция для актуальной версии генератора Telegram username.

## Главное

- Обычные username Telegram в проекте: **5-6 символов**, только **`[a-z]`**.
- Безопасный просмотр без Telegram-действий:
  ```powershell
  python main.py --no-telegram --dry-run
  ```
- Статистика без входа в меню:
  ```powershell
  python main.py --no-telegram --dry-run --stats
  ```
- Рабочий запуск:
  ```powershell
  python main.py
  ```

Telegram теперь подключается **только когда вы выбираете live-проверку через аккаунты из `sessions/` или создание канала через основной аккаунт из `.env`**. Просто открыть меню можно безопасно.

Для live-проверок нужно добавить Telegram-аккаунты на вкладке **Аккаунты**. Проверка автоматически переключается между ними при FloodWait/RPCError и показывает текущий активный номер на вкладке **Telegram**. Основной аккаунт из `.env` в проверках не участвует и нужен только для создания канала.

## Первый запуск

1. Откройте PowerShell в папке проекта:
   ```powershell
   cd "C:\path\to\telegram-username-generator"
   ```

2. Активируйте окружение:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Если окружение ещё не готово:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Запустите LM Studio OpenAI-compatible API:
   ```text
   http://localhost:1234/v1
   ```

5. Проверьте `.env` для основного аккаунта создания каналов:
   ```env
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_PHONE=
   LM_STUDIO_URL=http://127.0.0.1:1234/v1
   LM_STUDIO_MODEL=local-model
TELEGRAM_DRY_RUN=0
   ```

6. Для live-проверок откройте вкладку **Аккаунты**, нажмите **+ Добавить**, введите `API ID`, `API HASH`, телефон, код из Telegram и 2FA-пароль, если он включен.

## Меню

```text
1. Генерировать и оценить батч
2. Проверить доступность на Telegram
3. Создать канал для username
4. Статистика и просмотр базы
5. Переключить dry-run
6. Аккаунты Telegram
7. Выход
```

### Рекомендуемый порядок

1. `1` - сгенерировать и оценить батч.
2. `4` - посмотреть топы/статистику/доступные username.
3. `2` - проверить доступность через аккаунты из `sessions/`. Система сначала берёт свежий батч, если его нет - лучшие unchecked из базы.
4. Создание канала происходит через основной аккаунт из `.env` только после подтверждения:
   ```text
   Использовать <username> (score: X)? (y/n)
   ```

## Статистика и база

Пункт `4` открывает подменю:

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

Пункт **2. Доступные username** показывает только username, которые:

- имеют статус `available`;
- ещё не `used`;
- проходят текущий фильтр `5-6` символов и `[a-z]`;
- не являются служебными словами.

## Безопасность

- Не удаляйте `username_database.db`.
- Не удаляйте `telegram_session.session`.
- Не делайте массовые Telegram-проверки без понимания лимита.
- Аккаунт со статусом `cooldown` временно пропускается, `dead` требует повторного входа.
- Для просмотра используйте:
  ```powershell
  python main.py --no-telegram --dry-run
  ```
- Логи лежат тут:
  ```text
  logs/logs.txt
  ```

## Если что-то не работает

Показать последние логи:

```powershell
Get-Content logs\logs.txt -Tail 100
```

Проверить быстрый безопасный запуск:

```powershell
python main.py --no-telegram --dry-run --stats
```
