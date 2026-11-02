"""SQLite persistence for mistake records."""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATA = Path(os.environ.get("IELTS_DATA_DIR", Path(__file__).parent / "data"))


@contextmanager
def connect():
    DATA.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATA / "learning.db")
    db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE IF NOT EXISTS mistakes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      passage TEXT NOT NULL DEFAULT '',
      question TEXT NOT NULL,
      learner TEXT NOT NULL DEFAULT '',
      accepted TEXT NOT NULL,
      choices TEXT NOT NULL DEFAULT '[]',
      multiple INTEGER NOT NULL DEFAULT 0,
      correct INTEGER NOT NULL DEFAULT 0,
      evidence TEXT NOT NULL DEFAULT '',
      reasoning TEXT NOT NULL DEFAULT '',
      notes TEXT NOT NULL DEFAULT '',
      cause TEXT,
      created TEXT DEFAULT CURRENT_TIMESTAMP,
      updated TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE INDEX IF NOT EXISTS idx_mistakes_cause ON mistakes(cause);
    """)
    try:
        with db:
            yield db
    finally:
        db.close()


def _row(record):
    item = dict(record)
    item["accepted"] = json.loads(item["accepted"])
    item["choices"] = json.loads(item["choices"])
    item["multiple"] = bool(item["multiple"])
    item["correct"] = bool(item["correct"])
    return item


def add(record):
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO mistakes(passage,question,learner,accepted,choices,multiple,"
            "correct,evidence,reasoning,notes,cause) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (record["passage"], record["question"], record["learner"],
             json.dumps(record["accepted"], ensure_ascii=False),
             json.dumps(record["choices"], ensure_ascii=False),
             int(record["multiple"]), int(record["correct"]), record["evidence"],
             record["reasoning"], record["notes"], record.get("cause")))
        return cursor.lastrowid


def records(include_correct=True):
    sql = "SELECT * FROM mistakes" + ("" if include_correct else " WHERE correct=0")
    with connect() as db:
        return [_row(r) for r in db.execute(sql + " ORDER BY id DESC")]


def get(mistake_id):
    with connect() as db:
        row = db.execute("SELECT * FROM mistakes WHERE id=?", (mistake_id,)).fetchone()
    return _row(row) if row else None


def pending():
    """待确认记录：已经保存，但学习者还没确认原因。"""
    with connect() as db:
        return [_row(r) for r in db.execute(
            "SELECT * FROM mistakes WHERE cause IS NULL ORDER BY id DESC")]


def confirm(mistake_id, cause):
    """确认一条记录的原因。"""
    with connect() as db:
        db.execute("UPDATE mistakes SET cause=?, updated=CURRENT_TIMESTAMP WHERE id=?",
                   (cause, mistake_id))


def confirm_many(ids, cause):
    """批量确认原因，返回实际更新的条数。"""
    ids = [int(i) for i in ids]
    if not ids:
        return 0
    marks = ",".join("?" * len(ids))
    with connect() as db:
        cursor = db.execute(
            "UPDATE mistakes SET cause=?, updated=CURRENT_TIMESTAMP WHERE id IN (%s)" % marks,
            [cause] + ids)
        return cursor.rowcount


def reset(mistake_id):
    """把一条记录退回待确认状态。"""
    with connect() as db:
        db.execute("UPDATE mistakes SET cause=NULL, updated=CURRENT_TIMESTAMP WHERE id=?",
                   (mistake_id,))


def update(mistake_id, **fields):
    """更新证据、思路、笔记等文本字段。"""
    allowed = {"passage", "evidence", "reasoning", "notes", "learner"}
    patch = {k: v for k, v in fields.items() if k in allowed}
    if not patch:
        return
    sets = ", ".join("%s=?" % k for k in patch)
    with connect() as db:
        db.execute("UPDATE mistakes SET %s, updated=CURRENT_TIMESTAMP WHERE id=?" % sets,
                   list(patch.values()) + [mistake_id])


def delete(mistake_id):
    with connect() as db:
        db.execute("DELETE FROM mistakes WHERE id=?", (mistake_id,))
