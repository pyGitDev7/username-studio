"""
Система логирования проекта
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

import config

# Создаём директорию для логов если её нет
Path("logs").mkdir(exist_ok=True)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def setup_logger(name: str = "username_generator") -> logging.Logger:
    """
    Настраивает логгер с выводом в файл и консоль
    
    Args:
        name: имя логгера
        
    Returns:
        logger: настроенный экземпляр логгера
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Очищаем старые обработчики если есть
    logger.handlers.clear()
    
    # Формат логов
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик файлов
    file_handler = logging.FileHandler(
        f"logs/{config.LOG_FILE}",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Обработчик консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt='[%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Создаём глобальный логгер
logger = setup_logger()


def log_batch_start(batch_num: int, batch_size: int):
    """Логирует начало батча"""
    logger.info(f"▶️ НАЧАЛО БАТЧ #{batch_num} ({batch_size} username)")


def log_batch_complete(batch_num: int, count: int):
    """Логирует завершение батча"""
    logger.info(f"✅ БАТЧ #{batch_num} завершён ({count} username)")


def log_evaluation_result(username: str, score: float):
    """Логирует результат оценки"""
    logger.debug(f"📊 {username} - score: {score:.2f}")


def log_telegram_check(username: str, available: bool):
    """Логирует результат проверки на Telegram"""
    status = "🟢 ДОСТУПЕН" if available else "🔴 ЗАНЯТ"
    logger.info(f"📱 {username} - {status}")


def log_channel_created(username: str, channel_id: int):
    """Логирует создание канала"""
    logger.info(f"✨ Канал создан: @{username} (ID: {channel_id})")


def log_error(message: str, exception: Exception = None):
    """Логирует ошибку"""
    if exception:
        logger.error(f"❌ {message}: {exception}")
    else:
        logger.error(f"❌ {message}")


def log_warning(message: str):
    """Логирует предупреждение"""
    logger.warning(f"⚠️ {message}")
