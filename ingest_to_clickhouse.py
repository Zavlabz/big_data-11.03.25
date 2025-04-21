import csv
from datetime import datetime
from clickhouse_driver import Client

# 1) Подключение
client = Client(
    host='localhost',
    port=9000,
    user='default',
    password='123',
    database='forum_logs'
)

# 2) Загрузка users.csv (если нужна)
with open('users.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = []
    for row in reader:
        # parse created_at into datetime
        created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
        rows.append((
            int(row['user_id']),
            row['username'],
            created_at
        ))
if rows:
    client.execute(
        'INSERT INTO users (user_id, username, created_at) VALUES',
        rows
    )

# 3) Загрузка logs.csv
with open('logs.csv', newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = []
    for row in reader:
        user_id = int(row['user_id']) if row['user_id'] else None
        action_id = int(row['action_id']) if row['action_id'] else None
        # parse timestamp into datetime
        ts = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
        rows.append((
            user_id,
            row['action_type'],
            action_id,
            row['server_response'],
            ts
        ))

client.execute(
    'INSERT INTO logs_raw (user_id, action_type, action_id, server_response, timestamp) VALUES',
    rows
)

print("✅ Данные успешно загружены в ClickHouse.")
