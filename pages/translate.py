import streamlit as st
from deep_translator import GoogleTranslator
import pandas as pd
import translations
from database import get_db_connection, close_db_connection

def translate_page():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title(translations.t('translate'))

    # Инициализация состояния для результата перевода
    if 'translation_result' not in st.session_state:
        st.session_state.translation_result = None

    text_to_translate = st.text_area(translations.t('translate'), placeholder=translations.t('translate'))
    target_language = st.selectbox(translations.t('language_label'), ["en", "fr", "es", "de", "ru"])
    if st.button(translations.t('translate_button')):
        if text_to_translate:
            translator = GoogleTranslator(source='auto', target=target_language)
            translation = translator.translate(text_to_translate)
            # Сохраняем результат перевода в состояние сессии
            st.session_state.translation_result = translation
            connection = get_db_connection()
            if connection:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO translations (original_text, translated_text, source_language, target_language, username) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            (text_to_translate, translation, 'auto', target_language, st.session_state.username)
                        )
                        connection.commit()
                        st.success("Перевод сохранен.")
                except Exception as e:
                    st.error(f"Ошибка при сохранении перевода: {e}")
                finally:
                    close_db_connection(connection)
            else:
                st.error("Не удалось подключиться к базе данных.")
        else:
            st.error(translations.t('translate'))

    # Отображаем результат перевода, если он есть
    if st.session_state.translation_result:
        st.write(st.session_state.translation_result)

    with st.expander(translations.t('translation_history')):
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT original_text AS original, translated_text AS translated, target_language AS language "
                        "FROM translations WHERE username = %s",
                        (st.session_state.username,)
                    )
                    translation_history = cursor.fetchall()
                    if translation_history:
                        st.dataframe(pd.DataFrame(translation_history), use_container_width=True)
                        if st.button(translations.t('clear_history')):
                            with connection.cursor() as cursor:
                                cursor.execute("DELETE FROM translations WHERE username = %s", (st.session_state.username,))
                                connection.commit()
                                st.success("История переводов очищена.")
                                st.session_state.translation_result = None  # Очищаем результат перевода
                                st.rerun()
                    else:
                        st.write(translations.t('history_empty'))
            except Exception as e:
                st.error(f"Ошибка при получении истории переводов: {e}")
            finally:
                close_db_connection(connection)
        else:
            st.error("Не удалось подключиться к базе данных.")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    translate_page()