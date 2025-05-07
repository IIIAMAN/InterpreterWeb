import os
import streamlit as st
import translations
import base64

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
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Заголовок сайта
st.markdown(f"<h1 style='text-align: center; color: var(--text-color);'>{translations.t('title')}</h1>", unsafe_allow_html=True)

# Определение страниц с переведенными заголовками
def define_pages():
    return [
        st.Page("pages/login.py", title=translations.t('login'), icon="🔒"),
        st.Page("pages/register.py", title=translations.t('register'), icon="🆕"),
        st.Page("pages/home.py", title=translations.t('chat'), icon="💬"),
        st.Page("pages/translate.py", title=translations.t('translate'), icon="🌐"),
        st.Page("pages/notes.py", title=translations.t('notes'), icon="📝"),
    ]

# Определение доступных страниц
all_pages = define_pages()
login_page, register_page, home_page, translate_page, notes_page = all_pages

# Выбор страниц в зависимости от состояния авторизации
if st.session_state.authenticated:
    pages = [home_page, translate_page, notes_page]
else:
    pages = [login_page, register_page]

# Установка начальной страницы
if st.session_state.page == 'home' and not st.session_state.authenticated:
    st.session_state.page = 'login'
elif st.session_state.page not in ['login', 'register', 'home', 'translate', 'notes']:
    st.session_state.page = 'login'

# Навигация
current_page = st.navigation(pages, position="sidebar")

# Защита страниц
if not st.session_state.authenticated and current_page in [home_page, translate_page, notes_page]:
    st.error(translations.t('login_required'))
    st.session_state.page = 'login'
    st.rerun()

# Добавление кнопки выхода для авторизованных пользователей
if st.session_state.authenticated:
    if st.sidebar.button(translations.t('logout')):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.page = 'login'
        st.rerun()

# Чтение и кодирование изображения QR-кода
with open("qr_code.png", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode()
qr_code_html = f'''
<div style="text-align: center; margin-bottom: 10px;">
    <p style="font-size: 16px; font-weight: bold; color: #2ecc71;">↓ Скачивай Desktop приложение!! ↓</p>
</div>
<div style="text-align: center; border: 2px solid #3498db; border-radius: 10px; padding: 10px; background-color: #f9f9f9;">
    <a href="https://disk.yandex.ru/d/HXpwXFD_QqPpCA" target="_blank">
        <img src="data:image/png;base64,{base64_image}" width="200" style="display: block; margin: 0 auto;">
    </a>
</div>
'''

# Добавление QR-кода для всех пользователей
st.sidebar.markdown(qr_code_html, unsafe_allow_html=True)

# Выполнение текущей страницы
current_page.run()