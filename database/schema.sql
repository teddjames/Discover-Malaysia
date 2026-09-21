PRAGMA foreign_keys = ON;


-- ==========================================
-- DESTINATIONS
-- ==========================================

CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    image TEXT
);


-- ==========================================
-- ATTRACTIONS
-- ==========================================

CREATE TABLE IF NOT EXISTS attractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    destination_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,

    category TEXT,
    description TEXT,

    rating REAL DEFAULT 0,
    price REAL DEFAULT 0,

    image TEXT,

    FOREIGN KEY (destination_id)
        REFERENCES destinations(id)
        ON DELETE CASCADE
);


-- ==========================================
-- HOTELS
-- ==========================================

CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    destination_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,

    type TEXT,

    description TEXT,

    rating REAL DEFAULT 0,

    price_per_night REAL DEFAULT 0,

    image TEXT,

    FOREIGN KEY (destination_id)
        REFERENCES destinations(id)
        ON DELETE CASCADE
);


-- ==========================================
-- ACTIVITIES
-- ==========================================

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    destination_id INTEGER NOT NULL,

    name TEXT NOT NULL,

    category TEXT,

    description TEXT,

    duration TEXT,

    price REAL DEFAULT 0,

    rating REAL DEFAULT 0,

    image TEXT,

    FOREIGN KEY (destination_id)
        REFERENCES destinations(id)
        ON DELETE CASCADE
);


-- ==========================================
-- TRANSPORT ROUTES
-- ==========================================

CREATE TABLE IF NOT EXISTS transport_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    origin TEXT NOT NULL,
    destination TEXT NOT NULL,

    transport_type TEXT NOT NULL,

    duration_minutes INTEGER,

    min_price REAL,
    max_price REAL,

    notes TEXT
);