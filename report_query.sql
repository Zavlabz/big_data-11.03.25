-- report_query.sql

WITH
    -- 1) Собираем по дням все нужные метрики и net‑темы
    daily AS (
        SELECT
            toDate(timestamp) AS day,
            countIf(action_type='registration' AND server_response='success')       AS new_accounts,
            countIf(action_type='create_message'  AND server_response='success')    AS total_messages,
            countIf(action_type='create_message'  AND server_response='success' AND isNull(user_id)) AS anonymous_messages,
            countIf(action_type='create_topic'    AND server_response='success')
          - countIf(action_type='delete_topic'    AND server_response='success')   AS daily_net_topics
        FROM forum_logs.logs_raw
        WHERE timestamp BETWEEN toDateTime('2023-01-01 00:00:00')
                            AND toDateTime('2023-01-31 23:59:59')
        GROUP BY day
        ORDER BY day
    )

SELECT
    day,
    new_accounts,
    total_messages,
    ROUND(anonymous_messages * 100.0 / NULLIF(total_messages, 0), 2) AS percent_anonymous,
    -- running_total = сумма net_topics до текущего дня
    sum(daily_net_topics) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
    -- prev_running = running_total минус net_topics текущего дня
    (sum(daily_net_topics) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
     - daily_net_topics) AS prev_running,
    -- процент изменения тем
    CASE
      WHEN prev_running > 0
        THEN ROUND(daily_net_topics * 100.0 / prev_running, 2)
      WHEN prev_running = 0 AND running_total > 0
        THEN 100.00
      ELSE NULL
    END AS topic_change_percent
FROM daily
ORDER BY day
FORMAT CSVWithNames;
