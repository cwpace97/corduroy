CREATE OR REPLACE VIEW SKI_DATA.v_runs_history AS
SELECT location, updated_date, count(*) as open_count
FROM SKI_DATA.runs
WHERE run_status = 'true'
GROUP BY location, updated_date;