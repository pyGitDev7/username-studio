"""
Клиент Telegram для проверки и создания каналов
"""
import asyncio
import time
import random
from typing import List, Dict, Tuple, Optional

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    UsernameNotOccupiedError,
    UsernameInvalidError,
    UsernameOccupiedError,
    RPCError,
)
from telethon.tl.functions.account import CheckUsernameRequest as CheckAccountUsernameRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.channels import (
    CheckUsernameRequest as CheckChannelUsernameRequest,
    CreateChannelRequest,
    UpdateUsernameRequest,
)

import config
import utils
from logger import logger


class TelegramChannelManager:
    """Управляет каналами Telegram"""
    
    def __init__(self, api_id: Optional[int] = None,
                 api_hash: Optional[str] = None,
                 phone: Optional[str] = None):
        """
        Инициализирует менеджер Telegram
        
        Args:
            api_id: ID приложения Telegram
            api_hash: хэш приложения Telegram
            phone: номер телефона для авторизации
        """
        self.api_id = config.TELEGRAM_API_ID if api_id is None else api_id
        self.api_hash = config.TELEGRAM_API_HASH if api_hash is None else api_hash
        self.phone = config.TELEGRAM_PHONE if phone is None else phone
        self.client = None
        self.request_delay = config.REQUEST_DELAY_MIN
        self.created_channels_count = 0
    
    async def connect(self):
        """Подключается к Telegram"""
        try:
            self.client = TelegramClient(
                config.SESSION_NAME,
                self.api_id,
                self.api_hash
            )
            
            # Важно! start() с phone будет просить код подтверждения
            await self.client.start(phone=self.phone)
            logger.info(f"✅ Подключено к Telegram")
            
            # Получаем информацию о пользователе
            me = await self.client.get_me()
            self._ensure_account_matches_config(me)
            logger.info(f"👤 Пользователь: {me.first_name} (@{me.username})")
            
        except Exception as e:
            if self.client:
                await self.client.disconnect()
                self.client = None
            logger.error(f"❌ Ошибка подключения: {e}")
            raise

    def _ensure_account_matches_config(self, me) -> None:
        if utils.telegram_phone_matches(getattr(me, "phone", ""), self.phone):
            return

        actual = self._mask_phone(getattr(me, "phone", "") or "")
        expected = self._mask_phone(self.phone)
        raise RuntimeError(
            "Активная Telegram-сессия принадлежит другому аккаунту "
            f"({actual}), а в .env указан {expected}. "
            f"Сбросьте сессию {config.SESSION_NAME}.session и войдите заново."
        )

    @staticmethod
    def _mask_phone(phone: str) -> str:
        phone = str(phone or "").strip()
        if len(phone) <= 5:
            return phone or "-"
        return f"{phone[:3]}{'*' * max(3, len(phone) - 6)}{phone[-3:]}"
    
    async def disconnect(self):
        """Отключается от Telegram"""
        if self.client:
            await self.client.disconnect()
            logger.info("✅ Отключено от Telegram")
    
    async def check_username_availability(self, username: str) -> bool:
        """
        Проверяет доступность username на Telegram
        
        Args:
            username: username для проверки (без @)
            
        Returns:
            bool: True если доступен
        """
        result = await self.check_username_status(username)
        return bool(result.get("available"))

    async def check_username_status(self, username: str, retry_count: int = 0) -> Dict[str, object]:
        """
        Проверяет username и возвращает подробный статус для сохранения в БД.
        """
        if not self.client:
            logger.error("❌ Клиент не подключен")
            return {"available": False, "status": "error", "notes": "client_not_connected"}
        
        username = utils.normalize_username_input(username)
        if not utils.is_telegram_username_format(username):
            logger.debug(f"❌ @{username} невалидный формат")
            return {"available": False, "status": "invalid", "notes": "invalid_format"}

        # Добавляем задержку для избежания флуд-блокировки
        await self._add_delay()

        try:
            # Шаг 1: Проверяем, не занят ли username кем-то другим (канал, бот, пользователь)
            try:
                await self.client(ResolveUsernameRequest(username))
                # Если дошли сюда — username существует (занят)
                logger.debug(f"❌ @{username} занят")
                return {"available": False, "status": "checked_taken", "notes": "resolve_username_found"}
            except UsernameNotOccupiedError:
                # Не занят — идём дальше
                pass

            # Шаг 2: Проверяем, доступен ли он для регистрации
            result = await self.client(CheckAccountUsernameRequest(username))

            if result:
                logger.info(f"✅ @{username} ДОСТУПЕН")
                return {"available": True, "status": "available", "notes": "account_check_ok"}
            else:
                logger.debug(f"❌ @{username} недоступен для регистрации")
                return {"available": False, "status": "checked_taken", "notes": "account_check_false"}

        except UsernameInvalidError:
            logger.debug(f"❌ @{username} невалидный формат")
            return {"available": False, "status": "invalid", "notes": "UsernameInvalidError"}
            
        except UsernameOccupiedError:
            logger.info(f"❌ @{username} ЗАНЯТ")
            return {"available": False, "status": "checked_taken", "notes": "UsernameOccupiedError"}

        except FloodWaitError as e:
            wait_time = e.seconds
            logger.warning(f"⚠️ FloodWait: {wait_time} сек")
            self.request_delay = min(self.request_delay * 2, config.REQUEST_DELAY_MAX)
            if retry_count >= config.MAX_FLOOD_RETRIES:
                return {"available": False, "status": "error", "notes": f"FloodWaitError after {retry_count} retries: {wait_time}s"}
            await asyncio.sleep(wait_time)
            return await self.check_username_status(username, retry_count + 1)

        except RPCError as e:
            if e.__class__.__name__ == "UsernamePurchaseAvailableError":
                logger.info(f"💎 @{username} доступен только как collectible/premium username")
                return {"available": False, "status": "invalid", "notes": "UsernamePurchaseAvailableError"}
            logger.error(f"❌ RPC ошибка проверки @{username}: {type(e).__name__}: {e}")
            return {"available": False, "status": "error", "notes": f"{type(e).__name__}: {e}"}

        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            logger.error(f"❌ Ошибка проверки @{username}: {err_msg}")
            return {"available": False, "status": "error", "notes": err_msg}
    
    async def create_channel(self, username: str, title: str = None) -> Optional[Tuple[int, str]]:
        """
        Создаёт канал с указанным username
        
        Args:
            username: желаемый username для канала
            title: название канала (если None, используется username)
            
        Returns:
            Tuple[channel_id, username] или None если ошибка
        """
        if not self.client:
            logger.error("❌ Клиент не подключен")
            return None
        
        # Проверяем лимит на создание каналов
        if self.created_channels_count >= config.MAX_CHANNELS_TO_CREATE:
            logger.warning(f"⚠️ Достигнут лимит: {config.MAX_CHANNELS_TO_CREATE} каналов")
            return None
        
        username = utils.normalize_username_input(username)
        if not utils.is_telegram_username_format(username):
            logger.error(f"❌ Невалидный username для канала: {username}")
            return None

        title = title or username
        
        try:
            if not await self.check_username_availability(username):
                logger.warning(f"⚠️ @{username} недоступен, канал не создаётся")
                return None

            logger.info(f"📝 Создание канала: @{username}")

            # Создаём канал
            result = await self.client(CreateChannelRequest(
                title=title,
                about=f"Channel: @{username}",
                megagroup=False
            ))
            channel = result.chats[0]
            channel_id = channel.id
            self.created_channels_count += 1

            await self._add_delay()

            channel_check = await self.client(CheckChannelUsernameRequest(
                channel=channel,
                username=username
            ))
            if not channel_check:
                logger.warning(f"⚠️ Telegram не разрешил username @{username} для созданного канала")
                return None

            await self._add_delay()

            # Устанавливаем username
            await self.client(UpdateUsernameRequest(
                channel=channel,
                username=username
            ))

            logger.info(f"✨ Канал создан: @{username} (ID: {channel_id})")

            return channel_id, username
            
        except FloodWaitError as e:
            wait_time = e.seconds
            logger.warning(f"⚠️ FloodWait при создании: {wait_time} сек")
            self.request_delay = min(self.request_delay * 2, config.REQUEST_DELAY_MAX)
            await asyncio.sleep(wait_time)
            # Пытаемся снова
            return await self.create_channel(username, title)
            
        except (UsernameInvalidError, UsernameOccupiedError) as e:
            logger.error(f"❌ Username @{username} нельзя установить: {type(e).__name__}: {e}")
            return None

        except RPCError as e:
            logger.error(f"❌ RPC ошибка создания канала @{username}: {type(e).__name__}: {e}")
            return None

        except Exception as e:
            logger.error(f"❌ Ошибка создания канала @{username}: {type(e).__name__}: {e}")
            return None
    
    async def check_batch(self, usernames: List[str]) -> Dict[str, bool]:
        """
        Проверяет батч username параллельно
        
        Args:
            usernames: список username для проверки
            
        Returns:
            Dict[str, bool]: словарь {username: available}
        """
        logger.info(f"🔍 Проверка {len(usernames)} username на Telegram")
        
        detailed = await self.check_batch_detailed(usernames)
        results = {username: bool(details.get("available")) for username, details in detailed.items()}

        available_count = sum(1 for v in results.values() if v)
        logger.info(f"📊 Результат: {available_count}/{len(usernames)} доступны")
        
        return results

    async def check_batch_detailed(self, usernames: List[str], progress_callback=None) -> Dict[str, Dict[str, object]]:
        """
        Проверяет батч username последовательно и возвращает подробные статусы.
        """
        logger.info(f"🔍 Подробная проверка {len(usernames)} username на Telegram")

        results = {}
        total = len(usernames)
        for index, username in enumerate(usernames, 1):
            results[username] = await self.check_username_status(username)
            if progress_callback:
                callback_result = progress_callback(username, results[username], index, total)
                if asyncio.iscoroutine(callback_result):
                    await callback_result

        available_count = sum(1 for details in results.values() if details.get("available"))
        logger.info(f"📊 Результат: {available_count}/{len(usernames)} доступны")
        return results
    
    async def _add_delay(self):
        """Добавляет задержку между запросами"""
        delay = random.uniform(
            config.REQUEST_DELAY_MIN,
            config.REQUEST_DELAY_MAX
        )
        await asyncio.sleep(delay)
    
    def get_created_channels_count(self) -> int:
        """Возвращает количество созданных каналов"""
        return self.created_channels_count
    
    def reset_created_channels_count(self):
        """Сбрасывает счётчик каналов"""
        self.created_channels_count = 0


def create_telegram_manager() -> TelegramChannelManager:
    """
    Фабрика для создания менеджера Telegram
    
    Returns:
        TelegramChannelManager: новый экземпляр менеджера
    """
    config.reload_env()
    return TelegramChannelManager()
