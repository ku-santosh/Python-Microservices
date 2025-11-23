-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS recsui;

-- Create table perspectives
CREATE TABLE IF NOT EXISTS recsui.perspectives (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    layout_name VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255) NOT NULL,
    column_state JSONB DEFAULT '[]',
    sort_model JSONB DEFAULT '[]',
    filter_model JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_perspectives_username
    ON recsui.perspectives (username);

CREATE INDEX IF NOT EXISTS idx_perspectives_layout
    ON recsui.perspectives (layout_name);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_perspectives_updated_at ON recsui.perspectives;

CREATE TRIGGER update_perspectives_updated_at
BEFORE UPDATE ON recsui.perspectives
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

-- Seed Data
INSERT INTO recsui.perspectives (username, layout_name, updated_by, column_state, sort_model, filter_model)
VALUES 
(
    'demo_user',
    'reconciliationsView',
    'admin@demo.com',
    '[{
        "name": "Default001",
        "view": "customerMode",
        "defaultColumns": ["riskEventType", "priority", "businessUnit"],
        "default": true
    }]',
    '[{
        "colId": "priority",
        "sort": "asc"
    }]',
    '[{
        "name": "Filter001",
        "view": "customerMode",
        "filters": {
            "riskEventType": {"type": "contains", "filter": "High"}
        },
        "default": true
    }]'
);

INSERT INTO recsui.perspectives (username, layout_name, updated_by, column_state, sort_model, filter_model)
VALUES 
(
    'test_user',
    'analyticsView',
    'qa@demo.com',
    '[{
        "name": "Analytics001",
        "view": "analyticsMode",
        "defaultColumns": ["cif", "reAmount", "reAmountCurrency"],
        "default": true
    }]',
    '[{
        "colId": "reAmount",
        "sort": "desc"
    }]',
    '[{
        "name": "Filter002",
        "view": "analyticsMode",
        "filters": {
            "reAmount": {"type": "greaterThan", "filter": 10000}
        },
        "default": false
    }]'
);
