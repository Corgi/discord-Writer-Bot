CREATE TABLE IF NOT EXISTS sprint_users (
    id INTEGER PRIMARY KEY auto_increment,
    sprint INTEGER NOT NULL,
    user TEXT NOT NULL,
    timejoined BIGINT DEFAULT 0,
    starting_wc INTEGER DEFAULT 0,
    current_wc INTEGER DEFAULT 0,
    ending_wc INTEGER DEFAULT 0,
    project INTEGER NULL
);