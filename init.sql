CREATE USER IF NOT EXISTS "lambda-service-account" IDENTIFIED BY "***";
GRANT CREATE TEMPORARY TABLES, DELETE, EXECUTE, INSERT, LOCK TABLES, SELECT, SHOW VIEW, UPDATE ON cwp.* TO 'lambda-service-account';
CREATE TABLE IF NOT EXISTS cwp.runs_stg (
    location varchar(255),
    run_name varchar(255),
    run_difficulty varchar(255),
    run_status boolean,
    -- run_area varchar(255),
    -- run_groomed boolean,
    updated_date date
);
CREATE TABLE IF NOT EXISTS cwp.lifts_stg (
    location varchar(255),
    lift_name varchar(255),
    lift_type varchar(255),
    lift_status boolean,
    updated_date date
);