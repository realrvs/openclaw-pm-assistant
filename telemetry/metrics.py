import sqlite3
import json
from pathlib import Path
from datetime import datetime
import time

DB_PATH = Path.home() / '.openclaw/workspace/telemetry/metrics.db'

class MetricsCollector:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()
    
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                project TEXT NOT NULL,
                action TEXT NOT NULL,
                jira_latency_ms INTEGER,
                llm_latency_ms INTEGER,
                tokens_used INTEGER,
                status_code TEXT,
                metadata TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_project ON metrics(project)')
        conn.commit()
        conn.close()
    
    def record_call(self, project: str, action: str, jira_latency: int = 0, 
                    llm_latency: int = 0, tokens: int = 0, status: str = "SUCCESS", 
                    metadata: dict = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO metrics (project, action, jira_latency_ms, llm_latency_ms, 
                                 tokens_used, status_code, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project, action, jira_latency, llm_latency, tokens, status, 
              json.dumps(metadata) if metadata else None))
        conn.commit()
        conn.close()
    
    def get_metrics(self, hours: int = 24):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, project, action, jira_latency_ms, llm_latency_ms, 
                   tokens_used, status_code
            FROM metrics
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        ''', (hours,))
        data = cursor.fetchall()
        conn.close()
        return data

if __name__ == "__main__":
    m = MetricsCollector()
    m.record_call("RUS", "test", 150, 200, 45, "SUCCESS")
    print("✅ Тестовая метрика записана")
    print("📊 Последние записи:")
    for row in m.get_metrics(1):
        print(row)
