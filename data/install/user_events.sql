CREATE TABLE IF NOT EXISTS user_events (
    id INTEGER PRIMARY KEY auto_increment,
    event INTEGER NOT NULL,
    user TEXT NOT NULL,
    words INTEGER NOT NULL DEFAULT 0
);