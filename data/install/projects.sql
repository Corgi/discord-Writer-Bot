CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY auto_increment,
    guild TEXT NOT NULL,
    user TEXT NOT NULL,
    name TEXT NOT NULL,
    shortname TEXT NOT NULL,
    words INTEGER DEFAULT 0,
    completed BIGINT DEFAULT 0
);