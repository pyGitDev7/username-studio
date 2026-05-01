"""
Фильтрация и валидация username
"""
import re
from typing import List, Set

import config
import utils
from logger import logger


class UsernameFilter:
    """Фильтрует и валидирует username"""
    
    def __init__(
        self,
        excluded_usernames: Set[str] = None,
        min_length: int = config.USERNAME_MIN_LENGTH,
        max_length: int = config.USERNAME_MAX_LENGTH,
        allow_digits: bool = False,
    ):
        """
        Инициализирует фильтр
        
        Args:
            excluded_usernames: набор username которые нужно исключить
        """
        self.excluded_usernames = excluded_usernames or set()
        self.min_length = int(min_length)
        self.max_length = int(max_length)
        self.allow_digits = bool(allow_digits)
        if self.allow_digits:
            pattern = f"^[a-z][a-z0-9]{{{max(self.min_length - 1, 0)},{max(self.max_length - 1, 0)}}}$"
        else:
            pattern = f"^[a-z]{{{self.min_length},{self.max_length}}}$"
        self.regex_pattern = re.compile(pattern)
    
    def filter_batch(self, usernames: List[str]) -> List[str]:
        """
        Фильтрует батч username, убирая невалидные
        
        Args:
            usernames: список username для фильтрации
            
        Returns:
            List[str]: отфильтрованные username
        """
        filtered = []
        
        for username in usernames:
            clean = utils.cleanup_string(username, allow_digits=self.allow_digits)
            if self.is_valid(clean):
                filtered.append(clean)
            else:
                logger.debug(f"❌ Отфильтрован: {username} (невалидный формат)")
        
        logger.info(f"✅ Фильтрация: {len(usernames)} → {len(filtered)} username")
        return filtered
    
    def is_valid(self, username: str) -> bool:
        """
        Проверяет полную валидность username
        
        Args:
            username: проверяемое имя пользователя
            
        Returns:
            bool: True если валидно
        """
        username = utils.normalize_username_input(username)
        if not username:
            return False
        
        # Проверка формата и длины
        if not self.regex_pattern.match(username):
            return False
        
        # Проверка на исключённые username
        if username in self.excluded_usernames:
            return False
        
        # Проверка на чёрные паттерны
        if not utils.is_valid_username(
            username,
            min_length=self.min_length,
            max_length=self.max_length,
            allow_digits=self.allow_digits,
        ):
            return False
        
        # Проверка на чрезмерные повторения
        if utils.has_excessive_repetition(username):
            return False
        
        # Проверка на сложные комбинации
        if utils.avoid_difficult_combinations(username):
            return False
        
        # Проверка на читаемость (минимальная гласная)
        if not self._has_minimum_readability(username):
            return False
        
        return True
    
    def _has_minimum_readability(self, username: str) -> bool:
        """
        Проверяет минимальную читаемость
        
        Args:
            username: имя пользователя
            
        Returns:
            bool: True если достаточно читаемо
        """
        vowels = "aeiou"
        vowel_count = sum(1 for c in username if c in vowels)
        
        # Минимум 1 гласная для читаемости
        return vowel_count >= 1
    
    def remove_duplicates(self, usernames: List[str]) -> List[str]:
        """
        Убирает дубликаты из списка
        
        Args:
            usernames: список username
            
        Returns:
            List[str]: уникальные username
        """
        original_count = len(usernames)
        unique_usernames = list(dict.fromkeys(
            utils.cleanup_string(u, allow_digits=self.allow_digits) for u in usernames
        ))
        unique_usernames = [u for u in unique_usernames if u]
        removed = original_count - len(unique_usernames)
        
        if removed > 0:
            logger.debug(f"🔄 Убрано дубликатов: {removed}")
        
        return unique_usernames
    
    def remove_blacklisted_patterns(self, usernames: List[str]) -> List[str]:
        """
        Убирает username с чёрными паттернами
        
        Args:
            usernames: список username
            
        Returns:
            List[str]: отфильтрованные username
        """
        filtered = []
        
        for username in usernames:
            is_blacklisted = False
            
            for pattern in config.BLACKLIST_PATTERNS:
                if re.match(pattern, username):
                    is_blacklisted = True
                    logger.debug(f"❌ Чёрный паттерн: {username} ({pattern})")
                    break
            
            if not is_blacklisted:
                filtered.append(username)
        
        logger.info(f"🚫 Чёрные паттерны: {len(usernames)} → {len(filtered)}")
        return filtered
    
    def add_excluded_username(self, username: str):
        """
        Добавляет username в список исключений
        
        Args:
            username: имя пользователя
        """
        self.excluded_usernames.add(username.lower())
    
    def add_excluded_batch(self, usernames: List[str]):
        """
        Добавляет батч username в исключения
        
        Args:
            usernames: список username
        """
        for username in usernames:
            self.add_excluded_username(username)
    
    def get_quality_score(self, username: str) -> float:
        """
        Вычисляет оценку качества для фильтрации
        
        Args:
            username: имя пользователя
            
        Returns:
            float: оценка качества от 0 до 10
        """
        score = 10.0
        
        # Штраф за длину (короче = лучше)
        length_penalty = (len(username) - self.min_length) * 0.5
        score -= length_penalty
        
        # Бонус за гласные
        vowel_bonus = utils.prefer_vowels(username) * 2
        score += vowel_bonus
        
        # Штраф за сложные комбинации
        if utils.avoid_difficult_combinations(username):
            score -= 3
        
        # Штраф за повторения
        if utils.has_excessive_repetition(username):
            score -= 2
        
        # Бонус за читаемость
        score += utils.calculate_readability_score(username) * 0.3
        
        return max(0.0, min(10.0, score))


def create_filter(
    excluded_usernames: Set[str] = None,
    min_length: int = config.USERNAME_MIN_LENGTH,
    max_length: int = config.USERNAME_MAX_LENGTH,
    allow_digits: bool = False,
) -> UsernameFilter:
    """
    Фабрика для создания фильтра
    
    Args:
        excluded_usernames: набор исключённых username
        
    Returns:
        UsernameFilter: новый экземпляр фильтра
    """
    return UsernameFilter(
        excluded_usernames,
        min_length=min_length,
        max_length=max_length,
        allow_digits=allow_digits,
    )
