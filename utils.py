from database import get_db_connection, close_db_connection

def get_unique_note_title(title, username):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT title FROM notes WHERE username = %s AND title LIKE %s",
                    (username, f"{title}%")
                )
                existing_titles = [row[0] for row in cursor.fetchall()]  # Используем row[0] вместо row['title']
                if title not in existing_titles:
                    return title
                i = 1
                while f"{title} ({i})" in existing_titles:
                    i += 1
                return f"{title} ({i})"
        except Exception as e:
            raise e
        finally:
            close_db_connection(connection)
    return title