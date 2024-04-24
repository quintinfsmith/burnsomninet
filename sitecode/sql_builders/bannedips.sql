DROP TABLE IF EXISTS burnsomninet.banned_ip;
DROP TABLE IF EXISTS burnsomninet.malicious_query;

CREATE TABLE IF NOT EXISTS burnsomninet.banned_ip (
    `ip` VARCHAR(16),
    `ts` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (`ip`)
);

CREATE TABLE IF NOT EXISTS burnsomninet.malicious_query (
    `query` VARCHAR(256),
    PRIMARY KEY (`query`)
)
