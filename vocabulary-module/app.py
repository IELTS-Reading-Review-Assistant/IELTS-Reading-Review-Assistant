import sqlite3
import streamlit as st
import storage
from vocabulary import recommend

st.set_page_config(page_title='雅思阅读复习助手', page_icon='📖', layout='wide')
st.title('雅思阅读复习助手')
st.caption('词汇模块 Version 3 · 从正在读的文章开始')


def perform(action, *args):
    try:
        action(*args)
        return True
    except (OSError, sqlite3.Error, ValueError) as exc:
        st.error(f'操作未完成，当前输入仍保留。{exc}')
        return False


try:
    book = storage.wordbook()
    history = storage.passages()
except (OSError, sqlite3.Error):
    st.error('无法读取学习记录，请检查 data 文件夹是否可读写。')
    st.stop()

mastered = {r['word'] for r in book if r['mastered']}
saved = {r['word'] for r in book}
c1, c2, c3 = st.columns(3)
c1.metric('生词本', len(book))
c2.metric('已掌握', len(mastered))
c3.metric('每篇推荐上限', '20 词')
reading, notebook = st.tabs(['文章词汇推荐', '我的生词本'])
with reading:
    st.write('粘贴文章，筛选值得优先学习的词汇。')
    if history:
        selected = st.selectbox('已保存的文章', range(len(history)),
                                format_func=lambda i: history[i][:65].replace('\n', ' ') + '…')
        if st.button('打开这篇文章'):
            st.session_state['passage_input'] = history[selected]
            st.session_state['analysed'] = history[selected]
    text = st.text_area('英文文章', key='passage_input', height=240,
                        placeholder='Paste your English passage here…')
    st.caption(f'{len(text):,} / 50,000 字符；最多 5,000 个英文词。')
    if st.button('推荐词汇', type='primary'):
        try:
            recommend(text, mastered)
            if perform(storage.save_passage, text):
                st.session_state['analysed'] = text
        except (ValueError, OSError) as exc:
            st.error(str(exc))
    st.caption('按文章词频排序，过滤基础词和已掌握词。推荐的是学习重点，不保证属于雅思必考词；词形暂不合并。')
    passage = st.session_state.get('analysed')
    if passage is not None:
        if text != passage:
            st.info('文章已修改，下方仍是上次分析的结果。点击“推荐词汇”更新。')
        try:
            items = recommend(passage, mastered)
        except (ValueError, OSError) as exc:
            st.error(str(exc))
            items = []
        st.subheader(f'学习重点 · {len(items)} 个词')
        if not items:
            st.info('没有符合条件的词汇。文章可能较简单，或相关词汇已掌握。')
        for item in items:
            word = item['word']
            try:
                meaning = storage.lookup(word)
            except (OSError, sqlite3.Error) as exc:
                st.error(f'词典暂不可用：{exc}')
                meaning = ''
            with st.expander(f"{word} · 出现 {item['count']} 次", expanded=True):
                st.text(meaning or '词典暂不可用')
                st.caption(item['reason'])
                for source in item['sentences']:
                    st.text(f"原句 {source['position']}：{source['text']}")
                a, b = st.columns(2)
                if a.button('补充本篇原句' if word in saved else '加入生词本',
                            key='add_' + word):
                    if perform(storage.save_word, item, meaning, passage):
                        st.toast('已保存到生词本')
                        st.rerun()
                if b.button('标记已掌握', key='master_' + word):
                    if perform(storage.save_word, item, meaning, passage, True):
                        st.rerun()
        st.caption('释义来源：ECDICT。多个词义请结合原句选择；个人修改仅保存到你的生词本。')

with notebook:
    query = st.text_input('搜索单词')
    mode = st.radio('学习状态', ['全部', '未掌握', '已掌握'], horizontal=True)
    shown = [r for r in book if query.strip().lower() in r['word'] and
             (mode == '全部' or bool(r['mastered']) == (mode == '已掌握'))]
    if not shown:
        st.info('暂无符合条件的记录。可以先从文章中添加单词。')
    for row in shown:
        word = row['word']
        with st.expander(word + (' · 已掌握' if row['mastered'] else ' · 未掌握')):
            with st.form('edit_' + word):
                meaning = st.text_area('个人释义', value=row['meaning'], max_chars=2000)
                known = st.checkbox('已掌握', value=bool(row['mastered']))
                if st.form_submit_button('保存修改'):
                    if perform(storage.update_word, word, meaning, known):
                        st.rerun()
            try:
                for group in storage.sources(word):
                    for source in group:
                        st.text(source['text'])
            except sqlite3.Error:
                st.error('原句读取失败，请重试。')
st.divider()
st.caption('学习记录保存在本机。适合个人使用；关闭页面后，已保存的生词和文章仍会保留。')
