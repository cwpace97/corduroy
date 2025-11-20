CREATE VIEW IF NOT EXISTS v_locations AS
SELECT DISTINCT
    location,
    LOWER(HEX(QUOTE(location))) AS location_id,
    MAX(updated_date) AS updated_date
FROM runs
GROUP BY location
UNION
SELECT DISTINCT
    location,
    LOWER(HEX(QUOTE(location))) AS location_id,
    MAX(updated_date) AS updated_date
FROM lifts
GROUP BY location;