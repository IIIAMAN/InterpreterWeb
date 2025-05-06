import streamlit as st
import translations
from database import get_db_connection, close_db_connection
import bcrypt
import re
import time

# Инициализация состояния для навигации и статуса регистрации
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'page' not in st.session_state:
    st.session_state.page = 'register'

def register_page():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title(translations.t('register'))

    # Функция валидации имени пользователя
    def validate_username(username):
        if not username:
            return False, translations.t('username_empty')
        if len(username) < 3 or len(username) > 50:
            return False, translations.t('username_length')
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, translations.t('username_invalid')
        return True, ""

    # Функция валидации пароля
    def validate_password(password):
        if not password:
            return False, translations.t('password_empty')
        if len(password) < 8:
            return False, translations.t('password_length')
        if not re.search(r'[A-Z]', password):
            return False, translations.t('password_uppercase')
        if not re.search(r'[a-z]', password):
            return False, translations.t('password_lowercase')
        if not re.search(r'[0-9]', password):
            return False, translations.t('password_digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>~`\-_=+[\]]', password):
            return False, translations.t('password_special')
        return True, ""

    with st.form("register_form"):
        new_username = st.text_input(translations.t('new_username'), placeholder=translations.t('new_username'))
        new_password = st.text_input(translations.t('new_password'), type="password", placeholder=translations.t('new_password'))
        submit_button = st.form_submit_button(translations.t('register_button'))

        if submit_button:
            is_valid_username, username_error = validate_username(new_username)
            is_valid_password, password_error = validate_password(new_password)

            if not is_valid_username:
                st.error(username_error)
            elif not is_valid_password:
                st.error(password_error)
            else:
                connection = get_db_connection()
                if connection:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT id FROM users WHERE username = %s", (new_username,))
                            if cursor.fetchone():
                                st.error(translations.t('username_taken'))
                            else:
                                password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                                cursor.execute(
                                    "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                                    (new_username, password_hash.decode('utf-8'))
                                )
                                connection.commit()
                                st.session_state.authenticated = True
                                st.session_state.username = new_username
                                st.success(translations.t('Регистрация успешна'))
                                time.sleep(1)  # Задержка для отображения сообщения
                                st.session_state.page = 'home'
                                st.rerun()
                    except Exception as e:
                        st.error(translations.t('registration_error'))
                    finally:
                        close_db_connection(connection)
                else:
                    st.error(translations.t('db_connection_error'))

    st.markdown('</div>', unsafe_allow_html=True)

register_page()