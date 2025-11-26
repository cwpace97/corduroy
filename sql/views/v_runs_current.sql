CREATE OR REPLACE VIEW SKI_DATA.v_runs_current AS
SELECT * FROM SKI_DATA.runs r1
WHERE r1.id = (
    SELECT r2.id 
    FROM SKI_DATA.runs r2 
    WHERE r2.run_id = r1.run_id
    ORDER BY r2.updated_date DESC, r2.id DESC
    LIMIT 1
);