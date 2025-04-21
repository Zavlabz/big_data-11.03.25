import mysql.connector
import pandas as pd
from datetime import datetime, timedelta

# Параметры БД
config = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'database': 'mydatabase',
    'port': '3307',
}

def aggregate_logs(start_date=None, end_date=None):
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            DATE(timestamp) as day,
            COUNT(DISTINCT CASE WHEN action = 'register' THEN user_id END) AS new_accounts,
            COUNT(CASE WHEN action = 'post_message' THEN 1 END) AS total_messages,
            COUNT(CASE WHEN action = 'post_message' AND is_authenticated = 0 THEN 1 END) AS anon_messages,
            COUNT(CASE WHEN action = 'create_topic' AND status = 'success' THEN 1 END) AS new_topics
        FROM user_logs
        WHERE timestamp BETWEEN %s AND %s
        GROUP BY day
        ORDER BY day
    """, (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows)
    df['anon_percent'] = round((df['anon_messages'] / df['total_messages']) * 100, 2)
    df['topics_change_percent'] = df['new_topics'].pct_change().fillna(0).apply(lambda x: round(x * 100, 2))

    df = df[['day', 'new_accounts', 'anon_percent', 'total_messages', 'topics_change_percent']]
    df.to_csv('logs/aggregated_report.csv', index=False)
    print("📊 Aggregation complete: logs/aggregated_report.csv")

if __name__ == "__main__":
    aggregate_logs()
