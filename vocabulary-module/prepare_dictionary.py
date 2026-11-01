"""Import ECDICT CSV into an indexed local database."""
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
source = ROOT / 'data/ecdict.csv'
target = ROOT / 'data/dictionary.build.db'
if target.exists():
    target.unlink()
with sqlite3.connect(target) as db:
    db.execute('CREATE TABLE dictionary(word TEXT PRIMARY KEY, translation TEXT NOT NULL)')
    with source.open(encoding='utf-8-sig', newline='') as handle:
        db.executemany('INSERT OR REPLACE INTO dictionary VALUES(?,?)',
                       ((row['word'].lower(), row['translation'])
                        for row in csv.DictReader(handle) if row['word']))
    count = db.execute('SELECT COUNT(*) FROM dictionary').fetchone()[0]
db.close()
target.replace(ROOT / 'data/dictionary.db')
(ROOT / 'data/dictionary_source.json').write_text(json.dumps({
    'source': 'https://github.com/skywind3000/ECDICT', 'file': 'ecdict.csv',
    'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'entries': count,
    'license': 'MIT; see third_party/ECDICT-LICENSE.txt'
}, indent=2), encoding='utf-8')
print(f'Imported {count:,} dictionary entries.')
