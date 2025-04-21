
import random
from datetime import datetime, timedelta
from faker import Faker
import csv

fake = Faker()

# Параметры диапазона дат
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2023, 1, 31)
DAYS       = (END_DATE - START_DATE).days + 1

# Все типы действий
ACTION_TYPES = [
    'first_visit',    # первый заход на сайт
    'registration',   # регистрация
    'login',          # логин
    'logout',         # логаут
    'create_topic',   # создание темы
    'view_topic',     # заход на тему
    'delete_topic',   # удаление темы
    'create_message'  # написание сообщения
]

users = []
logs  = []
next_user_id = 1

for day_offset in range(DAYS):
    current = START_DATE + timedelta(days=day_offset)

    for _ in range(5):
        logs.append({
            'user_id': None,
            'action_type': 'first_visit',
            'action_id': None,
            'server_response': 'success',
            'timestamp': current
        })

    for _ in range(5):
        user = {
            'user_id': next_user_id,
            'username': fake.user_name(),
            'created_at': current
        }
        users.append(user)

        logs.append({
            'user_id': next_user_id,
            'action_type': 'registration',
            'action_id': None,
            'server_response': 'success',
            'timestamp': current
        })
        next_user_id += 1

    for action in ACTION_TYPES:
        count = 5 + (2 if action == 'create_topic' else 0)
        for _ in range(count):
            if action in ('login', 'logout', 'create_topic', 'delete_topic'):
                uid = random.choice(users)['user_id'] if users else None
            elif action == 'create_message':
                # 50% chance: залогинен, 50% — аноним
                uid = random.choice(users)['user_id'] if users and random.choice([True, False]) else None
            else:
                uid = None

            if action == 'create_topic':
                resp = 'success' if uid else 'error'
            else:
                resp = 'success'

            logs.append({
                'user_id': uid,
                'action_type': action,
                'action_id': random.randint(1000, 9999) if action in ('create_topic', 'create_message') else None,
                'server_response': resp,
                'timestamp': current
            })

def fmt(value):
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return value

with open('users.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'username', 'created_at'])
    for u in users:
        writer.writerow([u['user_id'], u['username'], fmt(u['created_at'])])

with open('logs.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'action_type', 'action_id', 'server_response', 'timestamp'])
    for entry in logs:
        writer.writerow([
            entry['user_id'] or '',
            entry['action_type'],
            entry['action_id'] or '',
            entry['server_response'],
            fmt(entry['timestamp'])
        ])

print("Готово: сгенерированы файлы users.csv и logs.csv")
