"""cao_memory — SQLite FTS5 Episodic Memory Layer.

Provides fast full-text indexed storage and recall of past sessions, architectural
decisions, bug fixes, and user preferences into wcao/memory.sqlite.
"""
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_default_db_path() -> Path:
    from run.cao_auto import find_repo_root
    root = find_repo_root(Path.cwd())
    try:
        from run.cao_lib import resolve_workspace_dir
        ws = resolve_workspace_dir(root, create=True, auto_patch=True)
    except ImportError:
        ws = root / "wgambit" if (root / "wgambit").exists() else root / "wcao"
    ws.mkdir(parents=True, exist_ok=True)
    return ws / "memory.sqlite"


def get_fleet_db_path() -> Path:
    cao_dir = Path.home() / ".cao"
    cao_dir.mkdir(parents=True, exist_ok=True)
    return cao_dir / "fleet_memory.sqlite"


def get_connection(db_path: Optional[Path] = None, fleet: bool = False) -> sqlite3.Connection:
    if fleet and db_path is None:
        path = get_fleet_db_path()
    else:
        path = db_path or get_default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS session_memory USING fts5(
                session_id,
                category,
                summary,
                details,
                file_paths,
                created_at
            )
        """)


def store_memory(
    category: str,
    summary: str,
    details: str = "",
    file_paths: str = "",
    session_id: str = "default",
    db_path: Optional[Path] = None,
    fleet: bool = False,
) -> int:
    """Store an episodic memory entry into the FTS5 database."""
    conn = get_connection(db_path, fleet=fleet)
    now_iso = datetime.now(timezone.utc).isoformat()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO session_memory(session_id, category, summary, details, file_paths, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, category, summary, details, file_paths, now_iso),
        )
        return cursor.lastrowid


STOPWORDS = {"the", "for", "to", "in", "and", "a", "an", "is", "of", "on", "with", "this", "that", "it"}


def _sanitize_fts_query(query: str) -> str:
    # Remove characters that can break SQLite FTS syntax
    cleaned = re.sub(r'[^\w\s]', ' ', query)
    tokens = [t.strip().lower() for t in cleaned.split() if t.strip().lower() not in STOPWORDS and len(t.strip()) > 1]
    if not tokens:
        tokens = [t.strip().lower() for t in cleaned.split() if t.strip()]
    if not tokens:
        return ""
    # Use OR disjunction so relevant keyword matches are ranked by BM25
    return " OR ".join(f'"{t}"*' for t in tokens[:10])


def query_memory(
    query_text: str,
    category: Optional[str] = None,
    limit: int = 10,
    db_path: Optional[Path] = None,
    fleet: bool = False,
) -> List[Dict[str, Any]]:
    """Query memories using FTS5 match."""
    conn = get_connection(db_path, fleet=fleet)
    fts_query = _sanitize_fts_query(query_text)
    if not fts_query:
        return []

    try:
        if category:
            cursor = conn.execute(
                """
                SELECT rowid, session_id, category, summary, details, file_paths, created_at, rank
                FROM session_memory
                WHERE session_memory MATCH ? AND category = ?
                ORDER BY rank
                LIMIT ?
                """,
                (fts_query, category, limit),
            )
        else:
            cursor = conn.execute(
                """
                SELECT rowid, session_id, category, summary, details, file_paths, created_at, rank
                FROM session_memory
                WHERE session_memory MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (fts_query, limit),
            )
        return [dict(r) for r in cursor.fetchall()]
    except sqlite3.OperationalError:
        # Fallback to simple LIKE if FTS expression encounters an error
        like_term = f"%{query_text}%"
        if category:
            cursor = conn.execute(
                """
                SELECT rowid, session_id, category, summary, details, file_paths, created_at, 0 as rank
                FROM session_memory
                WHERE (summary LIKE ? OR details LIKE ?) AND category = ?
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (like_term, like_term, category, limit),
            )
        else:
            cursor = conn.execute(
                """
                SELECT rowid, session_id, category, summary, details, file_paths, created_at, 0 as rank
                FROM session_memory
                WHERE summary LIKE ? OR details LIKE ?
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (like_term, like_term, limit),
            )
        return [dict(r) for r in cursor.fetchall()]


def list_memories(
    limit: int = 20,
    db_path: Optional[Path] = None,
    fleet: bool = False,
) -> List[Dict[str, Any]]:
    """List recent memories."""
    conn = get_connection(db_path, fleet=fleet)
    cursor = conn.execute(
        """
        SELECT rowid, session_id, category, summary, details, file_paths, created_at, 0 as rank
        FROM session_memory
        ORDER BY rowid DESC
        LIMIT ?
        """,
        (limit,),
    )
    return [dict(r) for r in cursor.fetchall()]


def prune_memories(
    max_age_days: int = 30,
    keep_min: int = 50,
    db_path: Optional[Path] = None,
    fleet: bool = False,
) -> int:
    """Prune episodic memories older than max_age_days while retaining at least keep_min recent entries.

    Returns the number of pruned entries.
    """
    conn = get_connection(db_path, fleet=fleet)
    rows = conn.execute(
        """
        SELECT rowid, created_at
        FROM session_memory
        ORDER BY created_at DESC, rowid DESC
        """
    ).fetchall()

    if len(rows) <= max(0, keep_min):
        conn.close()
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    candidates = rows[max(0, keep_min):]
    rowids_to_delete: List[int] = []

    for row in candidates:
        raw_ts = row["created_at"] or ""
        try:
            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt < cutoff:
                rowids_to_delete.append(int(row["rowid"]))
        except Exception:
            continue

    if rowids_to_delete:
        placeholders = ",".join("?" for _ in rowids_to_delete)
        with conn:
            conn.execute(
                f"DELETE FROM session_memory WHERE rowid IN ({placeholders})",
                rowids_to_delete,
            )

    conn.close()
    return len(rowids_to_delete)


def vacuum_memory(
    db_path: Optional[Path] = None,
    fleet: bool = False,
) -> None:
    """Optimize FTS5 index and VACUUM the SQLite memory database."""
    conn = get_connection(db_path, fleet=fleet)
    with conn:
        conn.execute("INSERT INTO session_memory(session_memory) VALUES('optimize')")
    conn.execute("VACUUM")
    conn.close()
