DROP TABLE IF EXISTS Problem;
DROP TABLE IF EXISTS Solution;

CREATE TABLE Problem
(
    id INTEGER NOT NULL,
    problemName CHAR(20) NOT NULL,
    comment VARCHAR,
    dimension INTEGER NOT NULL,
    edgeWeightType CHAR(6) NOT NULL,
    nodes TEXT NOT NULL,

    CONSTRAINT PK PRIMARY KEY(id, problemName),
    CONSTRAINT UNIQUEITEMS UNIQUE(id, problemName, nodes)
);

CREATE TABLE Solution
(
    id INTEGER NOT NULL,
    problemName CHAR(20) NOT NULL,
    bestRoute TEXT NOT NULL,
    tourLength REAL NOT NULL,
    timeTaken INTEGER NOT NULL,
    dateSolved DATE NOT NULL,

    CONSTRAINT PK PRIMARY KEY(id, problemName),
    CONSTRAINT FK FOREIGN KEY(problemName) REFERENCES Problem(problemName),
    CONSTRAINT DATECHECK CHECK(dateSolved >= DATE("now"))
);