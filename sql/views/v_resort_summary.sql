-- Pre-aggregated resort summary view for home page
-- This avoids returning individual lift/run details and computes all counts in SQL

CREATE OR REPLACE VIEW SKI_DATA.v_resort_summary AS
WITH lift_counts AS (
    SELECT 
        location,
        COUNT(*) as total_lifts,
        COUNT(*) FILTER (WHERE lift_status IN ('Open', 'open', 'true', 'True', '1')) as open_lifts,
        MAX(updated_date) as last_updated
    FROM SKI_DATA.v_lifts_current
    GROUP BY location
),
run_counts AS (
    SELECT 
        location,
        COUNT(*) as total_runs,
        COUNT(*) FILTER (WHERE run_status IN ('Open', 'open', 'true', 'True', '1')) as open_runs,
        MAX(updated_date) as last_updated
    FROM SKI_DATA.v_runs_current
    GROUP BY location
),
runs_by_difficulty AS (
    SELECT 
        location,
        COUNT(*) FILTER (WHERE 
            run_status IN ('Open', 'open', 'true', 'True', '1') AND
            (LOWER(run_difficulty) LIKE '%green%' OR LOWER(run_difficulty) LIKE '%easiest%' OR LOWER(run_difficulty) LIKE '%beginner%')
        ) as green_count,
        COUNT(*) FILTER (WHERE 
            run_status IN ('Open', 'open', 'true', 'True', '1') AND
            (LOWER(run_difficulty) LIKE '%blue%' OR LOWER(run_difficulty) LIKE '%intermediate%' OR LOWER(run_difficulty) LIKE '%more difficult%')
        ) as blue_count,
        COUNT(*) FILTER (WHERE 
            run_status IN ('Open', 'open', 'true', 'True', '1') AND
            (LOWER(run_difficulty) LIKE '%double%' OR LOWER(run_difficulty) LIKE '%expert%' OR LOWER(run_difficulty) LIKE '%most difficult%')
        ) as double_black_count,
        COUNT(*) FILTER (WHERE 
            run_status IN ('Open', 'open', 'true', 'True', '1') AND
            (LOWER(run_difficulty) LIKE '%black%' OR LOWER(run_difficulty) LIKE '%advanced%' OR LOWER(run_difficulty) LIKE '%difficult%') AND
            NOT (LOWER(run_difficulty) LIKE '%double%' OR LOWER(run_difficulty) LIKE '%expert%' OR LOWER(run_difficulty) LIKE '%most difficult%')
        ) as black_count,
        COUNT(*) FILTER (WHERE 
            run_status IN ('Open', 'open', 'true', 'True', '1') AND
            (LOWER(run_difficulty) LIKE '%park%' OR LOWER(run_difficulty) LIKE '%terrain%')
        ) as terrain_park_count
    FROM SKI_DATA.v_runs_current
    GROUP BY location
),
lifts_history AS (
    SELECT 
        location,
        jsonb_agg(
            jsonb_build_object('date', updated_date, 'openCount', open_count)
            ORDER BY updated_date ASC
        ) as history
    FROM (
        SELECT location, updated_date, open_count
        FROM SKI_DATA.v_lifts_history
        WHERE updated_date::date >= CURRENT_DATE - INTERVAL '7 days'
    ) sub
    GROUP BY location
),
runs_history AS (
    SELECT 
        location,
        jsonb_agg(
            jsonb_build_object('date', updated_date, 'openCount', open_count)
            ORDER BY updated_date ASC
        ) as history
    FROM (
        SELECT location, updated_date, open_count
        FROM SKI_DATA.v_runs_history
        WHERE updated_date::date >= CURRENT_DATE - INTERVAL '7 days'
    ) sub
    GROUP BY location
),
recently_opened_lifts_ranked AS (
    SELECT 
        location,
        lift_name,
        date_opened,
        ROW_NUMBER() OVER (PARTITION BY location ORDER BY date_opened DESC) as rn
    FROM (
        SELECT location, lift_name, MIN(updated_date) as date_opened
        FROM SKI_DATA.lifts
        WHERE lift_status = 'true'
        GROUP BY location, lift_name
    ) sub
),
recently_opened_lifts AS (
    SELECT 
        location,
        jsonb_agg(
            jsonb_build_object('name', lift_name, 'dateOpened', date_opened)
            ORDER BY date_opened DESC
        ) as recently_opened
    FROM recently_opened_lifts_ranked
    WHERE rn <= 3
    GROUP BY location
),
recently_opened_runs_ranked AS (
    SELECT 
        location,
        run_name,
        date_opened,
        ROW_NUMBER() OVER (PARTITION BY location ORDER BY date_opened DESC) as rn
    FROM (
        SELECT location, run_name, MIN(updated_date) as date_opened
        FROM SKI_DATA.runs
        WHERE run_status = 'true'
        GROUP BY location, run_name
    ) sub
),
recently_opened_runs AS (
    SELECT 
        location,
        jsonb_agg(
            jsonb_build_object('name', run_name, 'dateOpened', date_opened)
            ORDER BY date_opened DESC
        ) as recently_opened
    FROM recently_opened_runs_ranked
    WHERE rn <= 3
    GROUP BY location
)
SELECT 
    l.location,
    COALESCE(l.total_lifts, 0) as total_lifts,
    COALESCE(l.open_lifts, 0) as open_lifts,
    COALESCE(l.total_lifts, 0) - COALESCE(l.open_lifts, 0) as closed_lifts,
    COALESCE(r.total_runs, 0) as total_runs,
    COALESCE(r.open_runs, 0) as open_runs,
    COALESCE(r.total_runs, 0) - COALESCE(r.open_runs, 0) as closed_runs,
    COALESCE(rd.green_count, 0) as green_runs,
    COALESCE(rd.blue_count, 0) as blue_runs,
    COALESCE(rd.black_count, 0) as black_runs,
    COALESCE(rd.double_black_count, 0) as double_black_runs,
    COALESCE(rd.terrain_park_count, 0) as terrain_park_runs,
    -- Calculate "other" as open_runs minus all categorized runs
    COALESCE(r.open_runs, 0) - (
        COALESCE(rd.green_count, 0) + 
        COALESCE(rd.blue_count, 0) + 
        COALESCE(rd.black_count, 0) + 
        COALESCE(rd.double_black_count, 0) + 
        COALESCE(rd.terrain_park_count, 0)
    ) as other_runs,
    GREATEST(l.last_updated, r.last_updated) as last_updated,
    COALESCE(lh.history, '[]'::jsonb) as lifts_history,
    COALESCE(rh.history, '[]'::jsonb) as runs_history,
    COALESCE(rol.recently_opened, '[]'::jsonb) as recently_opened_lifts,
    COALESCE(ror.recently_opened, '[]'::jsonb) as recently_opened_runs
FROM lift_counts l
FULL OUTER JOIN run_counts r ON l.location = r.location
LEFT JOIN runs_by_difficulty rd ON COALESCE(l.location, r.location) = rd.location
LEFT JOIN lifts_history lh ON COALESCE(l.location, r.location) = lh.location
LEFT JOIN runs_history rh ON COALESCE(l.location, r.location) = rh.location
LEFT JOIN recently_opened_lifts rol ON COALESCE(l.location, r.location) = rol.location
LEFT JOIN recently_opened_runs ror ON COALESCE(l.location, r.location) = ror.location
ORDER BY COALESCE(l.location, r.location);

