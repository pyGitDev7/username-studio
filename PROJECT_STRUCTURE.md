# РЎС‚СЂСѓРєС‚СѓСЂР° РїСЂРѕРµРєС‚Р°

РџР°РїРєР°:

```text
C:\path\to\telegram-username-generator
```

## РћСЃРЅРѕРІРЅС‹Рµ РјРѕРґСѓР»Рё

| Р¤Р°Р№Р» | РќР°Р·РЅР°С‡РµРЅРёРµ |
|---|---|
| `main.py` | CLI, РјРµРЅСЋ, workflow РіРµРЅРµСЂР°С†РёРё/РѕС†РµРЅРєРё/РїСЂРѕРІРµСЂРєРё/СЃРѕР·РґР°РЅРёСЏ |
| `config.py` | РќР°СЃС‚СЂРѕР№РєРё Telegram, LM Studio, С„РёР»СЊС‚СЂРѕРІ, score Рё Р»РёРјРёС‚РѕРІ |
| `llm_generator.py` | Р“РµРЅРµСЂР°С†РёСЏ username Рё СѓСЃС‚РѕР№С‡РёРІС‹Р№ РїР°СЂСЃРёРЅРі LLM-РѕС‚РІРµС‚РѕРІ |
| `llm_evaluator.py` | РћС†РµРЅРєР° username Рё РІРѕСЃСЃС‚Р°РЅРѕРІР»РµРЅРёРµ РѕС†РµРЅРѕРє РёР· РіСЂСЏР·РЅРѕРіРѕ JSON |
| `telegram_client.py` | Telethon-РєР»РёРµРЅС‚, РїСЂРѕРІРµСЂРєР° РґРѕСЃС‚СѓРїРЅРѕСЃС‚Рё, СЃРѕР·РґР°РЅРёРµ РєР°РЅР°Р»РѕРІ |
| `username_filter.py` | Р¤РёР»СЊС‚СЂР°С†РёСЏ username РїРµСЂРµРґ РѕС†РµРЅРєРѕР№/РїСЂРѕРІРµСЂРєРѕР№ |
| `storage.py` | SQLite-СЃС…РµРјР°, РјРёРіСЂР°С†РёРё, СЃС‚Р°С‚РёСЃС‚РёРєР°, Р·Р°РїСЂРѕСЃС‹ РїСЂРѕСЃРјРѕС‚СЂР° |
| `utils.py` | РќРѕСЂРјР°Р»РёР·Р°С†РёСЏ, РІР°Р»РёРґР°С†РёСЏ, СЌРІСЂРёСЃС‚РёРєРё, fallback helpers |
| `logger.py` | Р›РѕРіРё РІ РєРѕРЅСЃРѕР»СЊ Рё `logs/logs.txt` |

## Р”РѕРєСѓРјРµРЅС‚Р°С†РёСЏ

| Р¤Р°Р№Р» | РќР°Р·РЅР°С‡РµРЅРёРµ |
|---|---|
| `START_HERE.md` | РЎР°РјС‹Р№ РєРѕСЂРѕС‚РєРёР№ РІС…РѕРґ РІ РїСЂРѕРµРєС‚ |
| `README.md` | РћР±С‰РµРµ РѕРїРёСЃР°РЅРёРµ РІРѕР·РјРѕР¶РЅРѕСЃС‚РµР№ |
| `INSTRUCTIONS.md` | РџРѕРґСЂРѕР±РЅР°СЏ РёРЅСЃС‚СЂСѓРєС†РёСЏ Р·Р°РїСѓСЃРєР° |
| `QUICK_START.md` | РџСЂРёРјРµСЂС‹ Р°РІС‚РѕРјР°С‚РёР·Р°С†РёРё |
| `PROJECT_STRUCTURE.md` | Р­С‚РѕС‚ С„Р°Р№Р» |
| `SUMMARY.md` | РљСЂР°С‚РєРѕРµ СЃРѕСЃС‚РѕСЏРЅРёРµ РїСЂРѕРµРєС‚Р° |
| `TECHNICAL_SPEC.md` | РўРµРєСѓС‰РµРµ РўР—/СЃРїРµС†РёС„РёРєР°С†РёСЏ |

## Р”Р°РЅРЅС‹Рµ Рё Р»РѕРєР°Р»СЊРЅС‹Рµ С„Р°Р№Р»С‹

| Р¤Р°Р№Р»/РїР°РїРєР° | РќР°Р·РЅР°С‡РµРЅРёРµ |
|---|---|
| `username_database.db` | SQLite-Р±Р°Р·Р°. РќРµ СѓРґР°Р»СЏС‚СЊ |
| `telegram_session.session` | Telegram-СЃРµСЃСЃРёСЏ Telethon. РќРµ СѓРґР°Р»СЏС‚СЊ |
| `telegram_session.session-journal` | SQLite journal СЃРµСЃСЃРёРё. РќРµ СѓРґР°Р»СЏС‚СЊ РІСЂСѓС‡РЅСѓСЋ |
| `logs/logs.txt` | Р›РѕРіРё |
| `.env` | Р›РѕРєР°Р»СЊРЅС‹Рµ СЃРµРєСЂРµС‚С‹ Рё РЅР°СЃС‚СЂРѕР№РєРё |
| `.env.example` | РЁР°Р±Р»РѕРЅ РЅР°СЃС‚СЂРѕРµРє |
| `venv/` | Р’РёСЂС‚СѓР°Р»СЊРЅРѕРµ РѕРєСЂСѓР¶РµРЅРёРµ |

## РђСЂС…РёС‚РµРєС‚СѓСЂР°

```text
main.py
  в”њв”Ђ LLMUsernameGenerator
  в”‚    в”њв”Ђ LM Studio API
  в”‚    в””в”Ђ fallback generation
  в”њв”Ђ UsernameFilter
  в”‚    в””в”Ђ strict 5-6 [a-z] validation
  в”њв”Ђ LLMUsernameEvaluator
  в”‚    в”њв”Ђ LM Studio API
  в”‚    в””в”Ђ fallback scoring
  в”њв”Ђ UsernameStorage
  в”‚    в””в”Ђ SQLite
  в””в”Ђ TelegramChannelManager
       в””в”Ђ Telethon
```

## SQLite

### `checked_usernames`

РҐСЂР°РЅРёС‚ СЂРµР·СѓР»СЊС‚Р°С‚С‹ Telegram-РїСЂРѕРІРµСЂРєРё.

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

РҐСЂР°РЅРёС‚ username, РґР»СЏ РєРѕС‚РѕСЂС‹С… СЃРѕР·РґР°РЅ РєР°РЅР°Р».

```text
id
username
channel_id
channel_name
created_at
notes
```

### `scores`

РҐСЂР°РЅРёС‚ РїРѕСЃР»РµРґРЅСЋСЋ РѕС†РµРЅРєСѓ username.

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

РҐСЂР°РЅРёС‚ Р±Р°С‚С‡Рё.

```text
id
batch_num
total_usernames
available_count
generation_type
created_at
```

### `batch_usernames`

РҐСЂР°РЅРёС‚ СЃРѕСЃС‚Р°РІ РЅРѕРІС‹С… Р±Р°С‚С‡РµР№.

```text
id
batch_num
username
generation_type
created_at
```

РџСЂРёРјРµС‡Р°РЅРёРµ: СЃС‚Р°СЂС‹Рµ Р±Р°С‚С‡Рё РјРѕРіР»Рё РЅРµ РёРјРµС‚СЊ СЃРѕСЃС‚Р°РІР°, РїРѕСЌС‚РѕРјСѓ `batch_usernames` Р·Р°РїРѕР»РЅСЏРµС‚СЃСЏ РґР»СЏ РЅРѕРІС‹С… Р±Р°С‚С‡РµР№ РїРѕСЃР»Рµ РјРёРіСЂР°С†РёРё.

## РЎС‚Р°С‚СѓСЃС‹ username

```text
unchecked
checked_taken
available
used
invalid
error
```

## РћСЃРЅРѕРІРЅРѕР№ workflow

```text
1. Р“РµРЅРµСЂР°С†РёСЏ
   brandable / russian_transliteration / multilingual

2. РџР°СЂСЃРёРЅРі LLM
   JSON, markdown, dirty JSON, fallback extraction

3. Р¤РёР»СЊС‚СЂР°С†РёСЏ
   5-6 СЃРёРјРІРѕР»РѕРІ, С‚РѕР»СЊРєРѕ [a-z], blacklist, blocked service words

4. РћС†РµРЅРєР°
   readability, brandability, meaning, rarity

5. РЎРѕС…СЂР°РЅРµРЅРёРµ
   scores, batches, batch_usernames

6. РџСЂРѕРІРµСЂРєР° Telegram
   С‚РѕР»СЊРєРѕ Р»СѓС‡С€РёРµ unchecked РєР°РЅРґРёРґР°С‚С‹, safe limits, FloodWait handling

7. РЎРѕР·РґР°РЅРёРµ РєР°РЅР°Р»Р°
   С‚РѕР»СЊРєРѕ РїРѕСЃР»Рµ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
```

## CLI

```text
1. Р“РµРЅРµСЂРёСЂРѕРІР°С‚СЊ Рё РѕС†РµРЅРёС‚СЊ Р±Р°С‚С‡
2. РџСЂРѕРІРµСЂРёС‚СЊ РґРѕСЃС‚СѓРїРЅРѕСЃС‚СЊ РЅР° Telegram
3. РЎРѕР·РґР°С‚СЊ РєР°РЅР°Р» РґР»СЏ username
4. РЎС‚Р°С‚РёСЃС‚РёРєР° Рё РїСЂРѕСЃРјРѕС‚СЂ Р±Р°Р·С‹
5. РџРµСЂРµРєР»СЋС‡РёС‚СЊ dry-run
6. Р’С‹С…РѕРґ
```

## Р‘РµР·РѕРїР°СЃРЅРѕСЃС‚СЊ

- Telegram РЅРµ РїРѕРґРєР»СЋС‡Р°РµС‚СЃСЏ РїСЂРё РїСЂРѕСЃС‚РѕРј СЃС‚Р°СЂС‚Рµ РјРµРЅСЋ.
- `--no-telegram --dry-run` РїРѕР»РЅРѕСЃС‚СЊСЋ РѕС‚РєР»СЋС‡Р°РµС‚ Telegram-РґРµР№СЃС‚РІРёСЏ.
- РџСЂРѕРІРµСЂРєР° РєР°РЅРґРёРґР°С‚РѕРІ С„РёР»СЊС‚СЂСѓРµС‚ СЃС‚Р°СЂС‹Рµ РЅРµРІР°Р»РёРґРЅС‹Рµ Р·Р°РїРёСЃРё.
- РЎРѕР·РґР°РЅРёРµ РєР°РЅР°Р»Р° Р±Р»РѕРєРёСЂСѓРµС‚СЃСЏ РґР»СЏ `used`, `invalid`, `checked_taken`.
- FloodWait РѕР±СЂР°Р±Р°С‚С‹РІР°РµС‚СЃСЏ СЃ РѕРіСЂР°РЅРёС‡РµРЅРёРµРј РїРѕРІС‚РѕСЂРѕРІ.

