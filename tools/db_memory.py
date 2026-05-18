"""
Database Memory - SQLite-based persistent memory system
"""

import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class DatabaseMemory:
    """SQLite-based persistent memory for research findings"""

    def __init__(self, db_path: str = "database/memory.db"):
        """
        Initialize database memory

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.initialize_db()

    def initialize_db(self) -> None:
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Memory entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT UNIQUE NOT NULL,
                session_id TEXT NOT NULL,
                task_id TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                category TEXT,
                status TEXT,
                type TEXT,
                created_at REAL,
                updated_at REAL,
                accessed_count INTEGER DEFAULT 0
            )
        ''')

        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                query TEXT,
                created_at REAL,
                completed_at REAL,
                status TEXT,
                results_summary TEXT
            )
        ''')

        # Query cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT,
                results TEXT,
                created_at REAL,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL
            )
        ''')

        # Indices for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON memory_entries(session_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_task_id 
            ON memory_entries(task_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category 
            ON memory_entries(category)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON memory_entries(created_at)
        ''')

        self.conn.commit()

    def insert(self, memory_entry: Dict[str, Any]) -> int:
        """
        Insert memory entry

        Args:
            memory_entry: Dictionary with entry data

        Returns:
            Row ID of inserted entry
        """
        cursor = self.conn.cursor()

        entry_id = memory_entry.get('entry_id', f"mem_{int(time.time()*1000)}")
        timestamp = time.time()

        cursor.execute('''
            INSERT OR REPLACE INTO memory_entries
            (entry_id, session_id, task_id, content, metadata, category, status, type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry_id,
            memory_entry.get('session_id'),
            memory_entry.get('task_id'),
            memory_entry.get('content', ''),
            json.dumps(memory_entry.get('metadata', {})),
            memory_entry.get('category', 'general'),
            memory_entry.get('status', 'active'),
            memory_entry.get('type', 'entry'),
            timestamp,
            timestamp
        ))

        self.conn.commit()
        return cursor.lastrowid

    def query_by_session(
        self,
        session_id: str,
        limit: int = 100,
        order_by: str = "created_at DESC"
    ) -> List[Dict[str, Any]]:
        """
        Query memory entries by session

        Args:
            session_id: Session identifier
            limit: Maximum results to return
            order_by: ORDER BY clause

        Returns:
            List of memory entries
        """
        cursor = self.conn.cursor()

        cursor.execute(f'''
            SELECT * FROM memory_entries 
            WHERE session_id = ? AND status = 'active'
            ORDER BY {order_by}
            LIMIT ?
        ''', (session_id, limit))

        rows = cursor.fetchall()
        return self._rows_to_dicts(rows)

    def query_by_task(
        self,
        task_id: str,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query memory entries by task"""
        cursor = self.conn.cursor()

        if session_id:
            cursor.execute('''
                SELECT * FROM memory_entries 
                WHERE task_id = ? AND session_id = ? AND status = 'active'
                ORDER BY created_at DESC
            ''', (task_id, session_id))
        else:
            cursor.execute('''
                SELECT * FROM memory_entries 
                WHERE task_id = ? AND status = 'active'
                ORDER BY created_at DESC
            ''', (task_id,))

        rows = cursor.fetchall()
        return self._rows_to_dicts(rows)

    def search_by_category(
        self,
        category: str,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search memory by category"""
        cursor = self.conn.cursor()

        if session_id:
            cursor.execute('''
                SELECT * FROM memory_entries 
                WHERE category = ? AND session_id = ? AND status = 'active'
                ORDER BY accessed_count DESC, created_at DESC
                LIMIT ?
            ''', (category, session_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM memory_entries 
                WHERE category = ? AND status = 'active'
                ORDER BY accessed_count DESC, created_at DESC
                LIMIT ?
            ''', (category, limit))

        rows = cursor.fetchall()
        return self._rows_to_dicts(rows)

    def get_recent(
        self,
        session_id: str,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent memory entries from last N hours"""
        cursor = self.conn.cursor()

        cutoff_time = time.time() - (hours * 3600)

        cursor.execute('''
            SELECT * FROM memory_entries 
            WHERE session_id = ? AND status = 'active' AND created_at > ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (session_id, cutoff_time, limit))

        rows = cursor.fetchall()
        return self._rows_to_dicts(rows)

    def update(
        self,
        entry_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update memory entry"""
        cursor = self.conn.cursor()

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys() if k != 'entry_id'])
        values = [v for k, v in updates.items() if k != 'entry_id']
        values.append(entry_id)

        if set_clause:
            set_clause += ", updated_at = ?"
            values.insert(-1, time.time())

            cursor.execute(
                f'UPDATE memory_entries SET {set_clause} WHERE entry_id = ?',
                values
            )
            self.conn.commit()
            return cursor.rowcount > 0

        return False

    def delete(self, entry_id: str) -> bool:
        """Soft delete memory entry"""
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE memory_entries 
            SET status = 'deleted', updated_at = ?
            WHERE entry_id = ?
        ''', (time.time(), entry_id))

        self.conn.commit()
        return cursor.rowcount > 0

    def create_session(
        self,
        session_id: str,
        query: str
    ) -> None:
        """Create new research session"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO sessions
            (session_id, query, created_at, status)
            VALUES (?, ?, ?, ?)
        ''', (session_id, query, time.time(), 'in_progress'))

        self.conn.commit()

    def close_session(
        self,
        session_id: str,
        results_summary: str
    ) -> None:
        """Close research session"""
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE sessions 
            SET completed_at = ?, status = ?, results_summary = ?
            WHERE session_id = ?
        ''', (time.time(), 'completed', results_summary, session_id))

        self.conn.commit()

    def cache_query_results(
        self,
        query_hash: str,
        query: str,
        results: Dict[str, Any]
    ) -> None:
        """Cache query results for reuse"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO query_cache
            (query_hash, query, results, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            query_hash,
            query,
            json.dumps(results),
            time.time(),
            time.time()
        ))

        self.conn.commit()

    def get_cached_results(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached query results"""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT results FROM query_cache WHERE query_hash = ?
        ''', (query_hash,))

        row = cursor.fetchone()
        if row:
            cursor.execute('''
                UPDATE query_cache 
                SET access_count = access_count + 1, last_accessed = ?
                WHERE query_hash = ?
            ''', (time.time(), query_hash))
            self.conn.commit()

            return json.loads(row['results'])

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM memory_entries WHERE status = "active"')
        total_entries = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM sessions WHERE status = "completed"')
        completed_sessions = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM query_cache')
        cached_queries = cursor.fetchone()['count']

        return {
            'total_entries': total_entries,
            'completed_sessions': completed_sessions,
            'cached_queries': cached_queries
        }

    def cleanup_old_entries(self, days: int = 30) -> int:
        """Remove entries older than N days"""
        cursor = self.conn.cursor()

        cutoff_time = time.time() - (days * 86400)

        cursor.execute('''
            DELETE FROM memory_entries 
            WHERE created_at < ? AND status = 'deleted'
        ''', (cutoff_time,))

        self.conn.commit()
        return cursor.rowcount

    @staticmethod
    def _rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        """Convert sqlite3.Row objects to dictionaries"""
        return [dict(row) for row in rows]

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Ensure connection is closed on cleanup"""
        self.close()
