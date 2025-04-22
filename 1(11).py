import psycopg2
import csv
from tabulate import tabulate

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="postgres", port=5432)
cur = conn.cursor()

# ---------- СОЗДАНИЕ ТАБЛИЦЫ ----------
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
    first_name = input("Введите имя: ")
    last_name = input("Введите фамилию: ")
    phone = input("Введите номер телефона: ")
    email = input("Введите email: ")
    cur.execute("""
        INSERT INTO phonebook (first_name, last_name, phone, email)
        VALUES (%s, %s, %s, %s)
    """, (first_name, last_name, phone, email))
    conn.commit()
    print("✅ Запись добавлена")

def insert_from_csv():
    path = input("Введите путь к CSV-файлу: ")
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cur.execute("""
                INSERT INTO phonebook (first_name, last_name, phone, email)
                VALUES (%s, %s, %s, %s)
            """, (row['first_name'], row['last_name'], row['phone'], row['email']))
    conn.commit()
    print("📥 Данные из CSV загружены")

def update_user():
    id = input("Введите ID записи, которую хотите обновить: ")
    print("Выберите, что хотите изменить: 1 - Имя, 2 - Фамилия, 3 - Телефон, 4 - Email")
    choice = input("Выбор: ")
    field_map = {'1': 'first_name', '2': 'last_name', '3': 'phone', '4': 'email'}
    if choice in field_map:
        new_value = input(f"Введите новое значение для {field_map[choice]}: ")
        cur.execute(f"UPDATE phonebook SET {field_map[choice]} = %s WHERE id = %s", (new_value, id))
        conn.commit()
        print("✏️ Запись обновлена")
    else:
        print("Неверный выбор")

def search():
    pattern = input("Введите часть имени, фамилии или номера для поиска: ")
    query = """
        SELECT * FROM phonebook
        WHERE first_name ILIKE %s OR last_name ILIKE %s OR phone ILIKE %s
    """
    cur.execute(query, (f"%{pattern}%", f"%{pattern}%", f"%{pattern}%"))
    rows = cur.fetchall()
    print(tabulate(rows, headers=["ID", "Имя", "Фамилия", "Телефон", "Email"], tablefmt="fancy_grid"))

def delete():
    id = input("Введите ID записи для удаления: ")
    cur.execute("DELETE FROM phonebook WHERE id = %s", (id,))
    conn.commit()
    print("❌ Запись удалена")

def pagination():
    limit = int(input("Сколько записей отобразить: "))
    offset = int(input("С какого номера начать: "))
    cur.execute("SELECT * FROM phonebook ORDER BY id LIMIT %s OFFSET %s", (limit, offset))
    rows = cur.fetchall()
    print(tabulate(rows, headers=["ID", "Имя", "Фамилия", "Телефон", "Email"], tablefmt="fancy_grid"))

# ---------- МЕНЮ ----------
def menu():
    while True:
        print("""
📱 PhoneBook Menu:
1. Добавить вручную
2. Загрузить из CSV
3. Обновить запись
4. Поиск
5. Пагинация
6. Удалить
0. Выйти
""")
        choice = input("Выбор: ")
        if choice == '1':
            insert_from_input()
        elif choice == '2':
            insert_from_csv()
        elif choice == '3':
            update_user()
        elif choice == '4':
            search()
        elif choice == '5':
            pagination()
        elif choice == '6':
            delete()
        elif choice == '0':
            break
        else:
            print("Неверный ввод!")

menu()

cur.close()
conn.close()
print("🔒 Соединение закрыто")