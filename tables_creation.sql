CREATE TABLE IF NOT EXISTS module (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    SmObjId INT(8) NOT NULL, 
    PiqYear INT(4) NOT NULL,
    PiqSession INT(3) ZEROFILL NOT NULL,
    title TEXT,
    whitelisted BOOLEAN,
    CONSTRAINT key_2 UNIQUE (SmObjId, PiqYear, PiqSession)
);

CREATE TABLE IF NOT EXISTS searchterm (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    term TEXT NOT NULL CHECK (term <> N'') -- Ignored in MariaDB version < 10.2.1, we are on 10.1.37 :(
);

CREATE TABLE IF NOT EXISTS studyprogram (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    CgHighObjid INT(8) NOT NULL UNIQUE,
    CgHighText VARCHAR(255),
    CgHighCategory VARCHAR(255),
    CONSTRAINT key_2 UNIQUE (CgHighText, CgHighCategory)
);

CREATE TABLE IF NOT EXISTS module_studyprogram (
    module_id INT(8) NOT NULL,
    studyprogram_id INT(8) NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (studyprogram_id) REFERENCES studyprograms (id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (module_id, studyprogram_id)
);

SELECT DISTINCT m.SmObjId, CgHighText, CgHighCategory 
    FROM module AS m INNER JOIN modules_studyprograms AS ms 
        ON m.SmObjId = ms.SmObjId
    INNER JOIN studyprograms AS s
        ON ms.CgHighObjid = s.CgHighObjid;