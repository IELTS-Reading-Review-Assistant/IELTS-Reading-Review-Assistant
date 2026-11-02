"""Mistake record service: validate, compare, save, and confirm causes."""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[1] / "recommendations"))  # 目录名带连字符，无法作为包导入
import mapping  # noqa: E402
import stats  # noqa: E402

import compare  # noqa: E402
import storage  # noqa: E402

MAX_TEXT = 2000


def _text(value, limit=MAX_TEXT):
    value = (value or "").strip()
    if len(value) > limit:
        raise ValueError("单个字段不能超过 %d 个字符。" % limit)
    return value


def save(passage="", question="", learner="", accepted=(), choices=(),
         multiple=False, evidence="", reasoning="", notes="", cause=None):
    """保存一道题：先按规则判对错，再写入数据库。原因可以先留空（待确认）。"""
    question = _text(question)
    if not question:
        raise ValueError("请填写题干。")
    accepted = [_text(a) for a in accepted if _text(a)]
    if not accepted:
        raise ValueError("至少需要一个可接受答案。")
    if cause is not None and not mapping.is_cause(cause):
        raise ValueError("未知的错题原因：%s" % cause)
    record = {
        "passage": _text(passage),
        "question": question,
        "learner": _text(learner),
        "accepted": accepted,
        "choices": [_text(c) for c in choices if _text(c)],
        "multiple": bool(multiple),
        "correct": compare.is_correct(learner, accepted, bool(multiple)),
        "evidence": _text(evidence),
        "reasoning": _text(reasoning),
        "notes": _text(notes),
        "cause": cause,
    }
    return storage.add(record)


def detail(mistake_id):
    """取一条记录，附带差异提示和已映射的建议。"""
    record = storage.get(mistake_id)
    if record is None:
        raise ValueError("找不到编号为 %s 的记录。" % mistake_id)
    record["hint"] = compare.diff_hint(record["learner"], record["accepted"])
    record["advice"] = mapping.advice_for(record["cause"]) if record["cause"] else []
    return record


def pending():
    return storage.pending()


def confirm(mistake_id, cause):
    if not mapping.is_cause(cause):
        raise ValueError("未知的错题原因：%s" % cause)
    storage.confirm(mistake_id, cause)


def confirm_many(ids, cause):
    if not mapping.is_cause(cause):
        raise ValueError("未知的错题原因：%s" % cause)
    return storage.confirm_many(ids, cause)


def summary(include_correct=True):
    records = storage.records(include_correct=include_correct)
    return __import__("stats").summary(records)
