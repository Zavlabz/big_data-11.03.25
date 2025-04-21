CREATE DATABASE IF NOT EXISTS forum_logs;

DROP TABLE IF EXISTS forum_logs.logs_raw;

CREATE TABLE forum_logs.logs_raw
(
    user_id         Nullable(UInt32),
    action_type     String,
    action_id       Nullable(UInt32),
    server_response String,
    timestamp       DateTime
)
ENGINE = ReplacingMergeTree()
ORDER BY (toDate(timestamp), user_id)
SETTINGS allow_nullable_key = 1;

-- (Опционально) таблица users, если нужна
DROP TABLE IF EXISTS forum_logs.users;

CREATE TABLE forum_logs.users
(
    user_id    UInt32,
    username   String,
    created_at DateTime
)
ENGINE = MergeTree()
ORDER BY user_id;
