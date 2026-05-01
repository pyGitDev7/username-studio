"""
Утилиты для проекта
"""
import random
import string
import re
from typing import List, Set
from unidecode import unidecode

import config

VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnprstvwxyz"


def is_valid_username(
    username: str,
    min_length: int = None,
    max_length: int = None,
    allow_digits: bool = False,
) -> bool:
    """
    Проверяет, соответствует ли username требованиям
    
    Args:
        username: проверяемое имя пользователя
        
    Returns:
        bool: True если валидно, False иначе
    """
    if not isinstance(username, str):
        return False

    username = remove_accents(username).lower().strip()
    min_length = config.USERNAME_MIN_LENGTH if min_length is None else int(min_length)
    max_length = config.USERNAME_MAX_LENGTH if max_length is None else int(max_length)

    # Проверка длины и символов
    if allow_digits:
        pattern = rf"^[a-z][a-z0-9]{{{max(min_length - 1, 0)},{max(max_length - 1, 0)}}}$"
    else:
        pattern = rf"^[a-z]{{{min_length},{max_length}}}$"
    if not re.match(pattern, username):
        return False

    if username in config.BLOCKED_USERNAMES:
        return False
    
    # Проверка на чёрные паттерны
    for pattern in config.BLACKLIST_PATTERNS:
        if re.match(pattern, username):
            return False
    
    return True


def is_telegram_username_format(username: str) -> bool:
    """Checks Telegram's public username shape without project score filters."""
    if not isinstance(username, str):
        return False

    username = remove_accents(username).strip()
    if username.startswith("@"):
        username = username[1:]

    return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{3,30}[A-Za-z0-9]", username))


def has_excessive_repetition(username: str) -> bool:
    """
    Проверяет на чрезмерные повторения букв
    
    Args:
        username: проверяемое имя пользователя
        
    Returns:
        bool: True если есть чрезмерные повторения
    """
    # Две одинаковые буквы подряд - нормально
    # Три и более - плохо
    for char in set(username):
        if char * 3 in username:
            return True
    return False


def prefer_vowels(username: str) -> float:
    """
    Вычисляет "балл гласных" - предпочтение наличию гласных
    
    Args:
        username: имя пользователя
        
    Returns:
        float: коэффициент от 0 до 1
    """
    vowel_count = count_vowels(username)
    return min(vowel_count / len(username), 1.0)


def avoid_difficult_combinations(username: str) -> bool:
    """
    Проверяет на сложные комбинации букв
    
    Args:
        username: имя пользователя
        
    Returns:
        bool: True если содержит сложные комбинации
    """
    difficult_patterns = [
        r"[qzx]{2,}",  # qz, zx, qx и их комбо
        r"xq",
        r"zq",
        r"qwx",
        r"wqx",
        r"zxq",
        r"xqz",
    ]
    for pattern in difficult_patterns:
        if re.search(pattern, username):
            return True
    return False


def count_vowels(username: str) -> int:
    """Возвращает количество гласных в username."""
    return sum(1 for char in username if char in VOWELS)


def longest_consonant_run(username: str) -> int:
    """Возвращает максимальную длину подряд идущих согласных."""
    longest = 0
    current = 0

    for char in username:
        if char in CONSONANTS:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


def looks_like_service_word(username: str) -> bool:
    """Проверяет слова, которые чаще всего являются мусором из ответа модели."""
    return cleanup_string(username) in config.BLOCKED_USERNAMES


def phonetic_quality(username: str) -> float:
    """Оценивает фонетическую пригодность короткого username в диапазоне 0-10."""
    username = cleanup_string(username)
    if not is_valid_username(username):
        return 0.0

    score = 6.0
    vowel_count = count_vowels(username)
    vowel_ratio = vowel_count / len(username)

    if 0.30 <= vowel_ratio <= 0.55:
        score += 1.4
    elif vowel_count == 0:
        score -= 3.0
    else:
        score -= 0.8

    consonant_run = longest_consonant_run(username)
    if consonant_run >= 4:
        score -= 2.5
    elif consonant_run == 3:
        score -= 1.0

    if has_excessive_repetition(username):
        score -= 2.0
    if avoid_difficult_combinations(username):
        score -= 2.5

    rare_count = sum(1 for char in username if char in "qxz")
    if rare_count == 1:
        score += 0.3
    elif rare_count > 1:
        score -= 1.5

    if len(username) == config.USERNAME_MIN_LENGTH:
        score += 0.3

    return max(0.0, min(10.0, score))


def remove_accents(text: str) -> str:
    """
    Убирает акценты и преобразует в ASCII
    
    Args:
        text: исходный текст
        
    Returns:
        str: текст без акцентов
    """
    return unidecode(text)


def truncate_to_length(text: str, max_length: int) -> str:
    """
    Обрезает текст до нужной длины, старясь сохранить смысл
    
    Args:
        text: исходный текст
        max_length: максимальная длина
        
    Returns:
        str: обрезанный текст
    """
    if len(text) <= max_length:
        return text
    
    # Пытаемся обрезать в конце гласной для лучшей фонетики
    vowels = "aeiou"
    
    # Вариант 1: обрезать ровно
    truncated = text[:max_length]
    
    # Вариант 2: обрезать в конце на гласную если возможно
    for i in range(max_length, max_length - 2, -1):
        if i > 0 and i < len(text):
            if text[i - 1] in vowels:
                return text[:i]
    
    return truncated


def generate_random_username() -> str:
    """
    Генерирует случайный username как fallback
    
    Returns:
        str: случайный username
    """
    soft_starts = ["n", "v", "l", "m", "s", "r", "t", "k", "z", "p"]
    middles = ["a", "e", "i", "o", "u", "ae", "io", "or", "en", "al"]
    endings = ["a", "o", "e", "n", "r", "s", "x", "ia", "on", "en"]

    for _ in range(100):
        username = "".join([
            random.choice(soft_starts),
            random.choice(middles),
            random.choice(soft_starts),
            random.choice(endings),
        ])
        username = cleanup_string(username)[:config.USERNAME_MAX_LENGTH]

        if is_valid_username(username):
            return username

    return "noria"


def generate_batch_filename(batch_num: int) -> str:
    """
    Генерирует имя файла для сохранения батча
    
    Args:
        batch_num: номер батча
        
    Returns:
        str: имя файла
    """
    return f"batch_{batch_num:03d}.json"


def cleanup_string(text: str, allow_digits: bool = False) -> str:
    """
    Очищает строку от нежелательных символов
    
    Args:
        text: исходная строка
        
    Returns:
        str: очищенная строка
    """
    if text is None:
        return ""

    text = remove_accents(str(text)).lower()

    allowed = r"[^a-z0-9]" if allow_digits else r"[^a-z]"
    text = re.sub(allowed, "", text)
    return text


def normalize_username_input(text: str) -> str:
    """
    Нормализует пользовательский ввод без удаления запрещённых символов.
    Подходит для строгой валидации: @Name -> name, но name1 останется name1.
    """
    if text is None:
        return ""

    text = remove_accents(str(text)).lower().strip()
    if text.startswith("@"):
        text = text[1:]
    return text


def normalize_phone(phone: str) -> str:
    """Normalizes phone values for Telegram session/account comparisons."""
    return re.sub(r"\D", "", str(phone or ""))


def telegram_phone_matches(actual_phone: str, expected_phone: str) -> bool:
    expected = normalize_phone(expected_phone)
    if not expected:
        return True
    return normalize_phone(actual_phone) == expected


def unique_valid_usernames(
    usernames: List[str],
    min_length: int = None,
    max_length: int = None,
    allow_digits: bool = False,
) -> List[str]:
    """
    Нормализует список username, убирает дубликаты и невалидные варианты.
    """
    result = []
    seen = set()

    for username in usernames:
        clean = cleanup_string(username, allow_digits=allow_digits)
        if clean in seen:
            continue
        if not is_valid_username(
            clean,
            min_length=min_length,
            max_length=max_length,
            allow_digits=allow_digits,
        ):
            continue
        seen.add(clean)
        result.append(clean)

    return result


def calculate_readability_score(username: str) -> float:
    """
    Вычисляет оценку читаемости от 0 до 10
    
    Args:
        username: имя пользователя
        
    Returns:
        float: оценка читаемости
    """
    username = cleanup_string(username)
    if not is_valid_username(username):
        return 1.0

    score = 4.5  # базовая оценка
    
    # Предпочтение гласным
    score += prefer_vowels(username) * 3
    
    # Штраф за сложные комбинации
    if avoid_difficult_combinations(username):
        score -= 2
    
    # Штраф за повторения
    if has_excessive_repetition(username):
        score -= 1
    
    # Штраф за сложные переходы
    consonant_run = longest_consonant_run(username)
    if consonant_run >= 4:
        score -= 2
    elif consonant_run == 3:
        score -= 1

    score += phonetic_quality(username) * 0.2
    
    return max(0.0, min(10.0, score))


def is_word_like(username: str, known_words: Set[str] = None) -> bool:
    """
    Проверяет, похож ли username на слово
    
    Args:
        username: имя пользователя
        known_words: набор известных слов для проверки
        
    Returns:
        bool: True если похож на слово
    """
    if known_words and username in known_words:
        return True
    
    # Эвристика: если в слове есть хотя бы 2 гласные - похоже на слово
    vowels = count_vowels(username)
    return vowels >= 2
