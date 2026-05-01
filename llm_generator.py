"""
Генератор username с использованием LM Studio
Поддерживает 3 типа генерации:
1. BRANDABLE - короткие "искусственные" слова
2. RUSSIAN_TRANSLITERATION - русский транслит
3. MULTILINGUAL - многоязычный транслит
"""
import requests
import ast
import json
import random
import re
from typing import List, Dict

import config
from logger import logger
import utils


class LLMUsernameGenerator:
    """Генератор username с использованием локальной LLM"""
    USERNAME_KEYS = {"username", "usernames", "names", "handles", "results", "items", "data"}
    
    def __init__(
        self,
        base_url: str = config.LM_STUDIO_URL,
        model: str = config.LM_STUDIO_MODEL,
        min_length: int = config.USERNAME_MIN_LENGTH,
        max_length: int = config.USERNAME_MAX_LENGTH,
        allow_digits: bool = False,
    ):
        """
        Инициализирует генератор
        
        Args:
            base_url: URL LM Studio API
            model: модель для использования
        """
        self.base_url = base_url
        self.model = model
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
        self.min_length = int(min_length)
        self.max_length = int(max_length)
        self.allow_digits = bool(allow_digits)
        self._test_connection()

    def _length_text(self) -> str:
        return f"{self.min_length}-{self.max_length}"

    def _charset_text(self) -> str:
        return "[a-z0-9], start with a letter" if self.allow_digits else "[a-z]"

    def _unique_valid(self, usernames: List[str]) -> List[str]:
        return utils.unique_valid_usernames(
            usernames,
            min_length=self.min_length,
            max_length=self.max_length,
            allow_digits=self.allow_digits,
        )
    
    def _test_connection(self):
        """Проверяет соединение с LM Studio"""
        try:
            response = requests.get(f"{self.base_url.replace('/v1', '')}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ LM Studio доступен: {self.base_url}")
            else:
                logger.warning(f"⚠️ LM Studio может быть недоступен (статус: {response.status_code})")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к LM Studio: {e}")
    
    def _make_request(self, prompt: str, max_tokens: int = None) -> str:
        """
        Делает запрос к LM Studio API с автоопределением endpoint
        
        Args:
            prompt: промпт для генерации
            max_tokens: максимум токенов (опционально)
            
        Returns:
            str: результат генерации
        """
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        base = self.base_url.rstrip("/")
        
        # Пробуем OpenAI-compatible chat completions
        endpoints = [
            (f"{base}/chat/completions", "chat"),
            (f"{base}/v1/chat/completions", "chat"),
            (f"{base}/v1/completions", "legacy"),
            (f"{base}/api/v1/chat/completions", "chat"),
        ]
        
        for url, mode in endpoints:
            try:
                if mode == "chat":
                    payload = {
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": self.temperature,
                        "max_tokens": max_tokens,
                        "top_p": 0.95,
                    }
                else:
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": self.temperature,
                        "max_tokens": max_tokens,
                        "top_p": 0.95,
                    }
                
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if mode == "chat":
                    return data["choices"][0]["message"]["content"]
                else:
                    return data["choices"][0]["text"]
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in (404, 405):
                    continue  # Пробуем следующий endpoint
                logger.error(f"❌ HTTP ошибка ({url}): {e}")
                raise
            except (KeyError, IndexError) as e:
                raw = response.text if hasattr(response, "text") else str(response)
                logger.error(f"❌ Ошибка разбора ответа ({url}): {e}")
                logger.error(f"📄 Сырой ответ: {raw[:500]}")
                raise
        
        logger.error("❌ Ни один endpoint LM Studio не работает")
        raise RuntimeError("LM Studio endpoint недоступен")
    
    def generate_brandable(self, count: int = 30) -> List[str]:
        """
        Генерирует BRANDABLE username - короткие "искусственные" слова
        
        Args:
            count: количество username для генерации
            
        Returns:
            List[str]: список сгенерированных username
        """
        logger.info(f"🎯 Генерация BRANDABLE ({count} шт)...")
        
        nonce = random.randint(100000, 999999)
        prompt = f"""Generate exactly {count} unique, short, brandable usernames ({self._length_text()} characters).
These should be invented words that sound cool and memorable. Use only {self._charset_text()} characters.
Think like naming startups or apps.

Examples: novae, vexon, zenoa, lyron, nexo, voxel, tempo, astra, pyron

Output format: Return ONLY a JSON object with a "username" list, no other text.
Example: {{"username": ["novae", "vexon", "zenoa"]}}

Randomness nonce: {nonce}
Generate {count} unique usernames now:"""
        
        try:
            response = self._make_request(prompt, max_tokens=1000)
            usernames = self._parse_json_response(response)
            
            # Валидация и фильтрация
            valid_usernames = self._unique_valid(usernames)
            valid_usernames = self._ensure_count(valid_usernames, count, self._generate_brandable_fallback)
            logger.debug(f"✅ BRANDABLE: {len(valid_usernames)} валидных из {len(usernames)}")
            
            return valid_usernames[:count]
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации BRANDABLE: {e}")
            return self._generate_brandable_fallback(count)
    
    def generate_russian_transliteration(self, count: int = 30) -> List[str]:
        """
        Генерирует RUSSIAN TRANSLITERATION - русские слова в латинице
        
        Args:
            count: количество username для генерации
            
        Returns:
            List[str]: список сгенерированных username
        """
        logger.info(f"🇷🇺 Генерация RUSSIAN TRANSLITERATION ({count} шт)...")
        
        nonce = random.randint(100000, 999999)
        prompt = f"""Generate exactly {count} unique Russian words transliterated to Latin characters ({self._length_text()} characters).
Use simplified transliteration. You can shorten words to fit the configured length limit.

Examples:
- privet (привет - hello)
- volka (волк - wolf, adapted)
- tuman (туман - fog)
- moroz (мороз - frost)
- lunaa (луна - moon, adapted)
- canek (санёк - nickname for Alexander)
- pistolet → pistol (пистолет - pistol, shortened)
- molot (молот - hammer)

Rules:
1. Russian origin words only
2. {self._length_text()} characters
3. Use {self._charset_text()} only
4. Can truncate longer words
5. Prioritize common, memorable Russian words

Output format: Return ONLY a JSON object with a "username" list, no other text.
Example: {{"username": ["privet", "volka", "tuman"]}}

Randomness nonce: {nonce}
Generate {count} unique Russian transliterated usernames now:"""
        
        try:
            response = self._make_request(prompt, max_tokens=1000)
            usernames = self._parse_json_response(response)
            
            # Валидация
            valid_usernames = self._unique_valid(usernames)
            valid_usernames = self._ensure_count(valid_usernames, count, self._generate_russian_fallback)
            logger.debug(f"✅ RUSSIAN: {len(valid_usernames)} валидных из {len(usernames)}")
            
            return valid_usernames[:count]
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации RUSSIAN: {e}")
            return self._generate_russian_fallback(count)
    
    def generate_multilingual(self, count: int = 30) -> List[str]:
        """
        Генерирует MULTILINGUAL - слова из разных языков в латинице
        
        Args:
            count: количество username для генерации
            
        Returns:
            List[str]: список сгенерированных username
        """
        logger.info(f"🌍 Генерация MULTILINGUAL ({count} шт)...")
        
        nonce = random.randint(100000, 999999)
        prompt = f"""Generate exactly {count} unique words from different languages transliterated to Latin characters ({self._length_text()} characters).
Mix languages and create cool sounding usernames.

Examples from various languages:
- Japanese: kazea (風 - wind), soraa (空 - sky)
- Italian: lupon (wolf), nerox (black)
- French: noira (black), bleua (blue)
- Spanish: fuego (fire), lunar (moon-like)
- German: blaua (blue), walde (forest)
- Korean: bomun (봄 - spring), namua (나무 - tree)
- Portuguese: riona (river), maris (sea)

Rules:
1. Mix languages - don't use same language twice in a row
2. {self._length_text()} characters
3. Use {self._charset_text()} only, no accents/diacritics
4. Avoid complex consonant clusters (qzx, xqz)
5. Prefer words with vowels (a, e, i, o, u)
6. Can truncate longer words (fuego → fueg if needed)

Output format: Return ONLY a JSON object with a "username" list, no other text.
Example: {{"username": ["kazea", "lupon", "noira"]}}

Randomness nonce: {nonce}
Generate {count} unique multilingual usernames now:"""
        
        try:
            response = self._make_request(prompt, max_tokens=1000)
            usernames = self._parse_json_response(response)
            
            # Валидация
            valid_usernames = self._unique_valid(usernames)
            valid_usernames = self._ensure_count(valid_usernames, count, self._generate_multilingual_fallback)
            logger.debug(f"✅ MULTILINGUAL: {len(valid_usernames)} валидных из {len(usernames)}")
            
            return valid_usernames[:count]
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации MULTILINGUAL: {e}")
            return self._generate_multilingual_fallback(count)
    
    def generate_balanced_batch(self, batch_size: int = 100) -> Dict[str, List[str]]:
        """
        Генерирует сбалансированный батч с тремя типами
        
        Args:
            batch_size: общее количество username в батче
            
        Returns:
            Dict[str, List[str]]: словарь с типами и username
        """
        logger.info(f"📦 Генерация СБАЛАНСИРОВАННОГО БАТЧА ({batch_size} username)")
        
        # Вычисляем распределение
        balance = config.GENERATION_BALANCE
        brandable_count = int(batch_size * balance["brandable"])
        russian_count = int(batch_size * balance["russian_transliteration"])
        multilingual_count = batch_size - brandable_count - russian_count  # остаток
        
        logger.debug(f"Распределение: {brandable_count} brandable, {russian_count} russian, {multilingual_count} multilingual")
        
        result = {
            "brandable": self.generate_brandable(brandable_count),
            "russian": self.generate_russian_transliteration(russian_count),
            "multilingual": self.generate_multilingual(multilingual_count),
        }
        
        # Перемешиваем для разнообразия
        all_usernames = result["brandable"] + result["russian"] + result["multilingual"]
        random.shuffle(all_usernames)
        
        logger.info(f"✅ БАТЧ: {len(all_usernames)} username сгенерировано")
        
        return {
            "all": all_usernames,
            "by_type": result,
            "count": len(all_usernames)
        }
    
    def _parse_json_response(self, response: str) -> List[str]:
        """
        Парсит JSON-ответ от LLM
        
        Args:
            response: текстовый ответ от LLM
            
        Returns:
            List[str]: список username
        """
        usernames = []

        for data in self._decode_json_values(response):
            usernames.extend(self._extract_usernames_from_value(data))

        if usernames:
            return self._unique_valid(usernames)

        logger.debug("Не удалось найти корректный JSON в ответе LLM, пробую извлечь слова")
        return self._parse_plain_text_usernames(response)

    def _strip_markdown_fences(self, response: str) -> str:
        """Убирает ```json ... ``` вокруг ответа LLM."""
        response = str(response or "").strip()
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", response, flags=re.IGNORECASE).strip()

    def _decode_json_values(self, response: str) -> List:
        """Достаёт JSON/Python-like блоки из markdown, текста и частично грязного JSON."""
        response = str(response or "")
        values = []
        seen_blocks = set()

        sources = [response]
        sources.extend(re.findall(r"```(?:json)?\s*(.*?)```", response, flags=re.IGNORECASE | re.DOTALL))

        for source in sources:
            for block in self._iter_json_like_blocks(source):
                block = block.strip()
                if not block or block in seen_blocks:
                    continue
                seen_blocks.add(block)

                value = self._load_json_like(block)
                if value is not None:
                    values.append(value)

        return values

    def _iter_json_like_blocks(self, text: str) -> List[str]:
        """Возвращает валидные и потенциально валидные JSON-фрагменты из текста."""
        blocks = []
        decoder = json.JSONDecoder()
        index = 0

        while index < len(text):
            match = re.search(r"[\{\[]", text[index:])
            if not match:
                break

            start = index + match.start()
            try:
                _, end = decoder.raw_decode(text[start:])
                blocks.append(text[start:start + end])
                index = start + end
            except json.JSONDecodeError:
                index = start + 1

        blocks.extend(self._iter_balanced_blocks(text))
        stripped = text.strip()
        if stripped.startswith(("{", "[")):
            blocks.append(stripped)

        return blocks

    def _iter_balanced_blocks(self, text: str) -> List[str]:
        """Ищет сбалансированные {...} и [...] блоки, не ломаясь на строках."""
        blocks = []
        stack = []
        start = None
        quote = None
        escaped = False
        pairs = {"{": "}", "[": "]"}

        for index, char in enumerate(text):
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
                continue

            if char in {"'", '"'}:
                quote = char
                continue

            if char in pairs:
                if not stack:
                    start = index
                stack.append(pairs[char])
                continue

            if stack and char == stack[-1]:
                stack.pop()
                if not stack and start is not None:
                    blocks.append(text[start:index + 1])
                    start = None

        return blocks

    def _load_json_like(self, text: str):
        """Пробует разобрать строгий JSON, затем распространённые грязные варианты."""
        text = self._repair_json_text(text)
        variants = [
            text,
            re.sub(r",\s*([}\]])", r"\1", text),
            re.sub(r"([{,]\s*)([A-Za-z_][\w-]*)\s*:", r'\1"\2":', text),
        ]

        for variant in dict.fromkeys(variants):
            try:
                return json.loads(variant)
            except json.JSONDecodeError:
                pass

            try:
                return ast.literal_eval(variant)
            except (ValueError, SyntaxError):
                pass

        return None

    def _repair_json_text(self, text: str) -> str:
        """Нормализует кавычки и частые JSON-шероховатости."""
        replacements = {
            "\u201c": '"',
            "\u201d": '"',
            "\u2018": "'",
            "\u2019": "'",
            "\ufeff": "",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.strip()

    def _extract_usernames_from_value(self, value) -> List[str]:
        """Извлекает username только из ожидаемых JSON-полей и списков."""
        if isinstance(value, str):
            return [value]

        if isinstance(value, list):
            result = []
            for item in value:
                result.extend(self._extract_usernames_from_value(item))
            return result

        if isinstance(value, dict):
            result = []
            for key, item in value.items():
                key_normalized = str(key).strip().lower()
                if key_normalized in self.USERNAME_KEYS:
                    result.extend(self._extract_usernames_from_value(item))
                elif isinstance(item, list) and any(isinstance(row, dict) and "username" in row for row in item):
                    result.extend(self._extract_usernames_from_value(item))
            return result

        return []

    def _parse_plain_text_usernames(self, response: str) -> List[str]:
        """Fallback-парсер для списков через строки, запятые или маркеры."""
        candidates = re.findall(
            rf"\b[A-Za-z][A-Za-z0-9]{{{max(self.min_length - 1, 0)},{max(self.max_length - 1, 0)}}}\b"
            if self.allow_digits
            else rf"\b[A-Za-z]{{{self.min_length},{self.max_length}}}\b",
            str(response or ""),
        )
        return self._unique_valid(candidates)

    def _ensure_count(self, usernames: List[str], count: int, fallback_factory) -> List[str]:
        """Добирает список валидными fallback-значениями до нужного размера."""
        result = self._unique_valid(usernames)
        attempts = 0

        while len(result) < count and attempts < 10:
            attempts += 1
            missing = count - len(result)
            result.extend(fallback_factory(max(missing * 2, missing), log=False))
            result = self._unique_valid(result)

        return result[:count]
    
    def _generate_brandable_fallback(self, count: int, log: bool = True) -> List[str]:
        """Fallback для генерации BRANDABLE без LLM"""
        if log:
            logger.warning(f"⚠️ Использование fallback для BRANDABLE")
        
        branded_words = [
            "novae", "vexon", "zenoa", "lyron", "nexio", "voxel", "tempo", "astra",
            "pyron", "orion", "apexo", "flexa", "fluxa", "synca", "azure", "pixel",
            "nexus", "prism", "titan", "atlas", "viora", "loren", "maven", "zelio",
            "arven", "noria", "valen", "solen", "korin", "lumin", "verio", "zenit",
            "velon", "ravio", "daxon", "sorix", "merio", "lenix", "vario", "kairo",
        ]

        return self._fallback_from_pool(branded_words, count, style="brandable")
    
    def _generate_russian_fallback(self, count: int, log: bool = True) -> List[str]:
        """Fallback для генерации RUSSIAN TRANSLITERATION без LLM"""
        if log:
            logger.warning(f"⚠️ Использование fallback для RUSSIAN TRANSLITERATION")
        
        russian_words = [
            "privet", "volka", "tuman", "moroz", "lunaa", "sanya", "molot", "veter",
            "nochx", "zvezd", "vodar", "iskra", "zemla", "vozduh", "lesok", "polyx",
            "goraa", "rekaa", "morea", "lisak", "kotik", "rybak", "zhuki", "beliy",
            "sokol", "yasen", "bereg", "dozor", "metel", "groza", "dobra", "sever",
            "zarya", "volna", "rosaa", "tenya", "lugok", "daryo", "plamx",
        ]

        return self._fallback_from_pool(russian_words, count, style="russian")
    
    def _generate_multilingual_fallback(self, count: int, log: bool = True) -> List[str]:
        """Fallback для генерации MULTILINGUAL без LLM"""
        if log:
            logger.warning(f"⚠️ Использование fallback для MULTILINGUAL")
        
        multilingual_words = [
            # Japanese
            "kazea", "soraa", "hoshi", "yamaa", "moria", "namix",
            # Italian
            "lupon", "nerox", "vinoa", "solea", "lunia", "marea",
            # French
            "noira", "bleua", "feura", "vento", "nuite", "clair",
            # Spanish
            "fuego", "cielo", "marea", "rioja", "soles", "lunar",
            # German
            "blaua", "walde", "berga", "sonne", "monda", "stern",
            # Portuguese
            "riona", "maris", "vento", "fogoa", "solia", "luara",
            # Korean romanization
            "bomun", "namua", "hanul", "baram", "dalin", "nario", "kaori", "amaro",
        ]

        return self._fallback_from_pool(multilingual_words, count, style="multilingual")

    def _fallback_from_pool(self, words: List[str], count: int, style: str = "brandable") -> List[str]:
        """Генерирует нужное количество уникальных валидных username из пула и CVC-шаблонов."""
        if count <= 0:
            return []

        result = self._unique_valid(words)
        random.shuffle(result)
        result = result[:count]

        syllables = {
            "brandable": (
                ["a", "e", "i", "o", "u", "ae", "io"],
                ["n", "v", "l", "r", "m", "s", "t", "k", "z", "x", "p", "d"],
                ["a", "o", "e", "on", "en", "ix", "io", "ia", "or", "ar"],
            ),
            "russian": (
                ["a", "o", "u", "e", "ya", "ra", "za", "ve", "do"],
                ["v", "l", "m", "r", "s", "t", "k", "z", "n", "d", "g"],
                ["a", "o", "ik", "ok", "ar", "en", "ya", "or", "na", "ra"],
            ),
            "multilingual": (
                ["ka", "no", "lu", "mi", "ra", "so", "na", "vi", "io"],
                ["r", "n", "l", "m", "s", "v", "t", "k", "d", "b"],
                ["a", "o", "e", "ia", "io", "an", "en", "is", "un", "ar"],
            ),
        }
        starts, mids, ends = syllables.get(style, syllables["brandable"])

        attempts = 0
        while len(result) < count and attempts < count * 200:
            attempts += 1
            candidate = "".join([
                random.choice(starts),
                random.choice(mids),
                random.choice(ends),
            ])
            candidate = utils.cleanup_string(candidate, allow_digits=self.allow_digits)

            if self.allow_digits and random.random() < 0.35 and len(candidate) < self.max_length:
                candidate += str(random.randint(2, 99))

            if len(candidate) < self.min_length:
                candidate += random.choice(ends)
            if len(candidate) > self.max_length:
                candidate = utils.truncate_to_length(candidate, self.max_length)

            quality_source = re.sub(r"\d", "", candidate) if self.allow_digits else candidate
            if (
                utils.is_valid_username(
                    candidate,
                    min_length=self.min_length,
                    max_length=self.max_length,
                    allow_digits=self.allow_digits,
                )
                and candidate not in result
                and utils.phonetic_quality(quality_source) >= 5.5
            ):
                result.append(candidate)

        while len(result) < count:
            base = utils.generate_random_username()
            if self.allow_digits and self.max_length > 1:
                suffix = str(random.randint(2, 9999))
                candidate = f"{base}{suffix}"[:self.max_length]
            else:
                candidate = base[:self.max_length]
            if len(candidate) < self.min_length:
                candidate = (candidate + random.choice(ends) * self.min_length)[:self.min_length]
            if (
                utils.is_valid_username(
                    candidate,
                    min_length=self.min_length,
                    max_length=self.max_length,
                    allow_digits=self.allow_digits,
                )
                and candidate not in result
            ):
                result.append(candidate)

        return result[:count]
