import redis
import mysql.connector
import json

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Подключение к MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="mydatabase",
    port="3307"
)
cursor = db.cursor()

# Создание таблицы, если не существует
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(50),
    entity_id INT,
    status VARCHAR(10),
    timestamp DATETIME,
    description TEXT,
    is_authenticated BOOLEAN
)
""")
db.commit()

print("✅ Таблица user_logs готова.")

# Основной цикл
while True:
    message = r.brpop('user_logs', timeout=0)
    if message:
        log_data = json.loads(message[1])
        cursor.execute("""
            INSERT INTO user_logs 
            (user_id, action, entity_id, status, timestamp, description, is_authenticated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            log_data['user_id'],
            log_data['action'],
            log_data['entity_id'],
            log_data['status'],
            log_data['timestamp'],
            log_data['description'],
            log_data['is_authenticated']
        ))
        db.commit()
        print(f"💾 Saved: {log_data['action']} by user {log_data['user_id']}")
