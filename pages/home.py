import streamlit as st
import google.generativeai as genai
import translations
from database import get_gemini_api_key

# Настройка Gemini API
API_KEY = get_gemini_api_key()
if not API_KEY:
    st.error("Не удалось извлечь Gemini API ключ из базы данных.")
    st.stop()
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
MAX_MESSAGES = 50

# Инициализация истории чата
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.title(f"{translations.t('chat')}, {st.session_state.username}!")

# Стили для сообщений чата и контейнера
st.markdown("""
    <style>
        .stChatMessage {
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            max-width: 70%;
            word-wrap: break-word;
        }
        .stChatMessage.user {
            background-color: var(--primary-color);
            color: white;
        }
        .stChatMessage.assistant {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
        }
        .chat-container {
            max-height: 60vh;
            max-width: 60vw;
            margin: auto;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid var(--primary-color);
            border-radius: 8px;
            background-color: var(--secondary-background-color);
        }
    </style>
""", unsafe_allow_html=True)

# Контейнер для чата с кастомным HTML
with st.markdown('<div class="chat-container">', unsafe_allow_html=True):
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# Поле ввода
if user_input := st.chat_input(translations.t('chat')):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with chat_container:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_input)

    gemini_history = [
        {"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]}
        for msg in st.session_state.chat_history[-5:]
    ]

    with st.spinner(translations.t('extracting_text')):
        try:
            chat_session = model.start_chat(history=gemini_history[:-1])
            response = chat_session.send_message(user_input)
            bot_response = response.text.strip()
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            with chat_container:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(bot_response)
        except Exception as e:
            st.error(f"{translations.t('image_processing_error')}: {e}")
            bot_response = translations.t('image_processing_error')
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

# Ограничение истории
if len(st.session_state.chat_history) > MAX_MESSAGES:
    st.session_state.chat_history = st.session_state.chat_history[-MAX_MESSAGES:]

# Кнопка очистки
if st.button(translations.t('clear_chat')):
    st.session_state.chat_history = []
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)