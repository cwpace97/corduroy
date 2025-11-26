CREATE OR REPLACE VIEW SKI_DATA.v_lifts AS
SELECT DISTINCT
    location,
    lift_name,
    lift_type,
    md5(location) || '-' || md5(lift_name) AS lift_id,
    MAX(updated_date) AS updated_date
FROM SKI_DATA.lifts
GROUP BY location, lift_name, lift_type;