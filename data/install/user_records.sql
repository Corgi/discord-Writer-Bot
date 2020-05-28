CREATE TABLE IF NOT EXISTS user_records (
    id INTEGER PRIMARY KEY auto_increment,
    user TEXT NOT NULL,
    record TEXT NOT NULL,
    value REAL DEFAULT 0
);