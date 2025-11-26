CREATE OR REPLACE VIEW SKI_DATA.v_lifts_history AS
SELECT location, updated_date, count(*) as open_count
FROM SKI_DATA.lifts
WHERE lift_status = 'true'
GROUP BY location, updated_date;