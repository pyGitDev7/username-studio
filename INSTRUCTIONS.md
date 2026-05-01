# Инструкция по запуску и работе

## 1. Подготовка

Откройте PowerShell:

```powershell
cd "C:\path\to\telegram-username-generator"
```

Активируйте окружение:

```powershell
.\venv\Scripts\Activate.ps1
```

Если окружения нет:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. LM Studio

1. Откройте LM Studio.
2. Загрузите модель.
3. Запустите OpenAI-compatible API server.
4. Проверьте URL:
   ```text
   http://localhost:1234/v1
   ```

Р' `.env`:

```env
LM_STUDIO_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=local-model
LLM_TEMPERATURE=0.95
LLM_MAX_TOKENS=2000
```

Если LM Studio недоступен, скрипт использует fallback-генерацию и fallback-оценку.

## 3. Telegram API

1. Откройте https://my.telegram.org/.
2. Перейдите в API development tools.
3. Создайте приложение.
4. Скопируйте `api_id` и `api_hash`.

Р' `.env`:

```env
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_PHONE=
TELEGRAM_DRY_RUN=0
```

`TELEGRAM_DRY_RUN=1` включает preview-режим без Telegram-действий.

## 4. Безопасные команды

Посмотреть статистику без Telegram:

```powershell
python main.py --no-telegram --dry-run --stats
```

Открыть меню без Telegram:

```powershell
python main.py --no-telegram --dry-run
```

Обычный запуск:

```powershell
python main.py
```

## 5. Добавить первый мульти-аккаунт

1. Запустите web-интерфейс:
   ```powershell
   python main.py
   ```
2. Откройте вкладку **Аккаунты**.
3. Нажмите **+ Добавить**.
4. Введите `API ID`, `API HASH` и полный телефон аккаунта.
5. Нажмите **Отправить код**.
6. Введите код, который пришел в Telegram.
7. Если включен двухфакторный пароль, появится поле `2FA пароль`; введите пароль и нажмите **Подтвердить 2FA**.
8. После успешного входа аккаунт появится в таблице со статусом `active`.

Live-проверки на вкладке **Telegram** используют только аккаунты из `sessions/`. Если аккаунтов нет, добавьте их во вкладке **Аккаунты**; основной аккаунт из `.env` предназначен только для создания каналов.

## 6. Главное меню

```text
1. Генерировать и оценить батч
2. Проверить доступность на Telegram
3. Создать канал для username
4. Статистика и просмотр базы
5. Переключить dry-run
6. Аккаунты Telegram
7. Выход
```

Telegram подключается лениво: при запуске меню соединение не создаётся. Live-проверки подключают аккаунты из `sessions/`, а создание канала подключает основной аккаунт из `.env`.

## 7. Рабочий сценарий

1. Выберите `1`.
2. Введите размер батча, например `50` или `100`.
3. Дождитесь оценки.
4. Откройте `4 -> 5`, чтобы посмотреть топ по score.
5. Откройте `2`, чтобы проверить лучшие username через аккаунты из `sessions/`.
6. Если username доступен, основной аккаунт из `.env` используется только на этапе создания канала, и скрипт спросит:
   ```text
   Использовать <username> (score: X)? (y/n)
   ```
7. Канал создаётся только при ответе `y`.

## 8. Правила username

Текущая политика проекта:

- длина: `5-6`;
- символы: только `a-z`;
- без цифр, подчёркиваний и спецсимволов;
- служебные слова LLM блокируются;
- старые 4-буквенные записи могут оставаться в базе, но не отправляются на Telegram-проверку.

## 9. Просмотр базы

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

Пункт `2. Доступные username` показывает только username, которые можно использовать:

- статус `available`;
- нРµ `used`;
- проходят текущую валидацию `5-6 [a-z]`.

## 10. Статусы

```text
unchecked      ещё не проверялся в Telegram
checked_taken  занят или недоступен
available      Telegram показал, что доступен
used           уже использован для канала
invalid        невалиден
error          ошибка проверки
```

## 11. Статусы аккаунтов Telegram

```text
active    аккаунт доступен для live-проверки
cooldown  аккаунт временно пропускается после FloodWait/RPCError
dead      сессия недействительна или требует повторного входа
```

`FloodWaitError` ставит cooldown на время из ошибки Telegram. Обычный `RPCError` ставит cooldown на 120 секунд. Ошибки авторизации помечают аккаунт как `dead`.

## 12. Что сохраняется

База `username_database.db` хранит:

- оценки;
- статусы Telegram-проверки;
- доступные username;
- использованные username;
- состав новых батчей;
- channel_id/channel_name для used.

Не удаляйте:

```text
username_database.db
telegram_session.session
telegram_session.session-journal
sessions/
```

## 13. Troubleshooting

### ModuleNotFoundError

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### LM Studio connection refused

1. Откройте LM Studio.
2. Запустите server.
3. Проверьте `.env`.

### Telegram просиС' код

Это нормально при первом подключении. Введите код из Telegram и 2FA-пароль, если он включён.

### FloodWait

При FloodWait аккаунт проверки уходит в `cooldown`, а проверка переключается на следующий доступный аккаунт из `sessions/`. Основной аккаунт из `.env` в проверках не участвует.

### Смотреть последние логи

```powershell
Get-Content logs\logs.txt -Tail 100
```

## 14. Проверка после изменений

```powershell
python main.py --no-telegram --dry-run --stats
```

Если команда прошла, база и импорт основных модулей работают.
