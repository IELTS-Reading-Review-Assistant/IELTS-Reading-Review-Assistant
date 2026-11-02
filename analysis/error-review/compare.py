"""Rule-based answer comparison for mistake records, independent from the UI."""
import re

SPACE = re.compile(r"\s+")
LETTER = re.compile(r"[A-Za-z]")
TRIM = " \t\r\n.,;:!?'\"()[]{}。，、；：！？“”‘’（）【】《》"


def normalize(text):
    """把答案整理成可比较的形式：统一空白与大小写，去掉首尾标点。"""
    value = str(text).replace("\u3000", " ").strip().lower()
    value = SPACE.sub(" ", value)
    return value.strip(TRIM)


def letter_set(text):
    """把选择题答案拆成选项字母集合，例如 'A,C' 与 'ca' 都得到 {'A', 'C'}。"""
    return {c.upper() for c in LETTER.findall(str(text))}


def is_correct(learner, accepted, multiple=False):
    """判断一次作答是否算对。

    multiple=True 用于选择题：按字母集合比较，顺序和分隔符都不影响结果。
    否则按文本比较：去掉空白与首尾标点、忽略大小写后，与任一可接受答案相同即算对。
    """
    if not str(learner).strip():
        return False
    answers = [a for a in accepted if str(a).strip()]
    if not answers:
        return False
    if multiple:
        chosen = letter_set(learner)
        return bool(chosen) and any(chosen == letter_set(a) for a in answers)
    value = normalize(learner)
    return bool(value) and value in {normalize(a) for a in answers}


def diff_hint(learner, accepted):
    """给出作答与参考答案的差异提示，帮助学习者定位问题。"""
    value = normalize(learner)
    if not value:
        return "没有填写答案。"
    if not accepted:
        return "没有参考答案，无法比较。"
    if value in {normalize(a) for a in accepted}:
        return "答案一致。"
    return "与参考答案不一致：你的答案是「%s」，参考答案是「%s」。" % (
        str(learner).strip(), " / ".join(str(a).strip() for a in accepted))
