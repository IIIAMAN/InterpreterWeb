import os
import streamlit as st
import translations

# Отключение наблюдателя за файлами
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"
# Отключение подробных сообщений об ошибках
os.environ["STREAMLIT_LOG_LEVEL"] = "ERROR"

# Инициализация состояния сессии
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'notes' not in st.session_state:
    st.session_state.notes = []
if 'translation_history' not in st.session_state:
    st.session_state.translation_history = []
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'language' not in st.session_state:
    st.session_state.language = "Русский"  # Язык по умолчанию

# Заголовок сайта
st.markdown(f"<h1 style='text-align: center; color: var(--text-color);'>{translations.t('title')}</h1>", unsafe_allow_html=True)

# Определение страниц с переведенными заголовками
login_page = st.Page("pages/login.py", title=translations.t('login'), icon="🔒")
register_page = st.Page("pages/register.py", title=translations.t('register'), icon="🆕")
home_page = st.Page("pages/home.py", title=translations.t('chat'), icon="💬")
translate_page = st.Page("pages/translate.py", title=translations.t('translate'), icon="🌐")
notes_page = st.Page("pages/notes.py", title=translations.t('notes'), icon="📝")
ocr_page = st.Page("pages/ocr.py", title=translations.t('ocr'), icon="📸")

# Определение доступных страниц
if st.session_state.authenticated:
    pages = [home_page, translate_page, notes_page, ocr_page]
else:
    pages = [login_page, register_page]

# Навигация в боковой панели
current_page = st.navigation(pages, position="sidebar")

# Настройки в боковой панели
with st.sidebar:
    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
    language = st.selectbox(translations.t('language_label'), ["Русский", "English"])
    st.session_state.language = language

    # Кнопка выхода
    if st.button(translations.t('logout')):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

# Защита страниц
if not st.session_state.authenticated and current_page in [home_page, translate_page, notes_page, ocr_page]:
    st.error(translations.t('login_required'))
    st.rerun()

# Выполнение текущей страницы
current_page.run()