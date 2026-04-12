CREATE TABLE IF NOT EXISTS lobbies (
    token TEXT,
    name TEXT NOT NULL,
    owner_id INTEGER NOT NULL UNIQUE,
    quiz_id INTEGER NOT NULL,
    running BOOLEAN NOT NULL,
    PRIMARY KEY (token)
);

CREATE TABLE IF NOT EXISTS lobbies_users (
    token TEXT NOT NULL UNIQUE,
    login TEXT NOT NULL UNIQUE,
    PRIMARY KEY (token, login),
    FOREIGN KEY (token) REFERENCES lobbies (token)
)
