CREATE TABLE IF NOT EXISTS guild_settings (
    id INTEGER PRIMARY KEY auto_increment,
    guild TEXT NOT NULL,
    setting TEXT NOT NULL,
    value TEXT NOT NULL
);