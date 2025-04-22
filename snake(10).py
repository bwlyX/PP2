import psycopg2
import pygame
import random

# Подключение к БД
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Создание таблиц для пользователей и их результатов
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL
    );
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS user_score (
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        level INTEGER,
        score INTEGER,
        PRIMARY KEY (user_id, level)
    );
""")
conn.commit()

# Функции работы с базой данных
def create_user():
    username = input("Введите имя пользователя: ")
    cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
    user = cur.fetchone()

    if user:
        print(f"Добро пожаловать, {username}! Ваш текущий уровень: {get_user_level(username)}")
    else:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id;", (username,))
        user_id = cur.fetchone()[0]
        print(f"Пользователь {username} успешно создан! Ваш ID: {user_id}")
        conn.commit()

    return username

def get_user_level(username):
    cur.execute("""
        SELECT level FROM user_score
        JOIN users ON user_score.user_id = users.id
        WHERE users.username = %s
        ORDER BY level DESC LIMIT 1;
    """, (username,))
    result = cur.fetchone()
    return result[0] if result else 1

def save_score(username, level, score):
    cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
    user_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO user_score (user_id, level, score)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, level)
        DO UPDATE SET score = EXCLUDED.score;
    """, (user_id, level, score))
    conn.commit()
    print(f"💾 Результат сохранён: уровень {level}, счёт {score}")

# Инициализация игры
pygame.init()
clock = pygame.time.Clock()

# Размеры окна
WIDTH = 600
HEIGHT = 400
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Змейка
snake_size = 10
snake_speed = 15

# Стены (для уровней)
def generate_walls(level):
    walls = []
    if level == 1:
        walls.append(pygame.Rect(150, 100, 200, 10))  # Пример стены
    elif level == 2:
        walls.append(pygame.Rect(100, 100, 400, 10))
        walls.append(pygame.Rect(100, 200, 400, 10))
    elif level == 3:
        walls.append(pygame.Rect(50, 100, 500, 10))
        walls.append(pygame.Rect(50, 200, 500, 10))
        walls.append(pygame.Rect(200, 50, 10, 200))
    return walls

# Функции для игры
def draw_snake(snake_body):
    for x in snake_body:
        pygame.draw.rect(WINDOW, GREEN, pygame.Rect(x[0], x[1], snake_size, snake_size))

def draw_walls(walls):
    for wall in walls:
        pygame.draw.rect(WINDOW, YELLOW, wall)

def game_loop(username):
    level = get_user_level(username)
    snake_pos = [100, 50]
    snake_body = [[100, 50], [90, 50], [80, 50]]
    food_pos = [random.randrange(1, (WIDTH // snake_size)) * snake_size,
                random.randrange(1, (HEIGHT // snake_size)) * snake_size]
    food_spawn = True

    direction = "RIGHT"
    change_to = direction

    score = 0
    walls = generate_walls(level)  # Генерация стен для текущего уровня
    snake_speed = 15 + level  # Увеличиваем скорость с каждым уровнем

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = "UP"
                if event.key == pygame.K_DOWN:
                    change_to = "DOWN"
                if event.key == pygame.K_LEFT:
                    change_to = "LEFT"
                if event.key == pygame.K_RIGHT:
                    change_to = "RIGHT"
                if event.key == pygame.K_p:
                    save_score(username, level, score)
                    print("Игра сохранена!")
                    pygame.quit()
                    quit()

        # Если направление противоположное текущему, игнорируем
        if change_to == "UP" and direction != "DOWN":
            direction = "UP"
        if change_to == "DOWN" and direction != "UP":
            direction = "DOWN"
        if change_to == "LEFT" and direction != "RIGHT":
            direction = "LEFT"
        if change_to == "RIGHT" and direction != "LEFT":
            direction = "RIGHT"

        # Обновляем позицию змейки
        if direction == "UP":
            snake_pos[1] -= snake_size
        if direction == "DOWN":
            snake_pos[1] += snake_size
        if direction == "LEFT":
            snake_pos[0] -= snake_size
        if direction == "RIGHT":
            snake_pos[0] += snake_size

        # Добавляем новый блок головы змейки
        snake_body.insert(0, list(snake_pos))

        # Проверка на еду
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 10
            food_spawn = False
        else:
            snake_body.pop()

        # Спавн новой еды
        if not food_spawn:
            food_pos = [random.randrange(1, (WIDTH // snake_size)) * snake_size,
                        random.randrange(1, (HEIGHT // snake_size)) * snake_size]
        food_spawn = True

        # Если очки больше 200, увеличиваем уровень
        if score >= 100 * level:
            level += 1
            walls = generate_walls(level)  # Генерация новых стен для следующего уровня
            snake_speed = 15 + level  # Увеличиваем скорость

        # Отображение окна
        WINDOW.fill(BLACK)
        draw_snake(snake_body)
        pygame.draw.rect(WINDOW, RED, pygame.Rect(food_pos[0], food_pos[1], snake_size, snake_size))
        draw_walls(walls)

        # Отображение счета и уровня
        font = pygame.font.SysFont("arial", 25)
        score_text = font.render(f"Счёт: {score}", True, WHITE)
        level_text = font.render(f"Уровень: {level}", True, WHITE)
        WINDOW.blit(score_text, [10, 10])
        WINDOW.blit(level_text, [WIDTH - 150, 10])

        # Обновляем экран
        pygame.display.update()

        # Проверка на столкновение с границами и телом змейки
        if snake_pos[0] < 0 or snake_pos[0] >= WIDTH or snake_pos[1] < 0 or snake_pos[1] >= HEIGHT:
            break
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                break
        # Проверка на столкновение с стенами
        for wall in walls:
            if wall.collidepoint(snake_pos[0], snake_pos[1]):
                break

        clock.tick(snake_speed)

    save_score(username, level, score)
    print("Игра окончена!")

def menu():
    while True:
        print("\n🎮 Snake Game Menu:")
        print("1. Начать игру")
        print("0. Выйти")
        choice = input("Выбор: ")
        if choice == '1':
            username = create_user()
            game_loop(username)
        elif choice == '0':
            break
        else:
            print("Неверный ввод!")

menu()

# Закрытие
cur.close()
conn.close()
print("🔒 Соединение закрыто")
