CREATE VIEW IF NOT EXISTS v_lifts AS
SELECT DISTINCT
    location,
    lift_name,
    lift_type,
    LOWER(HEX(QUOTE(location))) || '-' || LOWER(HEX(QUOTE(lift_name))) AS lift_id,
    MAX(updated_date) AS updated_date
FROM lifts
GROUP BY location, lift_name, lift_type;