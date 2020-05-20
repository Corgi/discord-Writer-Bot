CREATE TABLE IF NOT EXISTS user_challenges (
    id INTEGER PRIMARY KEY,
    guild TEXT NOT NULL,
    user TEXT NOT NULL,
    challenge TEXT NOT NULL,
    completed BIGINT DEFAULT 0
);