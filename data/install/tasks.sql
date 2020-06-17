CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY auto_increment,
    time BIGINT NOT NULL,
    type VARCHAR(255) NOT NULL,
    object VARCHAR(255) NOT NULL,
    objectid INTEGER NOT NULL,
    processing INTEGER NOT NULL DEFAULT 0
)