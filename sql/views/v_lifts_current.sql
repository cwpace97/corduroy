CREATE VIEW IF NOT EXISTS v_lifts_current AS
SELECT * FROM lifts l1
WHERE l1.id = (
    SELECT l2.id 
    FROM lifts l2 
    WHERE l2.lift_id = l1.lift_id
    ORDER BY l2.updated_date DESC, l2.id DESC
    LIMIT 1
);