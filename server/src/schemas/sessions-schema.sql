CREATE TABLE IF NOT EXISTS sessions (
    login TEXT,
    token TEXT NOT NULL UNIQUE,
    PRIMARY KEY (login)
);
