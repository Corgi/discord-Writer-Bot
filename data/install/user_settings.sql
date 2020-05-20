CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY,
    user TEXT NOT NULL,
    setting TEXT NOT NULL,
    value TEXT NOT NULL
);