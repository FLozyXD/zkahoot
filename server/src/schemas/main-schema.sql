CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(32) NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS Quizzes (
    id SERIAL PRIMARY KEY,
    quiz_name VARCHAR(128) NOT NULL,
    creator_id INT REFERENCES Users (Id) NOT NULL,
    creation_date DATE,
    deletion_date DATE
);

CREATE TABLE IF NOT EXISTS Answers (
    id SERIAL PRIMARY KEY,
    answer VARCHAR(512) NOT NULL
);

CREATE TABLE IF NOT EXISTS Questions (
    id SERIAL PRIMARY KEY,
    quiz_id INT REFERENCES Quizzes (Id),
    question VARCHAR(512) NOT NULL,
    question_type VARCHAR(32) NOT NULL DEFAULT 'prompt',
    answer_id INT REFERENCES Answers (Id),
    type_dependent VARCHAR(512)
);
