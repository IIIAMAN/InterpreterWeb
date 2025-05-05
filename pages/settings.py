import streamlit as st

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.title("Настройки")

max_messages = st.slider(
    "Максимальное количество сообщений в чате",
    10, 100, st.session_state.max_messages,
    help="Установите лимит истории чата"
)
st.session_state.max_messages = max_messages
st.write(f"Максимальное количество сообщений: {max_messages}")

st.markdown('</div>', unsafe_allow_html=True)