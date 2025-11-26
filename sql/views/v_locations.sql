CREATE OR REPLACE VIEW SKI_DATA.v_locations AS
SELECT DISTINCT
    location,
    md5(location) AS location_id,
    MAX(updated_date) AS updated_date
FROM SKI_DATA.runs
GROUP BY location
UNION
SELECT DISTINCT
    location,
    md5(location) AS location_id,
    MAX(updated_date) AS updated_date
FROM SKI_DATA.lifts
GROUP BY location;