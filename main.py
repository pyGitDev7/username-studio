"""
Главный скрипт для генерации, оценки, проверки и просмотра Telegram username.
"""
import argparse
import asyncio
from typing import List, Dict, Optional

import config
from account_manager import AccountManager
from logger import logger, log_batch_start, log_batch_complete, log_telegram_check, log_error
from storage import UsernameStorage
from username_filter import create_filter
from llm_generator import LLMUsernameGenerator
from llm_evaluator import LLMUsernameEvaluator
from telegram_client import create_telegram_manager, check_batch_with_rotation
import utils


class UsernameGenerationSystem:
    """Основная система для работы с username."""

    def __init__(self, dry_run: bool = config.TELEGRAM_DRY_RUN, no_telegram: bool = False):
        self.storage = UsernameStorage(config.DATABASE_PATH)
        self.generator = None
        self.evaluator = None
        self.telegram_manager = None
        self.account_manager = AccountManager()
        self.batch_num = self.storage.get_last_batch_num()
        self.last_evaluated_usernames = []
        self.last_generation_types = {}
        self.dry_run = dry_run
        self.no_telegram = no_telegram

        excluded = set(self.storage.get_all_checked_usernames())
        excluded.update(self.storage.get_all_used_usernames())
        self.filter = create_filter(excluded)

        logger.info("✅ Система инициализирована")
        if self.dry_run:
            logger.info("🧪 Dry-run включён: Telegram-проверки и создание каналов не выполняются")

    def _get_generator(self) -> LLMUsernameGenerator:
        if self.generator is None:
            self.generator = LLMUsernameGenerator()
        return self.generator

    def _get_evaluator(self) -> LLMUsernameEvaluator:
        if self.evaluator is None:
            self.evaluator = LLMUsernameEvaluator()
        return self.evaluator

    async def ensure_telegram(self) -> bool:
        """Лениво подключает Telegram только когда это действительно нужно."""
        config.reload_env()

        if self.no_telegram:
            logger.error("❌ Telegram отключён флагом --no-telegram")
            return False

        if self.dry_run:
            logger.info("🧪 Dry-run: Telegram подключаться не будет")
            return False

        if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
            logger.error("❌ TELEGRAM_API_ID/TELEGRAM_API_HASH не заданы в .env")
            return False

        if not self.telegram_manager:
            logger.info("📱 Подключение к Telegram...")
            self.telegram_manager = create_telegram_manager()
            await self.telegram_manager.connect()
            logger.info("✅ Telegram подключён")

        return True

    async def close_telegram(self):
        if self.telegram_manager:
            await self.telegram_manager.disconnect()

    def generate_batch(
        self,
        batch_size: int = config.BATCH_SIZE,
        min_length: int = config.USERNAME_MIN_LENGTH,
        max_length: int = config.USERNAME_MAX_LENGTH,
        allow_digits: bool = False,
    ) -> Dict:
        """Генерирует сбалансированный батч username."""
        min_length = max(1, int(min_length))
        max_length = max(min_length, int(max_length))
        allow_digits = bool(allow_digits)
        self.batch_num += 1
        log_batch_start(self.batch_num, batch_size)

        try:
            generator = LLMUsernameGenerator(
                min_length=min_length,
                max_length=max_length,
                allow_digits=allow_digits,
            )
            generation_filter = create_filter(
                set(self.filter.excluded_usernames),
                min_length=min_length,
                max_length=max_length,
                allow_digits=allow_digits,
            )
            generation_result = generator.generate_balanced_batch(batch_size)
            by_type = generation_result["by_type"]
            type_map = self._build_generation_type_map(by_type, allow_digits=allow_digits)

            usernames = generation_filter.remove_duplicates(generation_result["all"])
            usernames = generation_filter.filter_batch(usernames)
            self.last_generation_types = {username: type_map.get(username) for username in usernames}

            self.storage.add_batch(self.batch_num, len(usernames), "mixed")
            self.storage.add_batch_usernames(self.batch_num, usernames, self.last_generation_types)

            log_batch_complete(self.batch_num, len(usernames))
            self.filter.add_excluded_batch(usernames)

            return {
                "batch_num": self.batch_num,
                "usernames": usernames,
                "count": len(usernames),
                "by_type": by_type,
                "settings": {
                    "min_length": min_length,
                    "max_length": max_length,
                    "allow_digits": allow_digits,
                },
            }

        except Exception as e:
            log_error(f"Ошибка генерации батча #{self.batch_num}", e)
            return {
                "batch_num": self.batch_num,
                "usernames": [],
                "count": 0,
                "error": str(e),
            }

    def _build_generation_type_map(self, by_type: Dict[str, List[str]], allow_digits: bool = False) -> Dict[str, str]:
        result = {}
        aliases = {
            "brandable": "brandable",
            "russian": "russian_transliteration",
            "multilingual": "multilingual",
        }
        for raw_type, usernames in by_type.items():
            generation_type = aliases.get(raw_type, raw_type)
            for username in usernames:
                clean = utils.cleanup_string(username, allow_digits=allow_digits)
                if clean and clean not in result:
                    result[clean] = generation_type
        return result

    def evaluate_batch(self, usernames: List[str]) -> List[Dict]:
        """Оценивает батч username и сохраняет score."""
        logger.info(f"🔍 Начало оценки {len(usernames)} username")

        try:
            ranked = self._get_evaluator().evaluate_batch(usernames)

            for item in ranked:
                username = item["username"]
                generation_type = self.last_generation_types.get(username)
                item["generation_type"] = generation_type
                self.storage.save_scores(
                    username=username,
                    readability=item.get("readability", 0),
                    brandability=item.get("brandability", 0),
                    meaning=item.get("meaning", 0),
                    rarity=item.get("rarity", 0),
                    total_score=item.get("total_score", 0),
                    generation_type=generation_type,
                    batch_num=self.batch_num,
                )

            logger.info(f"✅ Оценено: {len(ranked)} username")
            self.last_evaluated_usernames = ranked
            return ranked

        except Exception as e:
            log_error("Ошибка оценки батча", e)
            return []

    async def check_availability_batch(self, candidates: List[Dict], progress_callback=None) -> Dict[str, Dict]:
        """Проверяет доступность username на Telegram и сохраняет статусы."""
        if self.no_telegram or self.dry_run:
            logger.info("🧪 Preview: Telegram-запросы не выполнялись")
            return {}

        usernames = [item["username"] for item in candidates]
        logger.info(f"📱 Проверка {len(usernames)} username на Telegram")

        try:
            if not self.account_manager.has_active_accounts():
                logger.error(
                    "❌ Для live-проверки нужен активный аккаунт во вкладке Аккаунты. "
                    "Основной Telegram-аккаунт из .env используется только для создания каналов."
                )
                return {}

            results = await check_batch_with_rotation(
                usernames,
                self.account_manager,
                progress_callback=progress_callback,
            )

            by_username = {item["username"]: item for item in candidates}
            for username, details in results.items():
                item = by_username.get(username, {})
                score = item.get("score") if item.get("score") is not None else self.storage.get_score(username)
                status = details.get("status") or ("available" if details.get("available") else "checked_taken")
                notes = details.get("notes") or f"Checked in batch #{self.batch_num}"
                self.storage.add_checked_username(
                    username=username,
                    available=bool(details.get("available")),
                    score=score,
                    generation_type=item.get("generation_type"),
                    notes=notes,
                    status=status,
                    batch_num=item.get("batch_num") or self.batch_num,
                )

                if details.get("available"):
                    log_telegram_check(username, True)

            return results

        except Exception as e:
            log_error("Ошибка проверки доступности", e)
            return {}

    async def create_channel_for_username(self, username: str, title: str = None) -> Optional[int]:
        """Создаёт канал для username после всех проверок и подтверждений."""
        username = utils.normalize_username_input(username)
        record = self.storage.get_username_record(username)
        if record and record.get("status") in {"checked_taken", "invalid", "used"}:
            logger.error(f"❌ @{username} не создаётся: статус в базе {record.get('status')}")
            return None

        if not await self.ensure_telegram():
            return None

        try:
            result = await self.telegram_manager.create_channel(username, title)
            if not result:
                return None

            channel_id, created_username = result
            self.storage.add_used_username(
                username=created_username,
                channel_id=channel_id,
                channel_name=title or created_username,
            )

            logger.info(f"✨ Канал создан: @{created_username} (ID: {channel_id})")
            return channel_id

        except Exception as e:
            log_error(f"Ошибка создания канала @{username}", e)
            return None

    async def run_interactive_mode(self):
        """Интерактивный режим работы."""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 ИНТЕРАКТИВНЫЙ РЕЖИМ")
        logger.info("=" * 60)

        while True:
            fresh_records = self.storage.get_username_records(
                limit=None,
                min_score=config.SCORE_THRESHOLD,
                status="unchecked",
                last_batch_only=True,
                valid_only=True,
            )
            fresh_count = len(self._filter_check_candidates(fresh_records, log_skips=False))
            mode = "dry-run" if self.dry_run else "live"

            print("\nОпции:")
            print(f"1. Генерировать и оценить батч")
            print(f"2. Проверить доступность на Telegram ({fresh_count} из последнего батча готовы к проверке)")
            print("3. Создать канал для username")
            print("4. Статистика и просмотр базы")
            print(f"5. Переключить dry-run (сейчас: {mode})")
            print("6. Аккаунты Telegram")
            print("7. Выход")

            choice = input("\nВыберите опцию (1-7): ").strip()

            if choice == "1":
                await self._option_generate_and_evaluate()
            elif choice == "2":
                await self._option_check_availability()
            elif choice == "3":
                await self._option_create_channel()
            elif choice == "4":
                self._option_show_stats_menu()
            elif choice == "5":
                self.dry_run = not self.dry_run
                logger.info(f"🧪 Dry-run: {'включён' if self.dry_run else 'выключен'}")
            elif choice == "6":
                await self._option_accounts_menu()
            elif choice == "7":
                logger.info("👋 Выход...")
                break
            else:
                logger.warning("⚠️ Неверный выбор")

    async def _option_generate_and_evaluate(self):
        batch_size = self._prompt_int(f"Размер батча ({config.BATCH_SIZE}): ", config.BATCH_SIZE, minimum=1)

        batch_result = self.generate_batch(batch_size)
        usernames = batch_result["usernames"]

        if not usernames:
            logger.error("❌ Не удалось сгенерировать username")
            return

        evaluated = self.evaluate_batch(usernames)
        logger.info(f"\n📊 Лучшие из батча #{self.batch_num} ({len(evaluated)}):")
        for i, item in enumerate(evaluated[:30], 1):
            score = item.get("total_score", 0)
            generation_type = item.get("generation_type") or "-"
            logger.info(f"{i:3d}. {item['username']:6s}  score: {score:.2f}  type: {generation_type}")

    async def _option_check_availability(self):
        candidates, source = self._get_candidates_for_check()
        if not candidates:
            logger.warning(f"⚠️ Нет unchecked username с score >= {config.SCORE_THRESHOLD}")
            return

        source_text = "последний батч/текущая сессия" if source == "last_batch" else "лучшие из базы"
        logger.info(f"🎯 Кандидаты для проверки ({source_text}): {len(candidates)}")
        self._show_records("Предпросмотр кандидатов", candidates[:10])

        limit = self._prompt_int(
            f"Сколько проверить сейчас (макс. {config.MAX_TELEGRAM_CHECKS_PER_BATCH}): ",
            config.MAX_TELEGRAM_CHECKS_PER_BATCH,
            minimum=1,
        )
        if limit > config.MAX_TELEGRAM_CHECKS_PER_BATCH:
            logger.warning(f"⚠️ Лимит снижен до безопасного значения {config.MAX_TELEGRAM_CHECKS_PER_BATCH}")
            limit = config.MAX_TELEGRAM_CHECKS_PER_BATCH

        selected = candidates[:limit]
        logger.info(f"🔍 Выбрано для проверки: {', '.join(item['username'] for item in selected)}")

        if self.dry_run or self.no_telegram:
            logger.info("🧪 Preview: Telegram-запросы не выполнялись")
            return

        results = await self.check_availability_batch(selected)
        if not results:
            return

        by_username = {item["username"]: item for item in selected}
        available = [username for username, details in results.items() if details.get("available")]
        taken = [username for username, details in results.items() if not details.get("available")]

        if available:
            logger.info(f"\n✅ ДОСТУПНЫ ({len(available)}):")
            for username in available:
                score = by_username.get(username, {}).get("score") or 0
                logger.info(f"  - @{username} (score: {score:.2f})")

            for username in available:
                score = by_username.get(username, {}).get("score") or 0
                confirm = input(f"Использовать {username} (score: {score:.2f})? (y/n): ").strip().lower()
                if confirm != "y":
                    logger.info(f"⏭ @{username} пропущен: пользователь не подтвердил создание")
                    continue

                channel_id = await self.create_channel_for_username(username, username)
                if channel_id:
                    logger.info(f"✅ Username @{username} использован, канал ID: {channel_id}")
                else:
                    logger.error(f"❌ Не удалось использовать @{username}")

        if taken:
            logger.info(f"\n❌ ЗАНЯТЫ/НЕВАЛИД ({len(taken)}):")
            for username in taken[:20]:
                details = results.get(username, {})
                logger.info(f"  - @{username}: {details.get('status', 'checked_taken')} {details.get('notes', '')}")

    def _get_candidates_for_check(self) -> tuple[List[Dict], str]:
        if self.last_evaluated_usernames:
            already_checked = set(self.storage.get_all_checked_usernames())
            candidates = []
            for item in sorted(self.last_evaluated_usernames, key=lambda row: row.get("total_score", row.get("score", 0)), reverse=True):
                username = item.get("username")
                score = item.get("total_score", item.get("score", 0))
                if not utils.is_valid_username(username):
                    logger.info(f"⏭ @{username} пропущен: невалидный формат")
                    continue
                if username in already_checked:
                    logger.info(f"⏭ @{username} пропущен: уже проверялся")
                    continue
                if score < config.SCORE_THRESHOLD:
                    logger.info(f"⏭ @{username} пропущен: score {score:.2f} ниже {config.SCORE_THRESHOLD}")
                    continue

                row = dict(item)
                row["score"] = score
                row["status"] = "unchecked"
                row["batch_num"] = self.batch_num
                row["generation_type"] = row.get("generation_type") or self.last_generation_types.get(username)
                candidates.append(row)
            return candidates, "last_batch"

        last_batch = self._filter_check_candidates(self.storage.get_username_records(
            limit=None,
            min_score=config.SCORE_THRESHOLD,
            status="unchecked",
            last_batch_only=True,
            valid_only=True,
        ))
        if last_batch:
            return last_batch, "last_batch"

        database = self._filter_check_candidates(self.storage.get_username_records(
            limit=None,
            min_score=config.SCORE_THRESHOLD,
            status="unchecked",
            valid_only=True,
        ))
        return database, "database"

    def _filter_check_candidates(self, records: List[Dict], log_skips: bool = True) -> List[Dict]:
        """Оставляет только username, которые безопасно проверять в Telegram."""
        filtered = []
        invalid = []
        low_score = []
        for row in records:
            username = row.get("username")
            score = row.get("score") or 0
            if not utils.is_valid_username(username):
                invalid.append(username)
                continue
            if score < config.SCORE_THRESHOLD:
                low_score.append(username)
                continue
            filtered.append(row)

        if log_skips and invalid:
            logger.info(f"⏭ Пропущено {len(invalid)} невалидных/служебных: {', '.join(invalid[:12])}")
        if log_skips and low_score:
            logger.info(f"⏭ Пропущено {len(low_score)} с низким score: {', '.join(low_score[:12])}")

        return filtered

    async def _option_create_channel(self):
        username = utils.normalize_username_input(input("Введите username (без @): ").strip())
        title = input("Название канала (опционально): ").strip()

        if not username:
            logger.error("❌ Username пуст")
            return

        if not utils.is_telegram_username_format(username):
            logger.error(f"❌ @{username} не проходит формат Telegram username")
            return

        record = self.storage.get_username_record(username)
        if record and record.get("status") in {"checked_taken", "invalid", "used"}:
            logger.error(f"❌ @{username} пропущен: статус в базе {record.get('status')}")
            return

        score = self.storage.get_score(username)
        score_text = f"score: {score:.2f}" if score is not None else "score: нет"
        confirm = input(f"Использовать {username} ({score_text})? (y/n): ").strip().lower()
        if confirm != "y":
            logger.info("⏭ Создание отменено пользователем")
            return

        if self.dry_run or self.no_telegram:
            logger.info(f"🧪 Preview: канал для @{username} не создавался")
            return

        channel_id = await self.create_channel_for_username(username, title or username)
        if channel_id:
            logger.info(f"✅ Готово! ID канала: {channel_id}")
        else:
            logger.error("❌ Не удалось создать канал")

    async def _option_accounts_menu(self):
        while True:
            accounts = self.account_manager.list_accounts()
            print("\nАккаунты Telegram:")
            if accounts:
                for index, account in enumerate(accounts, 1):
                    cooldown = account.get("cooldown_remaining") or 0
                    cooldown_text = f", cooldown {cooldown}s" if cooldown else ""
                    active_mark = " *" if self.account_manager.active_account_id == account.get("account_id") else ""
                    print(f"{index}. {account.get('phone')} - {account.get('status')}{cooldown_text}{active_mark}")
            else:
                print("Нет добавленных мульти-аккаунтов.")

            print("\n1. Добавить аккаунт")
            print("2. Удалить аккаунт")
            print("0. Назад")
            choice = input("\nВыберите пункт: ").strip()

            if choice == "1":
                api_id = input("API ID: ").strip()
                api_hash = input("API Hash: ").strip()
                phone = input("Телефон (+79990000000): ").strip()
                try:
                    account = await self.account_manager.add_account_interactive(api_id, api_hash, phone)
                    logger.info(f"✅ Аккаунт добавлен: {account.phone}")
                except Exception as e:
                    log_error("Ошибка добавления аккаунта", e)
            elif choice == "2":
                account_id = input("Введите account_id или номер телефона для удаления: ").strip()
                normalized = utils.normalize_phone(account_id)
                target = normalized or account_id
                if self.account_manager.delete_account(target):
                    logger.info(f"✅ Аккаунт удалён: {account_id}")
                else:
                    logger.warning("⚠️ Аккаунт не найден")
            elif choice == "0":
                return
            else:
                logger.warning("⚠️ Неверный выбор")

    def _option_show_stats_menu(self):
        while True:
            print("\nСтатистика и база:")
            print("1. Общая статистика")
            print("2. Доступные username")
            print("3. Уже проверенные username")
            print("4. Использованные username")
            print("5. Топ username по score")
            print("6. Username из последнего батча")
            print("7. Не проверялись в Telegram")
            print("8. Занятые/невалидные")
            print("9. Фильтрованный просмотр")
            print("0. Назад")

            choice = input("\nВыберите пункт: ").strip()
            if choice == "1":
                self.show_overall_stats()
            elif choice == "2":
                self._show_limited_records("Доступные username для использования", status="available", valid_only=True)
            elif choice == "3":
                self._show_limited_records("Проверенные username", status="checked")
            elif choice == "4":
                self._show_limited_records("Использованные username", status="used")
            elif choice == "5":
                self._show_limited_records("Топ username по score")
            elif choice == "6":
                self._show_limited_records("Username из последнего батча", last_batch_only=True)
            elif choice == "7":
                self._show_limited_records("Не проверялись в Telegram", status="unchecked")
            elif choice == "8":
                self._show_limited_records("Занятые/невалидные", status="taken_invalid")
            elif choice == "9":
                self._option_custom_view()
            elif choice == "0":
                return
            else:
                logger.warning("⚠️ Неверный выбор")

    def show_overall_stats(self):
        stats = self.storage.get_stats()

        logger.info("\n📊 ОБЩАЯ СТАТИСТИКА:")
        logger.info(f"Всего оценено: {stats.get('total_evaluated', 0)}")
        logger.info(f"Всего проверено в Telegram: {stats.get('total_checked', 0)}")
        logger.info(f"Доступных: {stats.get('total_available', 0)}")
        logger.info(f"Занятых/невалидных: {stats.get('total_taken_invalid', 0)}")
        logger.info(f"Использованных: {stats.get('total_used', 0)}")
        logger.info(f"Непроверенных: {stats.get('total_unchecked', 0)}")
        logger.info(f"Хороших score >= {config.SCORE_THRESHOLD}: {stats.get('good_usernames', 0)}")
        logger.info(f"Средний score: {stats.get('avg_score', 0):.2f}")
        logger.info(f"Лучший score: {stats.get('best_score', 0):.2f}")
        logger.info(f"Последний batch_num: {stats.get('last_batch_num', 0)}")
        logger.info(f"Username в последнем батче: {stats.get('last_batch_count', 0)}")
        logger.info(f"Из последнего батча уже проверено: {stats.get('last_batch_checked', 0)}")
        logger.info(f"Из последнего батча доступно: {stats.get('last_batch_available', 0)}")

        if self.telegram_manager:
            logger.info(f"Каналов создано в этой сессии: {self.telegram_manager.get_created_channels_count()}")

    def _show_limited_records(self, title: str, status: str = None, last_batch_only: bool = False, valid_only: bool = False):
        limit = self._prompt_int("Сколько показать (20): ", 20, minimum=1)
        min_score = self._prompt_optional_float("Минимальный score (Enter без фильтра): ")
        records = self.storage.get_username_records(
            limit=limit,
            min_score=min_score,
            status=status,
            last_batch_only=last_batch_only,
            valid_only=valid_only,
        )
        self._show_records(title, records)

    def _option_custom_view(self):
        limit = self._prompt_int("Top N (20): ", 20, minimum=1)
        min_score = self._prompt_optional_float("Min score (Enter без фильтра): ")
        only_available = input("Только available? (y/n): ").strip().lower() == "y"
        only_unchecked = input("Только unchecked? (y/n): ").strip().lower() == "y"
        only_used = input("Только used? (y/n): ").strip().lower() == "y"
        last_batch_only = input("Только последний батч? (y/n): ").strip().lower() == "y"

        status = None
        if only_available:
            status = "available"
        elif only_unchecked:
            status = "unchecked"
        elif only_used:
            status = "used"

        records = self.storage.get_username_records(
            limit=limit,
            min_score=min_score,
            status=status,
            last_batch_only=last_batch_only,
            valid_only=only_available,
        )
        self._show_records("Фильтрованный просмотр", records)

    def _show_records(self, title: str, records: List[Dict]):
        logger.info(f"\n📋 {title}: {len(records)}")
        if not records:
            return

        logger.info("username  score  status         checked_at           scored_at            type                    channel              notes")
        for row in records:
            username = row.get("username", "")
            score = row.get("score")
            score_text = f"{score:.2f}" if isinstance(score, (int, float)) else "-"
            status = row.get("status") or "unchecked"
            checked_at = row.get("checked_at") or "-"
            scored_at = row.get("scored_at") or "-"
            generation_type = row.get("generation_type") or "-"
            channel_id = row.get("channel_id")
            channel_name = row.get("channel_name") or ""
            channel = f"{channel_id}:{channel_name}" if channel_id else "-"
            notes = (row.get("notes") or "").replace("\n", " ")[:80]
            logger.info(f"{username:8s} {score_text:>5s}  {status:13s} {checked_at!s:20s} {scored_at!s:20s} {generation_type:23s} {channel:20s} {notes}")

    def _prompt_int(self, prompt: str, default: int, minimum: int = None) -> int:
        raw = input(prompt).strip()
        try:
            value = int(raw or default)
        except ValueError:
            logger.warning(f"⚠️ Некорректное число, используется {default}")
            value = default

        if minimum is not None and value < minimum:
            logger.warning(f"⚠️ Значение повышено до минимума {minimum}")
            value = minimum

        return value

    def _prompt_optional_float(self, prompt: str) -> Optional[float]:
        raw = input(prompt).strip()
        if not raw:
            return None
        try:
            return float(raw.replace(",", "."))
        except ValueError:
            logger.warning("⚠️ Некорректный score, фильтр не применён")
            return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Telegram username generator",
        epilog="Проверка проекта: python -m compileall . && pytest -q",
    )
    parser.add_argument("--no-telegram", action="store_true", help="не подключаться к Telegram")
    parser.add_argument("--dry-run", action="store_true", help="preview-режим без Telegram-действий")
    parser.add_argument("--stats", action="store_true", help="показать общую статистику и выйти")
    parser.add_argument("--cli", action="store_true", help="run the old console menu")
    parser.add_argument("--host", default="127.0.0.1", help="web interface host")
    parser.add_argument("--port", type=int, default=8080, help="web interface port")
    parser.add_argument("--no-browser", action="store_true", help="do not open browser for web interface")
    return parser.parse_args()


async def main():
    args = parse_args()

    if not args.cli and not args.stats:
        from web_app import run_server

        run_server(args.host, args.port, open_browser=not args.no_browser)
        return

    system = UsernameGenerationSystem(
        dry_run=args.dry_run or config.TELEGRAM_DRY_RUN,
        no_telegram=args.no_telegram,
    )

    try:
        if args.stats:
            system.show_overall_stats()
            return

        await system.run_interactive_mode()

    except KeyboardInterrupt:
        logger.info("\n⚠️ Прервано пользователем")
    except Exception as e:
        log_error("Критическая ошибка", e)
    finally:
        await system.close_telegram()
        logger.info("\n✅ Завершено")


if __name__ == "__main__":
    asyncio.run(main())
