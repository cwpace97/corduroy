DROP TABLE IF EXISTS SKI_DATA.ref__lift_mapping;
CREATE TABLE SKI_DATA.ref__lift_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lift_type TEXT NOT NULL,
    lift_category TEXT NOT NULL,
    lift_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO SKI_DATA.ref__lift_mapping (
    lift_type, lift_category, lift_size
) 
VALUES
    ('Double', 'Double', 2),
    ('Triple', 'Triple', 3),
    ('Six Person', 'Six', 6),
    ('Quad Chair', 'Quad', 4),
    ('Double Chair', 'Double', 2),
    ('Gondola', 'Gondola', 8),
    ('Surface', 'Carpet', 1),
    ('Triple Chair', 'Triple', 3),
    ('Carpet', 'Carpet', 1),
    ('Six-Person Chair', 'Six', 6),
    ('Magic Carpet', 'Carpet', 1),
    ('Quad', 'Quad', 4);