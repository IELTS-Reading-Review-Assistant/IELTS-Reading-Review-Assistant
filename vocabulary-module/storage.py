import json
import os
import sqlite3
from contextlib import contextmanager, closing
from pathlib import Path

DATA = Path(os.environ.get('IELTS_DATA_DIR', Path(__file__).parent / 'data'))


@contextmanager
def connect():
    DATA.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATA / 'learning.db')
    db.row_factory = sqlite3.Row
    db.executescript('''
    CREATE TABLE IF NOT EXISTS words (
      word TEXT PRIMARY KEY, meaning TEXT NOT NULL DEFAULT '',
      mastered INTEGER NOT NULL DEFAULT 0, updated TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS sources (
      word TEXT NOT NULL, passage TEXT NOT NULL, sentences TEXT NOT NULL,
      PRIMARY KEY(word, passage));
    CREATE TABLE IF NOT EXISTS passages (
      text TEXT PRIMARY KEY, updated TEXT DEFAULT CURRENT_TIMESTAMP);
    ''')
    try:
        with db:
            yield db
    finally:
        db.close()


def wordbook():
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT * FROM words ORDER BY updated DESC,word')]


def save_word(item, meaning, passage, mastered=False):
    with connect() as db:
        db.execute('INSERT OR IGNORE INTO words(word,meaning,mastered) VALUES(?,?,?)',
                   (item['word'], meaning, int(mastered)))
        if mastered:
            db.execute('UPDATE words SET mastered=1 WHERE word=?', (item['word'],))
        db.execute('INSERT OR REPLACE INTO sources VALUES(?,?,?)',
                   (item['word'], passage, json.dumps(item['sentences'], ensure_ascii=False)))


def update_word(word, meaning, mastered):
    if len(meaning) > 2000:
        raise ValueError('个人释义不能超过 2,000 个字符。')
    with connect() as db:
        db.execute('UPDATE words SET meaning=?, mastered=?, updated=CURRENT_TIMESTAMP WHERE word=?',
                   (meaning, int(mastered), word))


def sources(word):
    with connect() as db:
        return [json.loads(r[0]) for r in db.execute(
            'SELECT sentences FROM sources WHERE word=?', (word,))]


def save_passage(text):
    with connect() as db:
        db.execute('INSERT OR REPLACE INTO passages(text) VALUES(?)', (text,))


def passages():
    with connect() as db:
        return [r[0] for r in db.execute('SELECT text FROM passages ORDER BY updated DESC')]


def lookup(word):
    path = Path(__file__).parent / 'data' / 'dictionary.db'
    if not path.exists():
        raise FileNotFoundError('本地词典尚未安装，请先运行 setup.ps1。')
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        row = db.execute('SELECT translation FROM dictionary WHERE word=?',
                         (word.lower(),)).fetchone()
    return row[0].replace('\\n', '\n') if row and row[0] else '暂无释义'
