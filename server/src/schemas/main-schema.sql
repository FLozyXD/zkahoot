CREATE TABLE IF NOT EXISTS Users (
    Id SERIAL PRIMARY KEY,
    Login VARCHAR(32) NOT NULL UNIQUE,
    Password_Hash VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS Quizzes (
    Id SERIAL PRIMARY KEY,
    Quiz_Name VARCHAR(128) NOT NULL,
    Creator_Id INT REFERENCES Users (Id) NOT NULL,
    Creation_Date DATE,
    Deletion_Date DATE
);

CREATE TABLE IF NOT EXISTS Answers (
    Id SERIAL PRIMARY KEY,
    Answer VARCHAR(512) NOT NULL
);

CREATE TABLE IF NOT EXISTS Questions (
    Id SERIAL PRIMARY KEY,
    Quiz_Id INT REFERENCES Quizzes (Id),
    Question VARCHAR(512) NOT NULL,
    Question_Type VARCHAR(32) NOT NULL DEFAULT 'prompt',
    Answer_Id INT REFERENCES Answers (Id),
    Type_Dependent VARCHAR(512)
);
