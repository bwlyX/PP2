import psycopg2
import csv

# Подключение
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",  
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Создание таблицы с новой структурой
cur.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        email TEXT
    );
""")

conn.commit()

# ---------- ФУНКЦИИ ----------
def insert_from_input():
    username = input("Введите имя: ")
    phone = input("Введите номер телефона: ")
    cur.execute("INSERT INTO phonebook (username, phone) VALUES (%s, %s);", (username, phone))
    conn.commit()
    print("✅ Запись добавлена")

def insert_from_csv(path):
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)  # Чтение с заголовками
        for row in reader:
            cur.execute("""
                INSERT INTO phonebook (first_name, last_name, phone, email)
                VALUES (%s, %s, %s, %s);
            """, (row['first_name'], row['last_name'], row['phone'], row['email']))
    conn.commit()
    print("📥 Данные из CSV загружены")


def update_user():
    name = input("Введите имя пользователя, которого хотите обновить: ")
    choice = input("Что хотите изменить? (1 - имя, 2 - номер): ")
    if choice == '1':
        new_name = input("Введите новое имя: ")
        cur.execute("UPDATE phonebook SET username = %s WHERE username = %s;", (new_name, name))
    elif choice == '2':
        new_phone = input("Введите новый номер: ")
        cur.execute("UPDATE phonebook SET phone = %s WHERE username = %s;", (new_phone, name))
    conn.commit()
    print("✏️ Данные обновлены")

def search():
    choice = input("Поиск по: 1 - имени, 2 - номеру: ")
    if choice == '1':
        name = input("Введите имя: ")
        cur.execute("SELECT * FROM phonebook WHERE username = %s;", (name,))
    else:
        phone = input("Введите номер: ")
        cur.execute("SELECT * FROM phonebook WHERE phone = %s;", (phone,))
    rows = cur.fetchall()
    print("🔎 Результаты:")
    for row in rows:
        print(row)

def delete():
    choice = input("Удалить по: 1 - имени, 2 - номеру: ")
    if choice == '1':
        name = input("Введите имя: ")
        cur.execute("DELETE FROM phonebook WHERE username = %s;", (name,))
    else:
        phone = input("Введите номер: ")
        cur.execute("DELETE FROM phonebook WHERE phone = %s;", (phone,))
    conn.commit()
    print("❌ Удалено")

# ---------- МЕНЮ ----------
def menu():
    while True:
        print("\n📱 PhoneBook Menu:")
        print("1. Добавить вручную")
        print("2. Загрузить из CSV")
        print("3. Обновить запись")
        print("4. Поиск")
        print("5. Удалить")
        print("0. Выйти")
        choice = input("Выбор: ")
        if choice == '1':
            insert_from_input()
        elif choice == '2':
            path = input("Путь к CSV-файлу: ")
            insert_from_csv(path)
        elif choice == '3':
            update_user()
        elif choice == '4':
            search()
        elif choice == '5':
            delete()
        elif choice == '0':
            break
        else:
            print("Неверный ввод!")

menu()

# Закрытие
cur.close()
conn.close()
print("🔒 Соединение закрыто")
