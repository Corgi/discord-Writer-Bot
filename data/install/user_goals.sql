CREATE TABLE IF NOT EXISTS user_goals (
    id INTEGER PRIMARY KEY auto_increment,
    user TEXT NOT NULL,
    type TEXT NOT NULL,
    goal INTEGER NOT NULL,
    current INTEGER NOT NULL,
    completed BOOLEAN NOT NULL,
    reset BIGINT NOT NULL,
    lastreset BIGINT NOT NULL
);