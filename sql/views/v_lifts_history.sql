CREATE VIEW IF NOT EXISTS v_lifts_history AS
SELECT location, updated_date, count(*) as open_count
FROM lifts
WHERE lift_status = 'true'
GROUP BY location, updated_date;