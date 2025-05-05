import streamlit as st
import translations
from database import get_db_connection, close_db_connection
import bcrypt

def login_page():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title(translations.t('login'))

    # Функция валидации имени пользователя
    def validate_username(username):
        if not username:
            return False, "Имя пользователя не может быть пустым."
        return True, ""

    # Функция валидации пароля
    def validate_password(password):
        if not password:
            return False, "Пароль не может быть пустым."
        return True, ""

    with st.form("login_form"):
        username = st.text_input(translations.t('login'), placeholder=translations.t('login_placeholder'))
        password = st.text_input(translations.t('password'), type="password", placeholder=translations.t('password_placeholder'))
        submit_button = st.form_submit_button(translations.t('login_button'))

        if submit_button:
            # Валидация ввода
            is_valid_username, username_error = validate_username(username)
            is_valid_password, password_error = validate_password(password)

            if not is_valid_username:
                st.error(username_error)
            elif not is_valid_password:
                st.error(password_error)
            else:
                connection = get_db_connection()
                if connection:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
                            result = cursor.fetchone()
                            if result and result[0]:
                                password_hash = result[0]
                                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                                    st.session_state.authenticated = True
                                    st.session_state.username = username
                                    st.success(translations.t('login_success'))
                                    st.rerun()
                                else:
                                    st.error("Неверный пароль.")
                            else:
                                st.error("Пользователь не найден.")
                    except Exception as e:
                        st.error("Произошла ошибка при входе. Пожалуйста, попробуйте снова.")
                    finally:
                        close_db_connection(connection)
                else:
                    st.error("Не удалось подключиться к базе данных.")

    st.markdown('</div>', unsafe_allow_html=True)

# Отображаем страницу авторизации по умолчанию
login_page()