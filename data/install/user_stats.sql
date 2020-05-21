CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY auto_increment,
    guild TEXT NOT NULL,
    user TEXT NOT NULL,
    name TEXT NOT NULL,
    value INTEGER DEFAULT 0
);