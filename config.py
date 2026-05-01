"""
Конфигурация проекта для генерации username
"""
import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()


def _read_int_env(name: str, default: int = 0) -> int:
    raw = os.getenv(name, str(default)).strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def reload_env() -> None:
    """Reload .env values that may change while the web app is running."""
    load_dotenv(override=True)

    global TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE, TELEGRAM_DRY_RUN, SESSION_NAME
    TELEGRAM_API_ID = _read_int_env("TELEGRAM_API_ID", 0)
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")
    TELEGRAM_DRY_RUN = os.getenv("TELEGRAM_DRY_RUN", "0").strip().lower() in {"1", "true", "yes", "y", "on"}
    SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_session")

# ========================
# TELEGRAM CONFIGURATION
# ========================
TELEGRAM_API_ID = _read_int_env("TELEGRAM_API_ID", 0)
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")

# ========================
# LM STUDIO CONFIGURATION
# ========================
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "local-model")
_temp_raw = os.getenv("LLM_TEMPERATURE", "0.95").strip()
LLM_TEMPERATURE = float(_temp_raw) if _temp_raw else 0.95

_tokens_raw = os.getenv("LLM_MAX_TOKENS", "2000").strip()
LLM_MAX_TOKENS = int(_tokens_raw) if _tokens_raw else 2000

# ========================
# USERNAME GENERATION
# ========================
# Обычные публичные username Telegram должны быть минимум 5 символов.
# Диапазон 4-6 из исходного промпта оставляет 4-буквенные варианты, которые
# Telegram почти всегда отклоняет как UsernameInvalidError.
USERNAME_MIN_LENGTH = 5
USERNAME_MAX_LENGTH = 6
BATCH_SIZE = 100  # сколько username за один батч

# Баланс типов генерации (в процентах)
GENERATION_BALANCE = {
    "brandable": 0.40,        # 40% коротких "искусственных" слов
    "russian_transliteration": 0.30,  # 30% русский транслит
    "multilingual": 0.30,     # 30% другие языки
}

# ========================
# FILTERING CONFIGURATION
# ========================
BLACKLIST_PATTERNS = [
    r"^([a-z])\1{2,}$",      # aaa, aaaa, bbbbb - повторения
    r"^(qwer|asdf|zxcv|hjkl|sdfg|wert|xcvb)$",  # слабые клавиатурные паттерны
    r"(qzx|xqz|zxq|qwx|wqx)",  # трудные сочетания
]

BLOCKED_USERNAMES = {
    # Служебные слова, которые иногда вытаскиваются из ответа LLM при грязном JSON.
    "about", "array", "brand", "chars", "clean", "could", "exact", "extra",
    "field", "final", "first", "format", "given", "great", "input", "items",
    "json", "latin", "letter", "lines", "lists", "model", "names", "only",
    "other", "reply", "score", "short", "sound", "style", "these", "title",
    "using", "valid", "value", "words", "write",
}

# ========================
# TELEGRAM LIMITS
# ========================
REQUEST_DELAY_MIN = 5        # минимальная задержка (сек)
REQUEST_DELAY_MAX = 15       # максимальная задержка (сек)
MAX_CHANNELS_TO_CREATE = 10  # максимум каналов за сессию
MAX_FLOOD_RETRIES = 2        # максимум повторов после FloodWait для одного username
TELEGRAM_DRY_RUN = os.getenv("TELEGRAM_DRY_RUN", "0").strip().lower() in {"1", "true", "yes", "y", "on"}

# ========================
# STORAGE
# ========================
DATABASE_PATH = "username_database.db"
LOG_FILE = "logs.txt"

# ========================
# EVALUATOR SCORING
# ========================
SCORE_THRESHOLD = 6.0  # минимальный score для проверки на Telegram
MAX_TELEGRAM_CHECKS_PER_BATCH = 30
READABILITY_WEIGHT = 0.3
BRANDABILITY_WEIGHT = 0.3
MEANING_WEIGHT = 0.2
RARITY_WEIGHT = 0.2

# ========================
# SESSION CONFIGURATION
# ========================
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_session")
