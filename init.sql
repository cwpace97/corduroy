CREATE USER IF NOT EXISTS "lambda-service-account" IDENTIFIED BY "***";
GRANT CREATE TEMPORARY TABLES, DELETE, EXECUTE, INSERT, LOCK TABLES, SELECT, SHOW VIEW, UPDATE ON cwpdb.* TO 'lambda-service-account';

CREATE TABLE IF NOT EXISTS cwpdb.runs_stg (
    location varchar(255),
    run_name varchar(255),
    run_difficulty varchar(255),
    run_status boolean,
    updated_date date
);

CREATE TABLE IF NOT EXISTS cwpdb.lifts_stg (
    location varchar(255),
    lift_name varchar(255),
    lift_type varchar(255),
    lift_status boolean,
    updated_date date
);