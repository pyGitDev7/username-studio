"""
Система хранения данных (SQLite)
"""
import sqlite3
from typing import List, Dict, Optional

import config
import utils
from logger import logger


class UsernameStorage:
    """Управляет базой данных username."""

    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self._init_database()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Инициализирует таблицы и выполняет безопасные миграции."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS checked_usernames (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        available BOOLEAN NOT NULL,
                        score REAL,
                        generation_type TEXT,
                        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS used_usernames (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        channel_id INTEGER,
                        channel_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        readability REAL,
                        brandability REAL,
                        meaning REAL,
                        rarity REAL,
                        total_score REAL,
                        scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS batches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        batch_num INTEGER UNIQUE NOT NULL,
                        total_usernames INTEGER,
                        available_count INTEGER DEFAULT 0,
                        generation_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS batch_usernames (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        batch_num INTEGER NOT NULL,
                        username TEXT NOT NULL,
                        generation_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(batch_num, username)
                    )
                """)

                self._ensure_column(cursor, "checked_usernames", "status", "TEXT")
                self._ensure_column(cursor, "checked_usernames", "batch_num", "INTEGER")
                self._ensure_column(cursor, "scores", "generation_type", "TEXT")
                self._ensure_column(cursor, "scores", "batch_num", "INTEGER")

                cursor.execute("""
                    UPDATE checked_usernames
                    SET status = CASE
                        WHEN available = 1 THEN 'available'
                        WHEN status IS NULL OR status = '' THEN 'checked_taken'
                        ELSE status
                    END
                """)

                cursor.execute("CREATE INDEX IF NOT EXISTS idx_checked_username ON checked_usernames(username)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_checked_status ON checked_usernames(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_used_username ON used_usernames(username)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_username ON scores(username)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_total_score ON scores(total_score)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_batch ON scores(batch_num)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_batches_num ON batches(batch_num)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_batch_usernames_batch ON batch_usernames(batch_num)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_batch_usernames_username ON batch_usernames(username)")

                conn.commit()
                logger.debug("✅ База данных инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise

    def _ensure_column(self, cursor: sqlite3.Cursor, table: str, column: str, definition: str):
        cursor.execute(f"PRAGMA table_info({table})")
        existing = {row["name"] for row in cursor.fetchall()}
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def add_checked_username(
        self,
        username: str,
        available: bool,
        score: float = None,
        generation_type: str = None,
        notes: str = None,
        status: str = None,
        batch_num: int = None,
    ) -> bool:
        """Добавляет или обновляет результат Telegram-проверки."""
        status = status or ("available" if available else "checked_taken")
        if status in {"invalid", "checked_taken", "purchase_only", "error"}:
            available = False

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO checked_usernames
                    (username, available, score, generation_type, notes, status, batch_num)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(username) DO UPDATE SET
                        available = excluded.available,
                        score = COALESCE(excluded.score, checked_usernames.score),
                        generation_type = COALESCE(excluded.generation_type, checked_usernames.generation_type),
                        checked_at = CURRENT_TIMESTAMP,
                        notes = excluded.notes,
                        status = excluded.status,
                        batch_num = COALESCE(excluded.batch_num, checked_usernames.batch_num)
                """, (username, int(bool(available)), score, generation_type, notes, status, batch_num))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка добавления username: {e}")
            return False

    def add_used_username(
        self,
        username: str,
        channel_id: int = None,
        channel_name: str = None,
        notes: str = None,
    ) -> bool:
        """Добавляет использованный username и помечает его как used."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO used_usernames
                    (username, channel_id, channel_name, notes)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(username) DO UPDATE SET
                        channel_id = COALESCE(excluded.channel_id, used_usernames.channel_id),
                        channel_name = COALESCE(excluded.channel_name, used_usernames.channel_name),
                        notes = COALESCE(excluded.notes, used_usernames.notes)
                """, (username, channel_id, channel_name, notes))
                cursor.execute("""
                    INSERT INTO checked_usernames
                    (username, available, score, status, notes)
                    VALUES (?, 1, (SELECT total_score FROM scores WHERE username = ? ORDER BY id DESC LIMIT 1), 'used', ?)
                    ON CONFLICT(username) DO UPDATE SET
                        available = 1,
                        score = COALESCE(checked_usernames.score, excluded.score),
                        status = 'used',
                        notes = COALESCE(excluded.notes, checked_usernames.notes)
                """, (username, username, notes))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления используемого username: {e}")
            return False

    def get_all_used_usernames(self) -> List[str]:
        try:
            with self._connect() as conn:
                return [row["username"] for row in conn.execute("SELECT username FROM used_usernames")]
        except Exception as e:
            logger.error(f"Ошибка получения использованных username: {e}")
            return []

    def get_all_checked_usernames(self) -> List[str]:
        try:
            with self._connect() as conn:
                return [row["username"] for row in conn.execute("SELECT username FROM checked_usernames")]
        except Exception as e:
            logger.error(f"Ошибка получения проверенных username: {e}")
            return []

    def get_available_by_score(self, limit: int = 20) -> List[Dict]:
        return self.get_username_records(limit=limit, status="available", valid_only=True)

    def get_top_scored(self, limit: int = 20) -> List[Dict]:
        return self.get_username_records(limit=limit)

    def get_all_scored(self, min_score: float = None) -> List[Dict]:
        return self.get_username_records(limit=None, min_score=min_score)

    def is_username_checked(self, username: str) -> bool:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT 1 FROM checked_usernames WHERE username = ?",
                    (username,),
                ).fetchone()
                return row is not None
        except Exception as e:
            logger.error(f"Ошибка проверки username: {e}")
            return False

    def is_username_used(self, username: str) -> bool:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT 1 FROM used_usernames WHERE username = ?",
                    (username,),
                ).fetchone()
                return row is not None
        except Exception as e:
            logger.error(f"Ошибка проверки используемого username: {e}")
            return False

    def save_scores(
        self,
        username: str,
        readability: float,
        brandability: float,
        meaning: float,
        rarity: float,
        total_score: float,
        generation_type: str = None,
        batch_num: int = None,
    ) -> bool:
        """Сохраняет последнюю оценку username без дублей в scores."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM scores WHERE username = ?", (username,))
                cursor.execute("""
                    INSERT INTO scores
                    (username, readability, brandability, meaning, rarity, total_score, generation_type, batch_num)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (username, readability, brandability, meaning, rarity, total_score, generation_type, batch_num))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения оценок: {e}")
            return False

    def get_score(self, username: str) -> Optional[float]:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT total_score FROM scores WHERE username = ? ORDER BY id DESC LIMIT 1",
                    (username,),
                ).fetchone()
                return row["total_score"] if row else None
        except Exception as e:
            logger.error(f"Ошибка получения оценки: {e}")
            return None

    def add_batch(self, batch_num: int, total_usernames: int, generation_type: str = None) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO batches
                    (batch_num, total_usernames, generation_type)
                    VALUES (?, ?, ?)
                    ON CONFLICT(batch_num) DO UPDATE SET
                        total_usernames = excluded.total_usernames,
                        generation_type = COALESCE(excluded.generation_type, batches.generation_type)
                """, (batch_num, total_usernames, generation_type))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления информации о батче: {e}")
            return False

    def add_batch_usernames(self, batch_num: int, usernames: List[str], generation_types: Dict[str, str] = None) -> int:
        """Сохраняет состав батча для статистики и повторного просмотра."""
        generation_types = generation_types or {}
        rows = [(batch_num, username, generation_types.get(username)) for username in usernames]
        if not rows:
            return 0

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.executemany("""
                    INSERT OR IGNORE INTO batch_usernames
                    (batch_num, username, generation_type)
                    VALUES (?, ?, ?)
                """, rows)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Ошибка сохранения username батча: {e}")
            return 0

    def get_last_batch_num(self) -> int:
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT COALESCE(MAX(batch_num), 0) AS batch_num FROM batches").fetchone()
                return int(row["batch_num"])
        except Exception as e:
            logger.error(f"Ошибка получения последнего батча: {e}")
            return 0

    def get_check_candidates(self, min_score: float, limit: int = None) -> tuple[List[Dict], str]:
        """Берёт свежий последний батч, а если там нечего проверять - лучшие из базы."""
        last_batch = self.get_username_records(
            limit=limit,
            min_score=min_score,
            status="unchecked",
            last_batch_only=True,
            valid_only=True,
        )
        if last_batch:
            return last_batch, "last_batch"

        return self.get_username_records(
            limit=limit,
            min_score=min_score,
            status="unchecked",
            valid_only=True,
        ), "database"

    def get_username_records(
        self,
        limit: int = 20,
        min_score: float = None,
        status: str = None,
        last_batch_only: bool = False,
        valid_only: bool = False,
    ) -> List[Dict]:
        """Универсальный просмотр username с фильтрами по статусу, score и батчу."""
        params = []
        conditions = []

        if last_batch_only:
            last_batch_num = self.get_last_batch_num()
            conditions.append("batch_num = ?")
            params.append(last_batch_num)

        if min_score is not None:
            conditions.append("score >= ?")
            params.append(min_score)

        if status:
            if status == "checked":
                conditions.append("status IN ('available', 'checked_taken', 'invalid')")
            elif status == "taken_invalid":
                conditions.append("status IN ('checked_taken', 'invalid')")
            else:
                conditions.append("status = ?")
                params.append(status)

        where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        limit_sql = ""
        if limit is not None and not valid_only:
            limit_sql = "LIMIT ?"
            params.append(max(1, int(limit)))

        query = f"""
            WITH latest_scores AS (
                SELECT s.*
                FROM scores s
                INNER JOIN (
                    SELECT username, MAX(id) AS max_id
                    FROM scores
                    GROUP BY username
                ) latest ON s.username = latest.username AND s.id = latest.max_id
            ),
            latest_batch AS (
                SELECT bu.*
                FROM batch_usernames bu
                INNER JOIN (
                    SELECT username, MAX(batch_num) AS max_batch
                    FROM batch_usernames
                    GROUP BY username
                ) latest ON bu.username = latest.username AND bu.batch_num = latest.max_batch
            ),
            all_names AS (
                SELECT username FROM latest_scores
                UNION
                SELECT username FROM checked_usernames
                UNION
                SELECT username FROM used_usernames
                UNION
                SELECT username FROM batch_usernames
            ),
            records AS (
                SELECT
                    n.username,
                    s.total_score AS score,
                    s.readability,
                    s.brandability,
                    s.meaning,
                    s.rarity,
                    s.scored_at,
                    c.checked_at,
                    COALESCE(lb.generation_type, s.generation_type, c.generation_type) AS generation_type,
                    lb.batch_num,
                    u.channel_id,
                    u.channel_name,
                    COALESCE(u.notes, c.notes) AS notes,
                    CASE
                        WHEN u.username IS NOT NULL THEN 'used'
                        WHEN c.username IS NULL THEN 'unchecked'
                        WHEN c.status = 'invalid' THEN 'invalid'
                        WHEN c.available = 1 THEN 'available'
                        ELSE 'checked_taken'
                    END AS status
                FROM all_names n
                LEFT JOIN latest_scores s ON s.username = n.username
                LEFT JOIN latest_batch lb ON lb.username = n.username
                LEFT JOIN checked_usernames c ON c.username = n.username
                LEFT JOIN used_usernames u ON u.username = n.username
            )
            SELECT *
            FROM records
            {where_sql}
            ORDER BY score IS NULL ASC, score DESC, username ASC
            {limit_sql}
        """

        try:
            with self._connect() as conn:
                records = [dict(row) for row in conn.execute(query, params).fetchall()]
                if valid_only:
                    records = [
                        row for row in records
                        if utils.is_valid_username(row.get("username", ""))
                    ]
                    if limit is not None:
                        records = records[:max(1, int(limit))]
                return records
        except Exception as e:
            logger.error(f"Ошибка получения username: {e}")
            return []

    def get_username_record(self, username: str) -> Optional[Dict]:
        """Возвращает сводную запись по одному username."""
        username = (username or "").strip().lower()
        if not username:
            return None

        try:
            for row in self.get_username_records(limit=None):
                if row.get("username") == username:
                    return row
        except Exception as e:
            logger.error(f"Ошибка получения username @{username}: {e}")

        return None

    def get_stats(self) -> Dict:
        """Получает расширенную статистику по username."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                total_evaluated = cursor.execute("SELECT COUNT(DISTINCT username) AS c FROM scores").fetchone()["c"]
                total_checked = cursor.execute("SELECT COUNT(*) AS c FROM checked_usernames").fetchone()["c"]
                total_available = len(self.get_username_records(
                    limit=None,
                    status="available",
                    valid_only=True,
                ))
                total_taken_invalid = cursor.execute("""
                    SELECT COUNT(*) AS c
                    FROM checked_usernames
                    WHERE available = 0 OR status IN ('invalid', 'checked_taken', 'purchase_only', 'error')
                """).fetchone()["c"]
                total_used = cursor.execute("SELECT COUNT(*) AS c FROM used_usernames").fetchone()["c"]
                total_batches = cursor.execute("SELECT COUNT(*) AS c FROM batches").fetchone()["c"]

                total_unchecked = cursor.execute("""
                    WITH latest_scores AS (
                        SELECT username
                        FROM scores
                        GROUP BY username
                    )
                    SELECT COUNT(*) AS c
                    FROM latest_scores s
                    LEFT JOIN checked_usernames c ON c.username = s.username
                    LEFT JOIN used_usernames u ON u.username = s.username
                    WHERE c.username IS NULL AND u.username IS NULL
                """).fetchone()["c"]

                good_usernames = cursor.execute(
                    "SELECT COUNT(DISTINCT username) AS c FROM scores WHERE total_score >= ?",
                    (config.SCORE_THRESHOLD,),
                ).fetchone()["c"]

                score_row = cursor.execute("""
                    WITH latest_scores AS (
                        SELECT s.*
                        FROM scores s
                        INNER JOIN (
                            SELECT username, MAX(id) AS max_id
                            FROM scores
                            GROUP BY username
                        ) latest ON s.username = latest.username AND s.id = latest.max_id
                    )
                    SELECT AVG(total_score) AS avg_score, MAX(total_score) AS best_score
                    FROM latest_scores
                """).fetchone()

                last_batch_num = self.get_last_batch_num()
                last_batch_count = cursor.execute(
                    "SELECT COUNT(*) AS c FROM batch_usernames WHERE batch_num = ?",
                    (last_batch_num,),
                ).fetchone()["c"] if last_batch_num else 0
                last_batch_checked = cursor.execute("""
                    SELECT COUNT(*) AS c
                    FROM batch_usernames bu
                    INNER JOIN checked_usernames c ON c.username = bu.username
                    WHERE bu.batch_num = ?
                """, (last_batch_num,)).fetchone()["c"] if last_batch_num else 0
                last_batch_available = len(self.get_username_records(
                    limit=None,
                    status="available",
                    last_batch_only=True,
                    valid_only=True,
                )) if last_batch_num else 0

                return {
                    "total_evaluated": total_evaluated,
                    "total_checked": total_checked,
                    "total_available": total_available,
                    "total_taken_invalid": total_taken_invalid,
                    "total_used": total_used,
                    "total_unchecked": total_unchecked,
                    "total_batches": total_batches,
                    "good_usernames": good_usernames,
                    "avg_score": score_row["avg_score"] or 0,
                    "best_score": score_row["best_score"] or 0,
                    "last_batch_num": last_batch_num,
                    "last_batch_count": last_batch_count,
                    "last_batch_checked": last_batch_checked,
                    "last_batch_available": last_batch_available,
                }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
