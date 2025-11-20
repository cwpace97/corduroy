CREATE VIEW IF NOT EXISTS v_runs AS
SELECT DISTINCT
    location,
    run_name,
    run_difficulty,
    LOWER(HEX(QUOTE(location))) || '-' || LOWER(HEX(QUOTE(run_name))) AS run_id,
    MAX(updated_date) AS updated_date
FROM runs
GROUP BY location, run_name, run_difficulty;