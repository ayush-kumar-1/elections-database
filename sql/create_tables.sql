CREATE DATABASE election_data; 
USE election_data; 

CREATE TABLE contests (
	contest_id INT,
	sheet_number INT, 
	contest_name TEXT, 
	election_month INT, 
	election_year INT, 
	election_type TEXT, 
	PRIMARY KEY (contest_id)
); 

CREATE TABLE candidates (
	contest_id INT, 
	candidate_id CHAR(64), 
	candidate_name TEXT, 
	candidate_party CHAR(3), 
	sheet_number INT,
	election_year INT, 
	election_month INT,
	PRIMARY KEY (candidate_id),
	FOREIGN KEY (contest_id) REFERENCES contests(contest_id)
); 

CREATE TABLE counties (
	STATEFP        INT,
	COUNTYFP       INT,
	COUNTYNS       INT,
	GEOID          INT,
	COUNTYNAME     VARCHAR(128) UNIQUE,
	NAMELSAD      TEXT,
	LSAD           INT,
	CLASSFP       TEXT,
	MTFCC         TEXT,
	CSAFP         TEXT,
	CBSAFP        TEXT,
	METDIVFP      TEXT,
	FUNCSTAT      TEXT,
	ALAND        DECIMAL,
	AWATER       DECIMAL,
	INTPTLAT     DECIMAL,
	INTPTLON     DECIMAL,
	geometry    TEXT, 
    PRIMARY KEY (COUNTYFP)
);

CREATE TABLE results_by_county (
	county_name VARCHAR(128), 
	candidate_id CHAR(64), 
	election_day INT, 
	absentee_by_mail INT, 
	advance_in_person INT, 
	provisional INT, 
	total_votes INT, 
	result_id VARCHAR(512), 
	PRIMARY KEY (result_id), 
	FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id), 
	FOREIGN KEY (county_name) REFERENCES counties(COUNTYNAME)
); 

CREATE TABLE county_turnout (
	county_turnout_id INT AUTO_INCREMENT,
	county_name VARCHAR(128), 
	race TEXT, 
	gender TEXT, 
	age_grp TEXT, 
	registered INT, 
	voted INT, 
	turnout_percent DECIMAL, 
	election_year INT, 
	election_month INT,
	PRIMARY KEY (county_turnout_id),
	FOREIGN KEY (county_name) REFERENCES counties(COUNTYNAME)
);

CREATE TABLE precinct_turnout (
	precinct_turnout_id INT AUTO_INCREMENT, 
	county_name VARCHAR(128), 
	precinct_id TEXT, 
	precinct_description TEXT, 
	race TEXT, 
	gender TEXT,
	registered INT, 
	voted INT, 
	turnout_percent DECIMAL, 
	election_year INT, 
	election_month INT,
	PRIMARY KEY (precinct_turnout_id), 
	FOREIGN KEY (county_name) REFERENCES counties(COUNTYNAME)
); 

CREATE TABLE population (
	census_id INT, 
	county_fips_code INT, 
	year INT, 
	aggrp TEXT, 
	race TEXT, 
	gender TEXT, 
	population_amount INT, 
	PRIMARY KEY (census_id), 
	FOREIGN KEY (county_fips_code) REFERENCES counties(COUNTYFP)
);