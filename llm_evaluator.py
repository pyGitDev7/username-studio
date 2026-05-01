"""
Оценка качества username с использованием LLM
"""
import requests
import ast
import json
from typing import List, Dict
import re

import config
from logger import logger
import utils


class LLMUsernameEvaluator:
    """Оценивает качество username с помощью LLM"""
    RESULT_KEYS = {"results", "usernames", "scores", "items", "data"}
    USERNAME_KEYS = {"username", "name", "handle"}
    SCORE_KEY_ALIASES = {
        "readability": ("readability", "readable", "pronunciation", "memorability"),
        "brandability": ("brandability", "brandable", "brand", "branding"),
        "meaning": ("meaning", "semantic", "sense", "word_value"),
        "rarity": ("rarity", "unique", "uniqueness", "rare"),
    }
    
    def __init__(self, base_url: str = config.LM_STUDIO_URL, model: str = config.LM_STUDIO_MODEL):
        """
        Инициализирует оценщик
        
        Args:
            base_url: URL LM Studio API
            model: модель для использования
        """
        self.base_url = base_url
        self.model = model
        self.temperature = 0.1  # Низкая температура для консистентной оценки
        self.max_tokens = max(config.LLM_MAX_TOKENS, 2000)

    def _clamp_score(self, value: float) -> float:
        """Ограничивает оценку диапазоном 0-10."""
        if isinstance(value, str):
            match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", "."))
            value = match.group(0) if match else 5.0
        return max(0.0, min(10.0, float(value)))

    def _strip_markdown_fences(self, response: str) -> str:
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
    
    def _make_request(self, prompt: str) -> str:
        """
        Делает запрос к LM Studio API с автоопределением endpoint
        
        Args:
            prompt: промпт для оценки
            
        Returns:
            str: результат оценки
        """
        base = self.base_url.rstrip("/")
        
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
                        "max_tokens": self.max_tokens,
                    }
                else:
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
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
                    continue
                logger.error(f"❌ HTTP ошибка ({url}): {e}")
                raise
            except (KeyError, IndexError) as e:
                raw = response.text if hasattr(response, "text") else str(response)
                logger.error(f"❌ Ошибка разбора ({url}): {e} — {raw[:300]}")
                raise
        
        logger.error("❌ Ни один endpoint LM Studio не работает")
        raise RuntimeError("LM Studio endpoint недоступен")
    
    def evaluate_single(self, username: str) -> Dict[str, float]:
        """
        Оценивает один username по нескольким критериям
        
        Args:
            username: имя пользователя для оценки
            
        Returns:
            Dict[str, float]: словарь с оценками
        """
        logger.debug(f"📊 Оценка: {username}")
        
        prompt = f"""Evaluate the username "{username}" on these criteria (1-10 scale):

1. Readability: How easy is it to read and remember?
2. Brandability: Could it be a brand or project name?
3. Meaning: Does it have semantic value? (especially if it's transliteration)
4. Rarity: How unique and uncommon is it?

Also note:
- If it looks like a transliterated word, that increases meaning score
- Shorter is generally better for brandability
- Length {config.USERNAME_MIN_LENGTH}-{config.USERNAME_MAX_LENGTH} characters is optimal

Respond ONLY with JSON, no other text:
{{"readability": 0.0, "brandability": 0.0, "meaning": 0.0, "rarity": 0.0}}

Evaluate "{username}":"""
        
        try:
            response = self._make_request(prompt)
            scores = self._parse_scores(response)
            
            if scores:
                return scores
            else:
                return self._calculate_fallback_scores(username)
                
        except Exception as e:
            logger.error(f"❌ Ошибка оценки: {e}")
            return self._calculate_fallback_scores(username)
    
    def evaluate_batch(self, usernames: List[str], batch_size: int = 5) -> List[Dict]:
        """
        Оценивает батч username с группировкой для экономии запросов
        
        Args:
            usernames: список username для оценки
            batch_size: размер группы для оценки за раз
            
        Returns:
            List[Dict]: список результатов оценок
        """
        logger.info(f"📊 Оценка батча ({len(usernames)} username)")
        
        results = []
        
        # Обрабатываем батчами
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            batch_results = self._evaluate_batch_group(batch)
            results.extend(batch_results)
        
        # Добавляем total_score и сортируем
        results = self.rank_usernames(results)
        
        logger.info(f"✅ Оценено: {len(results)} username")
        
        return results
    
    def _evaluate_batch_group(self, usernames: List[str]) -> List[Dict]:
        """
        Оценивает группу username в одном запросе
        
        Args:
            usernames: список username (максимум 10)
            
        Returns:
            List[Dict]: результаты оценок
        """
        usernames_str = ", ".join(usernames)
        
        prompt = f"""Evaluate these {len(usernames)} usernames on criteria (1-10 scale):
Criteria: readability, brandability, meaning, rarity

Usernames: {usernames_str}

Rules for scoring:
1. Readability: pronunciation ease, memorable
2. Brandability: could be a brand/project
3. Meaning: semantic value (high if transliteration/real word)
4. Rarity: uniqueness

Respond ONLY with a compact valid JSON array. No markdown, no comments, no text before/after JSON.
Schema: [{{"username":"name","readability":7.0,"brandability":7.0,"meaning":7.0,"rarity":7.0}}]"""
        
        try:
            response = self._make_request(prompt)
            batch_results = self._parse_batch_scores(response, expected_usernames=set(usernames))
            
            # Заполняем fallback для отсутствующих результатов
            evaluated_usernames = {r["username"] for r in batch_results}
            for username in usernames:
                if username not in evaluated_usernames:
                    scores = self._calculate_fallback_scores(username)
                    batch_results.append({
                        "username": username,
                        **scores
                    })
            
            return batch_results
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка оценки группы: {e}")
            return [
                {
                    "username": username,
                    **self._calculate_fallback_scores(username)
                }
                for username in usernames
            ]
    
    def _parse_scores(self, response: str) -> Dict[str, float]:
        """
        Парсит JSON оценок из ответа
        
        Args:
            response: ответ от LLM
            
        Returns:
            Dict[str, float]: словарь с оценками
        """
        try:
            for value in self._decode_json_values(response):
                if isinstance(value, dict):
                    scores = self._coerce_score_item(value, allow_missing_username=True)
                    if scores:
                        scores.pop("username", None)
                        return scores

                for item in self._extract_score_items(value):
                    scores = self._coerce_score_item(item, allow_missing_username=True)
                    if scores:
                        scores.pop("username", None)
                        return scores

            return None

        except (ValueError, TypeError) as e:
            logger.debug(f"⚠️ Ошибка парсинга оценок: {e}")
            return None
    
    def _parse_batch_scores(self, response: str, expected_usernames: set = None) -> List[Dict]:
        """
        Парсит JSON массив оценок
        
        Args:
            response: ответ от LLM
            
        Returns:
            List[Dict]: список результатов
        """
        try:
            data = []
            for value in self._decode_json_values(response):
                data.extend(self._extract_score_items(value))

            if not data:
                data.extend(self._extract_score_items_from_text(response))

            results = []
            seen = set()
            for item in data:
                scores = self._coerce_score_item(item)
                if not scores:
                    continue

                username = scores["username"]
                if expected_usernames and username not in expected_usernames:
                    continue
                if username in seen:
                    continue

                seen.add(username)
                results.append(scores)

            return results

        except (ValueError, TypeError) as e:
            logger.debug(f"⚠️ Ошибка парсинга батча оценок: {e}")
            return []

    def _extract_score_items(self, value) -> List[Dict]:
        """Извлекает объекты оценок из массивов, вложенных results и dict username -> scores."""
        if isinstance(value, list):
            result = []
            for item in value:
                result.extend(self._extract_score_items(item))
            return result

        if not isinstance(value, dict):
            return []

        lowered_keys = {str(key).lower() for key in value}
        if lowered_keys & self.USERNAME_KEYS:
            return [value]

        result = []
        for key, item in value.items():
            key_normalized = str(key).strip().lower()
            if key_normalized in self.RESULT_KEYS:
                result.extend(self._extract_score_items(item))
            elif utils.is_valid_username(key_normalized):
                if isinstance(item, dict):
                    row = {"username": key_normalized}
                    row.update(item)
                    result.append(row)
                elif isinstance(item, (int, float, str)):
                    result.append({"username": key_normalized, "score": item})

        return result

    def _extract_score_items_from_text(self, response: str) -> List[Dict]:
        """Последняя попытка: достать отдельные объекты или строки с оценками из текста."""
        items = []
        for block in self._iter_balanced_blocks(str(response or "")):
            value = self._load_json_like(block)
            items.extend(self._extract_score_items(value))

        if items:
            return items

        pattern = re.compile(
            rf"\b(?P<username>[a-zA-Z]{{{config.USERNAME_MIN_LENGTH},{config.USERNAME_MAX_LENGTH}}})\b"
            r"(?P<context>.{0,180})",
            flags=re.DOTALL,
        )
        for match in pattern.finditer(str(response or "")):
            username = utils.cleanup_string(match.group("username"))
            if not utils.is_valid_username(username):
                continue

            context = match.group("context")
            row = {"username": username}
            found = False
            for field, aliases in self.SCORE_KEY_ALIASES.items():
                alias_pattern = "|".join(re.escape(alias) for alias in aliases)
                score_match = re.search(rf"(?:{alias_pattern})\D+(-?\d+(?:[\.,]\d+)?)", context, flags=re.IGNORECASE)
                if score_match:
                    row[field] = score_match.group(1)
                    found = True
            if found:
                items.append(row)

        return items

    def _coerce_score_item(self, item: Dict, allow_missing_username: bool = False) -> Dict:
        """Приводит один объект оценки к внутренней схеме."""
        if not isinstance(item, dict):
            return {}

        username = ""
        normalized = {str(key).strip().lower(): value for key, value in item.items()}
        for key in self.USERNAME_KEYS:
            if key in normalized:
                username = utils.cleanup_string(normalized.get(key, ""))
                break

        score_field_names = {"score", "total_score", "total", "overall"}
        for aliases in self.SCORE_KEY_ALIASES.values():
            score_field_names.update(aliases)
        if allow_missing_username and not (set(normalized) & score_field_names):
            return {}

        if not username and not allow_missing_username:
            return {}
        if username and not utils.is_valid_username(username):
            return {}

        total = self._find_score(item, ("score", "total_score", "total", "overall"))
        defaults = {
            "readability": total if total is not None else 5.0,
            "brandability": total if total is not None else 5.0,
            "meaning": total if total is not None else 5.0,
            "rarity": total if total is not None else 5.0,
        }

        result = {}
        if username:
            result["username"] = username

        for field, aliases in self.SCORE_KEY_ALIASES.items():
            value = self._find_score(item, aliases)
            result[field] = self._clamp_score(value if value is not None else defaults[field])

        return result

    def _find_score(self, item: Dict, aliases) -> float:
        """Ищет оценку по набору возможных названий поля."""
        normalized = {str(key).strip().lower(): value for key, value in item.items()}
        for alias in aliases:
            if alias in normalized:
                return normalized[alias]
        return None
    
    def _calculate_fallback_scores(self, username: str) -> Dict[str, float]:
        """
        Вычисляет fallback оценки без LLM
        
        Args:
            username: имя пользователя
            
        Returns:
            Dict[str, float]: словарь с оценками
        """
        username = utils.cleanup_string(username)
        logger.debug(f"Fallback оценка: {username}")

        if not utils.is_valid_username(username):
            return {
                "readability": 1.0,
                "brandability": 1.0,
                "meaning": 1.0,
                "rarity": 1.0,
            }

        phonetic = utils.phonetic_quality(username)
        readability = utils.calculate_readability_score(username)

        length_bonus = 0.5 if len(username) == config.USERNAME_MIN_LENGTH else 0.1
        brandability = 3.5 + phonetic * 0.45 + length_bonus

        vowel_count = utils.count_vowels(username)
        meaning = 3.8
        if utils.is_word_like(username):
            meaning += 1.4
        if re.search(r"(a|o|ia|io|en|on|ar|or)$", username):
            meaning += 0.5
        if vowel_count < 2:
            meaning -= 0.8

        rarity = 4.8
        rare_count = sum(1 for c in username if c in "qxz")
        if rare_count == 1:
            rarity += 0.7
        elif rare_count > 1:
            rarity -= 1.0
        if utils.has_excessive_repetition(username) or utils.longest_consonant_run(username) >= 3:
            rarity -= 0.8

        if utils.avoid_difficult_combinations(username):
            readability -= 1.5
            brandability -= 1.0
            rarity -= 1.0

        return {
            "readability": self._clamp_score(readability),
            "brandability": self._clamp_score(brandability),
            "meaning": self._clamp_score(meaning),
            "rarity": self._clamp_score(rarity),
        }
    
    def calculate_total_score(self, scores: Dict[str, float]) -> float:
        """
        Вычисляет общую оценку на основе взвешенных критериев
        
        Args:
            scores: словарь с оценками
            
        Returns:
            float: общая оценка (0-10)
        """
        total = (
            scores.get("readability", 5.0) * config.READABILITY_WEIGHT +
            scores.get("brandability", 5.0) * config.BRANDABILITY_WEIGHT +
            scores.get("meaning", 5.0) * config.MEANING_WEIGHT +
            scores.get("rarity", 5.0) * config.RARITY_WEIGHT
        )
        
        return min(10.0, max(0.0, total))
    
    def rank_usernames(self, evaluated_usernames: List[Dict]) -> List[Dict]:
        """
        Ранжирует username по общей оценке
        
        Args:
            evaluated_usernames: список с оценками
            
        Returns:
            List[Dict]: ранжированный список
        """
        # Вычисляем общие оценки
        for item in evaluated_usernames:
            scores = {
                "readability": item.get("readability", 5.0),
                "brandability": item.get("brandability", 5.0),
                "meaning": item.get("meaning", 5.0),
                "rarity": item.get("rarity", 5.0),
            }
            item["total_score"] = self.calculate_total_score(scores)
            item["score"] = item["total_score"]
        
        # Сортируем по общей оценке
        ranked = sorted(evaluated_usernames, key=lambda x: x["total_score"], reverse=True)
        
        return ranked
