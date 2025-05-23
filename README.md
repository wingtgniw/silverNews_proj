# silverNews_proj
과제 제출 버전

---

### DB

* newsletters table
** id INTEGER PRIMARY KEY AUTOINCREMENT,
** user_id INTEGER NOT NULL,
** title TEXT NOT NULL,
** content TEXT NOT NULL,
** crawled_keywords TEXT,
** crawled_summary TEXT,
** created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
** updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP