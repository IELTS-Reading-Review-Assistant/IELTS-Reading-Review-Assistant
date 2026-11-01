"""Rule-based vocabulary services, independent from the user interface."""
import re
from collections import Counter
from pathlib import Path

TOKEN = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
BASIC_PATH = Path(__file__).parent / 'data' / 'basic_words.txt'


def recommend(text, mastered=(), limit=20):
    if not text.strip():
        raise ValueError('请先粘贴英文文章。')
    tokens = TOKEN.findall(text)
    if len(text) > 50000 or len(tokens) > 5000:
        raise ValueError('文章不能超过 50,000 个字符或 5,000 个英文词。')
    if not tokens:
        raise ValueError('没有找到英文单词，请检查输入。')
    basic = {w.strip().lower() for w in BASIC_PATH.read_text(encoding='utf-8').splitlines()
             if w.strip() and not w.startswith('#')}
    excluded = basic | {w.lower() for w in mastered}
    counts = Counter(w.lower() for w in tokens)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text) if s.strip()]
    sources = {}
    for position, sentence in enumerate(sentences, 1):
        for word in {w.lower() for w in TOKEN.findall(sentence)}:
            sources.setdefault(word, []).append({'position': position, 'text': sentence})
    ranked = sorted((w for w in counts if w not in excluded), key=lambda w: -counts[w])
    return [{'word': w, 'count': counts[w], 'sentences': sources.get(w, []),
             'reason': ('文章中多次出现；' if counts[w] > 1 else '文章中出现一次；') + '尚未掌握'}
            for w in ranked[:max(0, min(limit, 20))]]
