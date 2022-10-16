/*DROP DATABASE sensor_droid; 
*/

CREATE DATABASE IF NOT EXISTS sensor_droid;
USE sensor_droid;

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

CREATE TABLE IF NOT EXISTS droids (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    droid_id			VARCHAR(256)		NOT NULL,
    name	 			VARCHAR(256)		NOT NULL,
    profile_fk			INT					NOT NULL,
    create_ts	        TIMESTAMP 			NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts			TIMESTAMP			NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_fk)
		REFERENCES profiles(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS temperature (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    temperature			FLOAT				NOT NULL,
    sample_time     	TIMESTAMP			NOT NULL,
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relative_humidity (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    relative_humidity	FLOAT				NOT NULL,
    sample_time			TIMESTAMP			NOT NULL,
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rssi (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    rssi				FLOAT				NOT NULL,
    sample_time			TIMESTAMP			NOT NULL,
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS soil_moisture (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    soil_moisture		FLOAT				NOT NULL,
    sample_time			TIMESTAMP			NOT NULL,
	droid_fk			INT					NOT NULL,
	FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS soil_temperature (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    soil_temperature	FLOAT				NOT NULL,
    sample_time			TIMESTAMP			NOT NULL,
    droid_fk			INT					NOT NULL,
    FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS uv (
	PRIMARY KEY (id),
    id					INT					NOT NULL AUTO_INCREMENT UNIQUE,
    uv_index			FLOAT				NOT NULL,
    sample_time			TIMESTAMP			NOT NULL,
    droid_fk			INT					NOT NULL,
    FOREIGN KEY (droid_fk)
		REFERENCES droids(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

/* Basic data to create one user and three droids for development purposes */

INSERT INTO profiles (name, email, subject, userName, region, userPoolId)
VALUES ('R2D2', 'r2d2@rebellion.com', '12345', '12345', 'tatooine', '12345');

INSERT INTO droids (droid_id, name, profile_fk)
VALUES ('0x00b', 'droid1', 1);

INSERT INTO droids (droid_id, name, profile_fk)
VALUES ('0x00b', 'droid2', 1);

INSERT INTO droids (droid_id, name, profile_fk)
VALUES ('0x00b', 'droid3', 1);

select * from droids;

desc break_here; 
