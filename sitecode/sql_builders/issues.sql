DROP TABLE IF EXISTS burnsomninet.issue;
DROP TABLE IF EXISTS burnsomninet.issue_note;
DROP TABLE IF EXISTS burnsomninet.issue_note_revision;
DROP TABLE IF EXISTS burnsomninet.issue_link;

CREATE TABLE IF NOT EXISTS burnsomninet.issue (
    `id` INT NOT NULL AUTO_INCREMENT,
    `project` VARCHAR(32) NOT NULL,
    `author` VARCHAR(64) NOT NULL,
    `ts` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    `title` VARCHAR(256),
    `rating` SMALLINT NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS burnsomninet.issue_note (
    `id` INT NOT NULL AUTO_INCREMENT,
    `author` VARCHAR(64) NOT NULL,
    `issue_id` INT NOT NULL,
    `ts` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    `state` SMALLINT DEFAULT 0,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS burnsomninet.issue_note_revision (
    `id` INT NOT NULL AUTO_INCREMENT,
    `note` VARCHAR(1024) NOT NULL,
    `note_id` INT,
    `ts` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (`id`)
);


CREATE TABLE IF NOT EXISTS burnsomninet.issue_link (
    `dependent` INT NOT NULL,
    `independent` INT NOT NULL
);
