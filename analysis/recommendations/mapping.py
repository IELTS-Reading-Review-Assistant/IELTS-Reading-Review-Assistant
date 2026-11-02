"""Rule-based mapping from mistake causes to review advice."""

CAUSES = {
    "vocabulary": "词汇不认识",
    "sentence": "句子没读懂",
    "evidence": "证据定位错",
    "qualifier": "忽略限定词",
}

ADVICE = {
    "vocabulary": [
        "把题干和原文里不认识的词加入生词本，优先记文章里反复出现的。",
        "背单词时连同它所在的句子一起记，避免只记住中文意思。",
    ],
    "sentence": [
        "先找主干（谁做什么），再把 although、because、which 引出的部分划出来。",
        "读不懂的长句先写一版翻译，再对照参考译文找差别。",
    ],
    "evidence": [
        "做题先圈题干关键词，再回原文定位，把定位到的句子抄进证据栏。",
        "IELTS 常把原文换一种说法，找同义替换而不是原词重现。",
    ],
    "qualifier": [
        "题干出现 only、all、never、mainly 这类词时，先划出来再看选项。",
        "把原文和选项逐项对照，重点检查程度词和范围词有没有被改动。",
    ],
}


def is_cause(cause):
    return cause in CAUSES


def options():
    """给界面用的取值列表：[(key, label), ...]，顺序固定。"""
    return [(key, CAUSES[key]) for key in CAUSES]


def label(cause):
    return CAUSES.get(cause, "未分类")


def advice_for(cause):
    """把一个原因映射成固定的复习建议；未知原因返回空列表。"""
    return list(ADVICE.get(cause, []))


def advice_for_records(records):
    """按出现次数从多到少，给出每个已确认原因对应的建议。"""
    counts = {}
    for record in records:
        cause = record.get("cause")
        if is_cause(cause):
            counts[cause] = counts.get(cause, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], list(CAUSES).index(item[0])))
    return [{"cause": cause, "label": CAUSES[cause], "count": count,
             "advice": advice_for(cause)} for cause, count in ordered]
