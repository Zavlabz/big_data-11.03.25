import random
import redis
import json
import time
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
r = redis.Redis(host='localhost', port=6379, db=0)

ACTIONS = [
    'first_visit', 'register', 'login', 'logout',
    'create_topic', 'visit_topic', 'delete_topic', 'post_message'
]

MIN_ACTION_COUNTS = {
    'first_visit': 5,
    'register': 5,
    'login': 5,
    'logout': 5,
    'create_topic': 5,
    'visit_topic': 5,
    'delete_topic': 5,
    'post_message': 5
}

def generate_log(action, is_logged_in):
    user_id = fake.random_int(min=1, max=100)
    entity_id = fake.random_int(min=1000, max=9999)
    timestamp = fake.date_time_between(start_date='-30d', end_date='now').isoformat()
    status = 'error' if action == 'create_topic' and not is_logged_in else 'success'
    description = f"{action} by {'user' if is_logged_in else 'anon'} #{user_id}"

    return {
        "user_id": user_id,
        "action": action,
        "entity_id": entity_id,
        "status": status,
        "timestamp": timestamp,
        "description": description,
        "is_authenticated": is_logged_in
    }

def send_log(log):
    r.lpush('user_logs', json.dumps(log))
    print(f"Sent: {log['action']} -> {log['status']}")

def generate_logs_for_day():
    for action in ACTIONS:
        count = max(MIN_ACTION_COUNTS[action], random.randint(5, 15))
        for _ in range(count):
            is_logged_in = random.choice([True, False])
            # Гарантируем 2 ошибки при создании темы без логина
            if action == 'create_topic' and random.random() < 0.2:
                is_logged_in = False
            if action == 'post_message':
                is_logged_in = random.choice([True, False])
            log = generate_log(action, is_logged_in)
            send_log(log)
            time.sleep(0.05)

if __name__ == "__main__":
    while True:
        generate_logs_for_day()
        print("🔁 Logs for 1 day generated.")
        time.sleep(10)  # Меняй на 86400 для генерации раз в день
