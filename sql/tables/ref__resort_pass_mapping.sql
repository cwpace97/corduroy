DROP TABLE IF EXISTS SKI_DATA.ref__resort_pass_mapping;
CREATE TABLE SKI_DATA.ref__resort_pass_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resort_name TEXT NOT NULL,
    resort_pass TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO SKI_DATA.ref__resort_pass_mapping (
    resort_name, resort_pass
) 
VALUES
('arapahoebasin', 'ikon'),
('breckenridge', 'epic'),
('copper', 'ikon'),
('crested butte', 'epic'),
('keystone', 'epic'),
('loveland', 'indy'),
('monarch', 'indy'),
('purgatory', 'indy'),
('steamboat', 'ikon'),
('telluride', 'epic'),
('vail', 'epic'),
('winterpark', 'ikon');