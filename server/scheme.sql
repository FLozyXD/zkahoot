CREATE TABLE IF NOT EXISTS Users(
    id SERIAL PRIMARY KEY,
    login VARCHAR(32) NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS Quizzes(
    id SERIAL PRIMARY KEY,
    creator_id INT REFERENCES Users(id),
	creation_date DATE, 
    deletion_date DATE
);

CREATE TABLE IF NOT EXISTS Questions(
    id SERIAL PRIMARY KEY,
    quiz_id INT REFERENCES Quizzes(id),
    question TEXT NOT NULL,
    answer_id INT REFERENCES Answers(id)   
);

CREATE TABLE IF NOT EXISTS Answers(
    id SERIAL PRIMARY KEY,
    answer VARCHAR(512) NOT NULL,
    answer_type VARCHAR(32) NOT NULL DEFAULT 'text'
);

