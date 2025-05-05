import streamlit as st
import translations
from database import get_db_connection, close_db_connection
import bcrypt
import re

# Инициализация состояния для навигации и статуса регистрации
if 'page' not in st.session_state:
    st.session_state.page = 'register'
if 'registration_success' not in st.session_state:
    st.session_state.registration_success = False

def register_page():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title(translations.t('register'))

    # Функция валидации имени пользователя
    def validate_username(username):
        if not username:
            return False, "Имя пользователя не может быть пустым."
        if len(username) < 3 or len(username) > 50:
            return False, "Имя пользователя должно быть от 3 до 50 символов."
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Имя пользователя может содержать только буквы, цифры, подчеркивания или дефисы."
        return True, ""

    # Функция валидации пароля
    def validate_password(password):
        if not password:
            return False, "Пароль не может быть пустым."
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов."
        if not re.search(r'[A-Z]', password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву."
        if not re.search(r'[a-z]', password):
            return False, "Пароль должен содержать хотя бы одну строчную букву."
        if not re.search(r'[0-9]', password):
            return False, "Пароль должен содержать хотя бы одну цифру."
        if not re.search(r'[!@#$%^&*(),.?":{}|<>~`\-_=+[\]]', password):
            return False, "Пароль должен содержать хотя бы один специальный символ (например, !, @, #, $, %, ^, &, *, (, ), ,, ., ?, :, ;, <, >, ~, `, -, _, =, +, [, ])."
        return True, ""

    # Отображение сообщения об успешной регистрации
    if st.session_state.registration_success:
        st.success("Регистрация прошла успешно! Нажмите ниже, чтобы войти.")
        if st.button("Перейти к входу"):
            st.session_state.page = 'login'
            st.session_state.registration_success = False  # Сбрасываем состояние
            st.rerun()
    else:
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
                                    # Добавление нового пользователя
                                    cursor.execute(
                                        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                                        (new_username, password_hash.decode('utf-8'))
                                    )
                                    connection.commit()
                                    st.session_state.registration_success = True  # Устанавливаем флаг успешной регистрации
                        except Exception as e:
                            st.error("Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.")
                        finally:
                            close_db_connection(connection)
                    else:
                        st.error("Не удалось подключиться к базе данных.")

    st.markdown('</div>', unsafe_allow_html=True)

register_page()