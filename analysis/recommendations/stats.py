"""Statistics over mistake records. Pure functions so they are easy to test."""
from collections import Counter

import mapping


def summary(records):
    """统计错题、待确认数量、各原因出现的次数，以及最需要关注的问题。"""
    total = len(records)
    wrong = sum(1 for record in records if not record.get("correct"))
    confirmed = [record for record in records if mapping.is_cause(record.get("cause"))]
    counts = Counter(record["cause"] for record in confirmed)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], list(mapping.CAUSES).index(item[0])))
    by_cause = [{"cause": cause, "label": mapping.label(cause), "count": count}
                for cause, count in ordered]
    return {
        "total": total,
        "wrong": wrong,
        "correct": total - wrong,
        "accuracy": round((total - wrong) / total, 4) if total else 0.0,
        "pending": total - len(confirmed),
        "confirmed": len(confirmed),
        "by_cause": by_cause,
        "top": by_cause[:3],
        "most_frequent": by_cause[0]["label"] if by_cause else "",
    }
