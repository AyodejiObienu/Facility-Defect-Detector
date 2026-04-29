-- Facility Anomaly Detection — PostgreSQL Init
-- ─────────────────────────────────────────────

CREATE DATABASE facility_anomaly;

\c facility_anomaly;

-- Tables will be auto-created by SQLAlchemy on startup.
-- This file is for any additional setup needed.

-- Create indexes for common queries
-- (These will be created after SQLAlchemy creates the tables)
