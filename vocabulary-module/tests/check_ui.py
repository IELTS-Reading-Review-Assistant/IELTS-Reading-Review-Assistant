"""Isolated Streamlit interaction check; never writes to the user's records."""
import os
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    os.environ['IELTS_DATA_DIR'] = tmp
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run(timeout=30)
    assert not app.exception
    app.text_area(key='passage_input').set_value(
        'Research protects biodiversity. Research supports ecosystems.')
    next(b for b in app.button if b.label == '推荐词汇').click().run(timeout=30)
    assert not app.exception
    app.button(key='add_research').click().run()
    assert not app.exception
    assert any(e.label == 'research · 未掌握' for e in app.expander)
    area = next(t for t in app.text_area if t.label == '个人释义')
    area.set_value('我的研究笔记')
    next(b for b in app.button if b.label == '保存修改').click().run()
    assert not app.exception
    app.button(key='master_research').click().run()
    assert not app.exception
    assert not any(b.key == 'add_research' for b in app.button)
    assert any(e.label == 'research · 已掌握' for e in app.expander)
    again = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run(timeout=30)
    assert not again.exception
    assert any(e.label == 'research · 已掌握' for e in again.expander)
    assert any(t.value == '我的研究笔记' for t in again.text_area)
    print('UI workflow passed: analyse, save, edit, master, reopen.')
