import streamlit as st
import translations
from database import get_db_connection, close_db_connection
from utils import get_unique_note_title

def notes_page():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title(translations.t('notes'))

    # Стили для карточек заметок
    st.markdown("""
        <style>
            .note-card {
                background: var(--secondary-background-color);
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 15px;
                margin-bottom: 10px;
                border: 1px solid var(--primary-color);
            }
            .note-card h4 {
                color: var(--text-color);
                margin: 0;
            }
            .note-card p {
                color: var(--text-color);
                margin: 5px 0;
            }
            .note-card .tag {
                background: var(--primary-color);
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 0.9em;
            }
        </style>
    """, unsafe_allow_html=True)

    # Форма для добавления заметок
    with st.expander(translations.t('add_note')):
        with st.form("note_form"):
            note_title = st.text_input(translations.t('note_title'), placeholder=translations.t('note_title'))
            note_content = st.text_area(translations.t('note_content'), placeholder=translations.t('note_content'))
            note_tag = st.text_input(translations.t('note_tag'), placeholder=translations.t('note_tag'))
            if st.form_submit_button(translations.t('submit_note')):
                if note_title and note_content:
                    connection = get_db_connection()
                    if connection:
                        try:
                            unique_title = get_unique_note_title(note_title, st.session_state.username)
                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "INSERT INTO notes (title, content, tag, username) VALUES (%s, %s, %s, %s)",
                                    (unique_title, note_content, note_tag, st.session_state.username)
                                )
                                connection.commit()
                                st.success(translations.t('note_added'))
                                st.rerun()
                        except Exception as e:
                            st.error(f"Ошибка при добавлении заметки: {e}")
                        finally:
                            close_db_connection(connection)
                    else:
                        st.error("Не удалось подключиться к базе данных.")
                else:
                    st.error(translations.t('note_title_content_required'))

    # Фильтр заметок по тегу
    tag_filter = st.text_input(translations.t('filter_tag'), placeholder=translations.t('filter_tag'))
    filtered_notes = []  # Инициализация перед try-except
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                if tag_filter:
                    cursor.execute(
                        "SELECT id, title, content, tag FROM notes WHERE username = %s AND tag LIKE %s",
                        (st.session_state.username, f"%{tag_filter.lower()}%")
                    )
                else:
                    cursor.execute(
                        "SELECT id, title, content, tag FROM notes WHERE username = %s",
                        (st.session_state.username,)
                    )
                filtered_notes = cursor.fetchall()
        except Exception as e:
            st.error(f"Ошибка при получении заметок: {e}")
        finally:
            close_db_connection(connection)
    else:
        st.error("Не удалось подключиться к базе данных.")

    # Отображение заметок
    for i, note in enumerate(filtered_notes):
        with st.expander(f"{note[1]}"):  # title по индексу 1
            st.markdown(f"""
                <div class="note-card">
                    <h4>{translations.t('note_title')}: {note[1]}</h4>
                    <p><strong>{translations.t('note_content')}:</strong> {note[2]}</p>
                    <span class="tag">{translations.t('note_tag')}: {note[3]}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button(translations.t('delete'), key=f"delete_{i}"):
                connection = get_db_connection()
                if connection:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "DELETE FROM notes WHERE id = %s AND username = %s",
                                (note[0], st.session_state.username)  # id по индексу 0
                            )
                            connection.commit()
                            st.success("Заметка удалена.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка при удалении заметки: {e}")
                    finally:
                        close_db_connection(connection)
                else:
                    st.error("Не удалось подключиться к базе данных.")

    if not filtered_notes:
        st.write(translations.t('no_notes'))

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    notes_page()