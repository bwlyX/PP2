import psycopg2

try:
    conn = psycopg2.connect(
        dbname="postgres",  # можешь поменять на свою базу, если знаешь имя
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    print("Успешно подключился к базе!")
    conn.close()
except Exception as e:
    print("Ошибка подключения:", e)
