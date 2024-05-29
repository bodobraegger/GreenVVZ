CREATE TABLE IF NOT EXISTS module (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    SmObjId INT(8) NOT NULL, 
    PiqYear INT(4) NOT NULL,
    PiqSession INT(3) NOT NULL,
    title TEXT,
    whitelisted BOOLEAN,
    searchterm TEXT,
    searchterm_id INT,
    CONSTRAINT key_2 UNIQUE (SmObjId, PiqYear, PiqSession)
);

CREATE TABLE IF NOT EXISTS searchterm (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS studyprogram (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    CgHighText VARCHAR(255),
    CgHighCategory VARCHAR(255),
    CONSTRAINT key_2 UNIQUE (CgHighText, CgHighCategory)
);

CREATE TABLE IF NOT EXISTS module_studyprogram (
    module_id INT(8) NOT NULL,
    studyprogram_id INT(8) NOT NULL,
    FOREIGN KEY (module_id) REFERENCES module (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (studyprogram_id) REFERENCES studyprogram (id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (module_id, studyprogram_id)
);

SELECT m.title, s.CgHighText, s.CgHighCategory, m.id, s.id 
FROM module AS m INNER JOIN module_studyprogram AS ms ON m.id = ms.module_id 
                 INNER JOIN studyprogram AS s ON s.id = ms.studyprogram_id 
WHERE whitelisted=1;