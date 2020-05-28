CREATE TABLE IF NOT EXISTS user_xp (
    id INTEGER PRIMARY KEY auto_increment,
    user TEXT NOT NULL,
    xp INTEGER DEFAULT 0
);