import psycopg2
import csv
import sys
import os

def main(start_date, end_date, out_path):
    # Читаем конфиг из окружения
    db_host     = os.getenv('DB_HOST', 'localhost')
    db_name     = os.getenv('DB_NAME', 'forum_logs')
    db_user     = os.getenv('DB_USER', 'admin')
    db_password = os.getenv('DB_PASSWORD', 'secret')
    db_port     = os.getenv('DB_PORT', '5432')

    # Открываем подключение
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    cur = conn.cursor()

    # Собираем статистику
    query = """
        WITH daily_stats AS (
            SELECT 
                DATE(timestamp) AS day,
                COUNT(*) FILTER (WHERE action_type = 'registration' AND server_response = 'success') AS new_accounts,
                COUNT(*) FILTER (WHERE action_type = 'create_message' AND server_response = 'success') AS total_messages,
                COUNT(*) FILTER (WHERE action_type = 'create_message' AND server_response = 'success' AND user_id IS NULL) AS anonymous_messages,
                COUNT(*) FILTER (WHERE action_type = 'create_topic' AND server_response = 'success') AS created_topics,
                COUNT(*) FILTER (WHERE action_type = 'delete_topic' AND server_response = 'success') AS deleted_topics
            FROM 
                logs
            WHERE 
                timestamp BETWEEN %s AND %s
            GROUP BY 
                DATE(timestamp)
        ),
        daily_topic_counts AS (
            SELECT
                day,
                new_accounts,
                total_messages,
                anonymous_messages,
                created_topics - deleted_topics AS daily_net_topics
            FROM
                daily_stats
        ),
        cumulative_topics AS (
            SELECT
                day,
                new_accounts,
                total_messages,
                anonymous_messages,
                daily_net_topics,
                SUM(daily_net_topics) OVER (ORDER BY day) AS running_total_topics
            FROM
                daily_topic_counts
        ),
        with_previous AS (
            SELECT
                *,
                LAG(running_total_topics, 1) OVER (ORDER BY day) AS previous_total
            FROM
                cumulative_topics
        )
        SELECT 
            day,
            new_accounts,
            CASE 
                WHEN total_messages > 0 THEN ROUND((anonymous_messages::numeric / total_messages::numeric) * 100, 2)
                ELSE 0 
            END AS percent_anonymous,
            total_messages,
            CASE 
                WHEN previous_total > 0 THEN ROUND(((running_total_topics - previous_total) / previous_total::numeric) * 100, 2)
                WHEN previous_total = 0 AND running_total_topics > 0 THEN 100.00
                ELSE NULL 
            END AS topic_change_percent
        FROM 
            with_previous
        ORDER BY 
            day;
    """

    # Выполняем запрос и пишем результат
    cur.execute(query, (start_date, end_date))
    rows = cur.fetchall()

    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['day', 'new_accounts', 'percent_anonymous', 'total_messages', 'topic_change_percent'])
        writer.writerows(rows)

    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python aggregate.py <start_date> <end_date> <output_csv>")
        sys.exit(1)
    _, start, end, out = sys.argv
    main(start, end, out)
