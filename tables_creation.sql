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