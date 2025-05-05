import streamlit as st
from PIL import Image
import pytesseract
import pyperclip
from deep_translator import GoogleTranslator
import pandas as pd
import translations
from database import get_db_connection, close_db_connection
from utils import get_unique_note_title

# Указание пути к tesseract.exe
pytesseract.pytesseract.tesseract_cmd = "./additions/tesseract.exe"

# Инициализация состояния сессии для переведенного текста
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = None

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.title(translations.t('ocr'))

uploaded_file = st.file_uploader(
    translations.t('upload_image'),
    type=["png", "jpg", "jpeg"],
    help=translations.t('supported_formats')
)

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption=translations.t('uploaded_image'), use_container_width=True)

        with st.spinner(translations.t('extracting_text')):
            extracted_text = pytesseract.image_to_string(image, lang='rus+eng')

        if extracted_text.strip():
            with col2:
                # Секция оригинального текста
                st.text_area(translations.t('extracted_text'), value=extracted_text, height=200, disabled=True)

                if st.button(translations.t('save_note'), key="save_original"):
                    connection = get_db_connection()
                    if connection:
                        try:
                            # Проверка и очистка имени файла
                            base_title = f"{translations.t('notes')} {uploaded_file.name}"
                            if not base_title.strip():
                                raise ValueError("Название файла пустое или некорректное")
                            unique_title = get_unique_note_title(base_title, st.session_state.username)
                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "INSERT INTO notes (title, content, tag, username) VALUES (%s, %s, %s, %s)",
                                    (unique_title, extracted_text, "OCR", st.session_state.username)
                                )
                                connection.commit()
                                st.success(translations.t('note_saved'))
                                st.rerun()
                        except Exception as e:
                            st.error(f"Ошибка при сохранении оригинальной заметки: {e}")
                            st.write(f"Отладка: base_title={base_title}, unique_title={unique_title if 'unique_title' in locals() else 'не определено'}, username={st.session_state.username}")
                        finally:
                            close_db_connection(connection)
                    else:
                        st.error("Не удалось подключиться к базе данных.")

                if st.button(translations.t('copy_text'), key="copy"):
                    pyperclip.copy(extracted_text)
                    st.success(translations.t('text_copied'))

                # Секция перевода
                target_language = st.selectbox(
                    translations.t('language_label'),
                    ["en", "fr", "es", "de", "ru"],
                    key="translate_select"
                )
                if st.button(translations.t('translate_button'), key="translate"):
                    translator = GoogleTranslator(source='auto', target=target_language)
                    st.session_state.translated_text = translator.translate(extracted_text)
                    connection = get_db_connection()
                    if connection:
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "INSERT INTO translations (original_text, translated_text, source_language, target_language, username) "
                                    "VALUES (%s, %s, %s, %s, %s)",
                                    (extracted_text, st.session_state.translated_text, 'auto', target_language, st.session_state.username)
                                )
                                connection.commit()
                                st.success("Перевод сохранен.")
                        except Exception as e:
                            st.error(f"Ошибка при сохранении перевода: {e}")
                        finally:
                            close_db_connection(connection)
                    else:
                        st.error("Не удалось подключиться к базе данных.")

                # Отображение переведенного текста и опция сохранения
                if st.session_state.translated_text:
                    st.text_area(translations.t('translated_text'), value=st.session_state.translated_text, height=200, disabled=True)
                    if st.button(translations.t('save_note'), key="save_translated"):
                        connection = get_db_connection()
                        if connection:
                            try:
                                # Проверка и очистка имени файла
                                base_title = f"{translations.t('notes')} {uploaded_file.name} ({target_language})"
                                if not base_title.strip():
                                    raise ValueError("Название файла пустое или некорректное")
                                unique_title = get_unique_note_title(base_title, st.session_state.username)
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        "INSERT INTO notes (title, content, tag, username) VALUES (%s, %s, %s, %s)",
                                        (unique_title, st.session_state.translated_text, "OCR_Translated", st.session_state.username)
                                    )
                                    connection.commit()
                                    st.success(translations.t('note_saved'))
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Ошибка при сохранении переведенной заметки: {e}")
                                st.write(f"Отладка: base_title={base_title}, unique_title={unique_title if 'unique_title' in locals() else 'не определено'}, username={st.session_state.username}")
                            finally:
                                close_db_connection(connection)
                        else:
                            st.error("Не удалось подключиться к базе данных.")

                # Отображение истории переводов
                with st.expander(translations.t('translation_history')):
                    connection = get_db_connection()
                    if connection:
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "SELECT original_text, translated_text, target_language "
                                    "FROM translations WHERE username = %s",
                                    (st.session_state.username,)
                                )
                                translation_history = cursor.fetchall()
                                if translation_history:
                                    # Преобразуем кортежи в список словарей для DataFrame
                                    history_data = [
                                        {
                                            "original": row[0],
                                            "translated": row[1],
                                            "language": row[2]
                                        }
                                        for row in translation_history
                                    ]
                                    st.dataframe(pd.DataFrame(history_data), use_container_width=True)
                                    if st.button(translations.t('clear_history'), key="clear_history"):
                                        with connection.cursor() as cursor:
                                            cursor.execute("DELETE FROM translations WHERE username = %s", (st.session_state.username,))
                                            connection.commit()
                                            st.success("История переводов очищена.")
                                            st.rerun()
                                else:
                                    st.write(translations.t('history_empty'))
                        except Exception as e:
                            st.error(f"Ошибка при получении истории переводов: {e}")
                        finally:
                            close_db_connection(connection)
                    else:
                        st.error("Не удалось подключиться к базе данных.")
        else:
            st.warning(translations.t('no_text_found'))
    except Exception as e:
        st.error(f"{translations.t('image_processing_error')}: {e}")

st.markdown('</div>', unsafe_allow_html=True)