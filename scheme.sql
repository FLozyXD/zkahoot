CREATE TABLE IF NOT EXISTS Users(
    id SERIAL PRIMARY KEY,
    login VARCHAR(32) NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS Quizzes(
    id SERIAL PRIMARY KEY,
    creator_id INT REFERENCES Users(id),
	date_of_birth DATE NOT NULL, 
    date_of_death DATE DEFAULT '2030-01-01'
);

CREATE TABLE IF NOT EXISTS Questions(
    id SERIAL PRIMARY KEY,
    quiz_id INT REFERENCES Quizzes(id),
    question TEXT,
    answer_id INT REFERENCES Answers(id)   
);

CREATE TABLE IF NOT EXISTS Answers(
    id SERIAL PRIMARY KEY,
    answer VARCHAR(512) NOT NULL,
    answer_type VARCHAR(32) NOT NULL DEFAULT 'text'
);

