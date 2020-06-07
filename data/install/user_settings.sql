CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY auto_increment,
    user TEXT NOT NULL,
    guild TEXT NULL,
    setting TEXT NOT NULL,
    value TEXT NOT NULL
);