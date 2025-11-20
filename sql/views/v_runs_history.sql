CREATE VIEW IF NOT EXISTS v_runs_history AS
SELECT location, updated_date, count(*) as open_count
FROM runs
WHERE run_status = 'true'
GROUP BY location, updated_date;