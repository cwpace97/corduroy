CREATE OR REPLACE VIEW SKI_DATA.v_lifts_current AS
SELECT * FROM SKI_DATA.lifts l1
WHERE l1.id = (
    SELECT l2.id 
    FROM SKI_DATA.lifts l2 
    WHERE l2.lift_id = l1.lift_id
    ORDER BY l2.updated_date DESC, l2.id DESC
    LIMIT 1
);