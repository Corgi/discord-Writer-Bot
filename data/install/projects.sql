CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY auto_increment,
    user TEXT NOT NULL,
    name TEXT NOT NULL,
    shortname TEXT NOT NULL,
    words INTEGER DEFAULT 0,
    completed BIGINT DEFAULT 0
);