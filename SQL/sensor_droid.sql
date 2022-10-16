DROP DATABASE sensor_droid; 


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

<<<<<<< Updated upstream
/* one soil moisture reading */
CREATE TABLE IF NOT EXISTS soil_moisture (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    soil_moisture		FLOAT				NOT NULL,
	droid_fk			INT					NOT NULL,
=======
/* one soil temp reading */
CREATE TABLE IF NOT EXISTS soil_temperature (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    soil_temperature	FLOAT				NOT NULL,
>>>>>>> Stashed changes
    time_ts				TIMESTAMP			NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES profiles(id)
        ON UPDATE CASCADE ON DELETE CASCADE

);

/* one soil temp reading */
CREATE TABLE IF NOT EXISTS soil_temperature (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    soil_temperature	FLOAT				NOT NULL,
    droid_fk			INT					NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
    FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

<<<<<<< Updated upstream
/* one uv sensor reading */
=======
/* one soil moisture reading */
CREATE TABLE IF NOT EXISTS soil_moisture (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    soil_moisture		FLOAT				NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

>>>>>>> Stashed changes
CREATE TABLE IF NOT EXISTS uv (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    uv_index			FLOAT				NOT NULL,
    droid_fk			INT					NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
<<<<<<< Updated upstream
    FOREIGN KEY (droid_fk)
		REFERENCES profiles(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

/* one temperature sensor reading */
CREATE TABLE IF NOT EXISTS temperature (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    temperature			FLOAT				NOT NULL,
    droid_fk			INT					NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
    FOREIGN KEY (droid_fk)
		REFERENCES profiles(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

/* one relative_humidity sensor reading */
CREATE TABLE IF NOT EXISTS relative_humidity (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    relative_humidity	FLOAT				NOT NULL,
    droid_fk			INT					NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
    FOREIGN KEY (droid_fk)
		REFERENCES profiles(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

/* one RSSI sensor reading */
CREATE TABLE IF NOT EXISTS rssi (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    rssi				FLOAT				NOT NULL,
    droid_fk			INT					NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
    FOREIGN KEY (droid_fk)
		REFERENCES profiles(id)
=======
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
>>>>>>> Stashed changes
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rssi (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    rssi				FLOAT				NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relative_humidity (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    relative_humidity	FLOAT				NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS temperature (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    temperature			FLOAT				NOT NULL,
    time_ts				TIMESTAMP			NOT NULL,
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

select * from profiles;

desc break_here; /* This is the basic data fro creating a user and the three droids */

INSERT INTO profiles (name, email, subject, userName, region, userPoolId)
VALUES ('R2D2', 'r2d2@rebellion.com', '12345', '12345', 'tatooine', '12345');

INSERT INTO profiles (name, email, subject, userName, region, userPoolId)
VALUES ('R2D2', 'r2d2@rebellion.com', '12345', '12345', 'tatooine', '12345');

INSERT INTO droids (droid_id, name, creator_fk)
VALUES ('0x00b', 'droid1', 1);

INSERT INTO droids (droid_id, name, creator_fk)
<<<<<<< Updated upstream
VALUES ('0x00b', 'droid2', 2);

SELECT
	*
FROM
	UV;
=======
VALUES ('0x00b', 'droid2', 1);

INSERT INTO droids (droid_id, name, creator_fk)
VALUES ('0x00b', 'droid3', 1);


select * from droids;




>>>>>>> Stashed changes
