/*DROP DATABASE sensor_droid; 
*/

CREATE DATABASE IF NOT EXISTS sensor_droid;
USE sensor_droid;

/* table populated on user creation via cognito information / lambda */
CREATE TABLE IF NOT EXISTS profiles (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    name	 			VARCHAR(256)		NOT NULL,
    email				VARCHAR(256)		NOT NULL,
    subject				VARCHAR(64)			NOT NULL,
    userName			VARCHAR(256)		NOT NULL,
    region				VARCHAR(128)		NOT NULL,
    userPoolId			VARCHAR(128)		NOT NULL,
    create_ts	        TIMESTAMP 			NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts			TIMESTAMP			NULL ON UPDATE CURRENT_TIMESTAMP
);

/* represents an individual droid, readings are connected to the droid */
CREATE TABLE IF NOT EXISTS droids (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    droid_id			VARCHAR(256)		NOT NULL,
    name	 			VARCHAR(256)		NOT NULL,
    creator_fk			INT					NOT NULL,		
    create_ts	        TIMESTAMP 			NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts			TIMESTAMP			NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_fk)
		REFERENCES profiles(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

/* one soil temp reading */
CREATE TABLE IF NOT EXISTS soil_temp (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    temp				FLOAT				NOT NULL,
    droid_fk			INT					NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
    FOREIGN KEY (droid_fk)
		REFERENCES profiles(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

/* one soil moisture reading */
CREATE TABLE IF NOT EXISTS soil_moisture (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    moisture			FLOAT				NOT NULL,
	droid_fk			INT					NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES profiles(id)
        ON UPDATE CASCADE ON DELETE CASCADE

);

/* one sample record per table for testing */
INSERT INTO profiles (name, email, subject, userName, region, userPoolId)
VALUES ('R2D2', 'r2d2@rebellion.com', '12345', '12345', 'tatooine', '12345');

INSERT INTO droids (droid_id, name, creator_fk)
VALUES ('12345', 'droid1', 1);

INSERT INTO soil_temp (temp, time_ts, droid_fk)
VALUES (28.9459, "2022-07-13T20:40:21.020", 1);

INSERT INTO soil_moisture (moisture, time_ts, droid_fk)
VALUES (28.9459, "2022-07-13T20:40:21.020", 1);

SELECT
	*
FROM
	soil_moisture;