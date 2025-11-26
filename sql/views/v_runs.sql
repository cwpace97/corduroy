CREATE OR REPLACE VIEW SKI_DATA.v_runs AS
SELECT DISTINCT
    location,
    run_name,
    run_difficulty,
    md5(location) || '-' || md5(run_name) AS run_id,
    MAX(updated_date) AS updated_date
FROM SKI_DATA.runs
GROUP BY location, run_name, run_difficulty;