-- DROP TABLE IF EXISTS cwp.runs_stg;
CREATE TABLE IF NOT EXISTS cwp.runs_stg (
    hash varchar(64),
    location varchar(255),
    run_name varchar(255),
    run_difficulty varchar(255),
    run_status boolean,
    run_area varchar(255),
    run_groomed varchar(255),
    updated_date date,
    PRIMARY KEY (hash)
);

-- DROP TABLE IF EXISTS cwp.lifts_stg;
CREATE TABLE IF NOT EXISTS cwp.lifts_stg (
	hash varchar(64),
    location varchar(255),
    lift_name varchar(255),
    lift_type varchar(255),
    lift_status boolean,
    updated_date date,
    PRIMARY KEY (hash)
);