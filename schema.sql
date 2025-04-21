CREATE TYPE action_type AS ENUM (
  'first_visit',
  'registration',
  'login',
  'logout',
  'create_topic',
  'view_topic',
  'delete_topic',
  'create_message'
);

CREATE TYPE server_response AS ENUM ('success','error');

CREATE TABLE users (
  user_id    SERIAL PRIMARY KEY,
  username   VARCHAR(50) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE logs (
  log_id          SERIAL PRIMARY KEY,
  user_id         INTEGER REFERENCES users(user_id),
  action_type     action_type     NOT NULL,
  action_id       INTEGER,
  server_response server_response NOT NULL,
  timestamp       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_logs_timestamp ON logs (timestamp);
CREATE INDEX idx_logs_user      ON logs (user_id);
