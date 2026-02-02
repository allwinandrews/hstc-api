-- Database initialization for gates and directed routes.
-- Includes seed data used by integration tests and local dev.
-- =========================
-- Gates (nodes)
-- =========================
CREATE TABLE IF NOT EXISTS gates (
    code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- =========================
-- Routes (directed edges; weights are per direction)
-- =========================
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    from_code VARCHAR(3) NOT NULL REFERENCES gates(code) ON DELETE CASCADE,
    to_code   VARCHAR(3) NOT NULL REFERENCES gates(code) ON DELETE CASCADE,
    hu_distance INTEGER NOT NULL CHECK (hu_distance > 0),
    CONSTRAINT uq_route UNIQUE (from_code, to_code)
);

-- =========================
-- Seed gates
-- =========================
INSERT INTO gates (code, name) VALUES
    ('SOL', 'Sol'),
    ('PRX', 'Proxima'),
    ('SIR', 'Sirius'),
    ('CAS', 'Castor'),
    ('PRO', 'Procyon'),
    ('DEN', 'Denebula'),
    ('RAN', 'Ran'),
    ('ARC', 'Arcturus'),
    ('FOM', 'Fomalhaut'),
    ('ALT', 'Altair'),
    ('VEG', 'Vega'),
    ('ALD', 'Aldermain'),
    ('ALS', 'Alshain')
ON CONFLICT (code) DO NOTHING;

-- =========================
-- Seed routes (DIRECTED)
-- =========================
INSERT INTO routes (from_code, to_code, hu_distance) VALUES
    -- SOL
    ('SOL', 'RAN', 100),
    ('SOL', 'PRX', 90),
    ('SOL', 'SIR', 100),
    ('SOL', 'ARC', 200),
    ('SOL', 'ALD', 250),

    -- PRX
    ('PRX', 'SOL', 90),
    ('PRX', 'SIR', 100),
    ('PRX', 'ALT', 150),

    -- SIR
    ('SIR', 'SOL', 80),
    ('SIR', 'PRX', 10),
    ('SIR', 'CAS', 200),

    -- CAS
    ('CAS', 'SIR', 200),
    ('CAS', 'PRO', 120),

    -- PRO
    ('PRO', 'CAS', 80),

    -- DEN
    ('DEN', 'PRO', 5),
    ('DEN', 'ARC', 2),
    ('DEN', 'FOM', 8),
    ('DEN', 'RAN', 100),
    ('DEN', 'ALD', 3),

    -- RAN
    ('RAN', 'SOL', 100),

    -- ARC
    ('ARC', 'SOL', 500),
    ('ARC', 'DEN', 120),

    -- FOM
    ('FOM', 'PRX', 10),
    ('FOM', 'DEN', 20),
    ('FOM', 'ALS', 9),

    -- ALT
    ('ALT', 'FOM', 140),
    ('ALT', 'VEG', 220),

    -- VEG
    ('VEG', 'ARC', 220),
    ('VEG', 'ALD', 580),

    -- ALD
    ('ALD', 'SOL', 200),
    ('ALD', 'ALS', 160),
    ('ALD', 'VEG', 320),

    -- ALS
    ('ALS', 'ALT', 1),
    ('ALS', 'ALD', 1)
ON CONFLICT (from_code, to_code) DO NOTHING;
