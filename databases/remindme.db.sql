BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `reminders` (
	`USER`	TEXT,
	`SERVER`	TEXT,
	`CHANNEL`	TEXT,
	`FINISHES`	INTEGER,
	`MESSAGE`	TEXT
);
COMMIT;