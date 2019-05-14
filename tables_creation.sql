CREATE TABLE IF NOT EXISTS `modules` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    SmObjId INT(8) NOT NULL, 
    PiqYear INT(4) NOT NULL,
    PiqSession INT(3) ZEROFILL NOT NULL,
    title TEXT,
    whitelisted BOOLEAN,
    CONSTRAINT key_2 UNIQUE (SmObjId, PiqYear, PiqSession)
);

-- should be searchterms
CREATE TABLE IF NOT EXISTS `searchterms` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `term` TEXT NOT NULL CHECK (`term` <> N'') -- Ignored in MariaDB version < 10.2.1, we are on 10.1.37 :(
);

CREATE TABLE IF NOT EXISTS studyprograms (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ScObjId INT(8) NOT NULL UNIQUE,
    ScText TEXT
);

CREATE TABLE IF NOT EXISTS modules_studyprograms (
    SmObjId INT(8) NOT NULL,
    ScObjId INT(8) NOT NULL,
    FOREIGN KEY (SmObjId) REFERENCES modules (SmObjId) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (ScObjId) REFERENCES studyprograms (ScObjId) ON DELETE RESTRICT ON UPDATE CASCADE,
    PRIMARY KEY (SmObjId, ScObjId)
);