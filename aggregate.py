import psycopg2, csv, sys
from dateutil import parser
import os

def main(start_str, end_str, out_path='report.csv'):
    start = parser.parse(start_str)
    end   = parser.parse(end_str)



    def main(start_date, end_date, out_path):
        db_host = os.getenv('DB_HOST', 'localhost')
        db_user = os.getenv('DB_USER', 'admin')
        db_password = os.getenv('DB_PASSWORD', 'secret')
        db_name = os.getenv('DB_NAME', 'forum_logs')
        db_port = os.getenv('DB_PORT', '5432')

        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
    cur = conn.cursor()

    query = """
    WITH daily AS (
      SELECT date(timestamp) AS day,
        COUNT(*) FILTER (WHERE action_type='registration' AND server_response='success') AS new_accounts,
        COUNT(*) FILTER (WHERE action_type='create_message' AND server_response='success') AS total_messages,
        COUNT(*) FILTER (WHERE action_type='create_message' AND server_response='success' AND user_id IS NULL) AS anon_messages,
        COUNT(*) FILTER (WHERE action_type='create_topic' AND server_response='success') AS topics_created,
        COUNT(*) FILTER (WHERE action_type='delete_topic' AND server_response='success') AS topics_deleted
      FROM logs
      WHERE timestamp BETWEEN %s AND %s
      GROUP BY date(timestamp)
    ),
    cumul AS (
      SELECT day, new_accounts, total_messages, anon_messages,
             topics_created - topics_deleted AS net_topics
      FROM daily
    ),
    running AS (
      SELECT day, new_accounts, total_messages, anon_messages, net_topics,
             SUM(net_topics) OVER (ORDER BY day) AS total_topics
      FROM cumul
    ),
    with_prev AS (
      SELECT *, LAG(total_topics) OVER (ORDER BY day) AS prev_total
      FROM running
    )
    SELECT
      day,
      new_accounts,
      CASE WHEN total_messages>0
           THEN ROUND((anon_messages::numeric/total_messages)*100,2)
           ELSE 0 END AS pct_anonymous,
      total_messages,
      CASE
        WHEN prev_total>0
          THEN ROUND(((total_topics - prev_total)/prev_total)*100,2)
        WHEN prev_total=0 AND total_topics>0
          THEN 100.00
        ELSE NULL
      END AS topic_change_pct
    FROM with_prev
    ORDER BY day;
    """

    cur.execute(query, (start, end))
    rows = cur.fetchall()
    cur.close(); conn.close()

    with open(out_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['day','new_accounts','pct_anonymous','total_messages','topic_change_pct'])
        w.writerows(rows)

    print(f"Отчёт сохранён в {out_path}")

if __name__=='__main__':
    if len(sys.argv)<3:
        print("Usage: python aggregate.py <start_date> <end_date> [<output.csv>]")
        sys.exit(1)
    args = sys.argv
    out = args[3] if len(args)==4 else 'report.csv'
    main(args[1], args[2], out)
