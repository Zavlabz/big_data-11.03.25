import mysql.connector
import time
from datetime import datetime

# Подключение к базе данных
config = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'database': 'mydatabase',
    'port': '3307',
}

def fetch_logs():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_logs")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def save_logs(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/log_export_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for row in data:
            f.write(','.join(map(str, row)) + '\n')
    print(f"✅ Logs saved to {filename}")

if __name__ == "__main__":
    while True:
        logs = fetch_logs()
        save_logs(logs)
        time.sleep(600)  # Раз в 10 минут
