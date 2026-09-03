-- VIGILIS Initial Seed Data

-- Insert 26 Departments (A-Z for simplicity in prototype)
INSERT INTO departments (id, name, description, region) VALUES
(uuid_generate_v4(), 'Ahmedabad City Police', 'Ahmedabad City Police Department', 'Ahmedabad'),
(uuid_generate_v4(), 'Surat City Police', 'Surat City Police Department', 'Surat'),
(uuid_generate_v4(), 'Vadodara City Police', 'Vadodara City Police Department', 'Vadodara'),
(uuid_generate_v4(), 'Rajkot City Police', 'Rajkot City Police Department', 'Rajkot'),
(uuid_generate_v4(), 'Bhavnagar Police', 'Bhavnagar District Police', 'Bhavnagar'),
(uuid_generate_v4(), 'Jamnagar Police', 'Jamnagar District Police', 'Jamnagar'),
(uuid_generate_v4(), 'Junagadh Police', 'Junagadh District Police', 'Junagadh'),
(uuid_generate_v4(), 'Gandhinagar Police', 'Gandhinagar District Police', 'Gandhinagar'),
(uuid_generate_v4(), 'Anand Police', 'Anand District Police', 'Anand'),
(uuid_generate_v4(), 'Kheda Police', 'Kheda District Police', 'Kheda'),
(uuid_generate_v4(), 'Panchmahal Police', 'Panchmahal District Police', 'Panchmahal'),
(uuid_generate_v4(), 'Dahod Police', 'Dahod District Police', 'Dahod'),
(uuid_generate_v4(), 'Mehsana Police', 'Mehsana District Police', 'Mehsana'),
(uuid_generate_v4(), 'Patan Police', 'Patan District Police', 'Patan'),
(uuid_generate_v4(), 'Banaskantha Police', 'Banaskantha District Police', 'Banaskantha'),
(uuid_generate_v4(), 'Sabarkantha Police', 'Sabarkantha District Police', 'Sabarkantha'),
(uuid_generate_v4(), 'Aravalli Police', 'Aravalli District Police', 'Aravalli'),
(uuid_generate_v4(), 'Mahisagar Police', 'Mahisagar District Police', 'Mahisagar'),
(uuid_generate_v4(), 'Chhota Udepur Police', 'Chhota Udepur District Police', 'Chhota Udepur'),
(uuid_generate_v4(), 'Narmada Police', 'Narmada District Police', 'Narmada'),
(uuid_generate_v4(), 'Bharuch Police', 'Bharuch District Police', 'Bharuch'),
(uuid_generate_v4(), 'Navsari Police', 'Navsari District Police', 'Navsari'),
(uuid_generate_v4(), 'Dang Police', 'Dang District Police', 'Dang'),
(uuid_generate_v4(), 'Tapi Police', 'Tapi District Police', 'Tapi'),
(uuid_generate_v4(), 'Valsad Police', 'Valsad District Police', 'Valsad'),
(uuid_generate_v4(), 'Kutch Police', 'Kutch District Police', 'Kutch');

-- Insert Watchlist Categories
INSERT INTO watchlists (id, name, category, description) VALUES
(uuid_generate_v4(), 'Stolen Vehicles (Statewide)', 'STOLEN_VEHICLE', 'Vehicles reported stolen across the state'),
(uuid_generate_v4(), 'Wanted Suspects', 'WANTED_PERSON', 'Vehicles linked to wanted suspects'),
(uuid_generate_v4(), 'Blacklisted Carriers', 'BLACKLISTED_VEHICLE', 'Commercial vehicles blacklisted by RTO');

-- Insert Watchlist Entries (Demo Data)
INSERT INTO watchlist_entries (id, watchlist_id, entity_type, entity_value, notes)
SELECT uuid_generate_v4(), id, 'VEHICLE', 'GJ01AB1234', 'Reported stolen on 2026-09-01' 
FROM watchlists WHERE category = 'STOLEN_VEHICLE' LIMIT 1;

INSERT INTO watchlist_entries (id, watchlist_id, entity_type, entity_value, notes)
SELECT uuid_generate_v4(), id, 'VEHICLE', 'GJ05XY9876', 'Suspect in recent robbery' 
FROM watchlists WHERE category = 'WANTED_PERSON' LIMIT 1;

-- Insert Roles
INSERT INTO roles (id, name, description) VALUES
(uuid_generate_v4(), 'SUPER_ADMIN', 'Full system access'),
(uuid_generate_v4(), 'POLICE', 'Standard police access'),
(uuid_generate_v4(), 'TRAFFIC_POLICE', 'Traffic monitoring access'),
(uuid_generate_v4(), 'RTO', 'RTO specific access'),
(uuid_generate_v4(), 'INVESTIGATOR', 'Access to historical tracking and events'),
(uuid_generate_v4(), 'DEPARTMENT_VIEWER', 'View only access for specific department');

-- Insert Demo Cameras for Ahmedabad
INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT 
    uuid_generate_v4(), 
    id, 
    'SG Highway Junction 1', 
    ST_SetSRID(ST_MakePoint(72.5255, 23.0312), 4326), 
    'SG Highway, Ahmedabad', 
    'RTSP', 
    'rtsp://demo:demo@192.168.1.100:554/stream1', 
    '1080p', 
    25, 
    'H.264', 
    'ONLINE'
FROM departments WHERE name = 'Ahmedabad City Police' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT 
    uuid_generate_v4(), 
    id, 
    'Ashram Road Cross', 
    ST_SetSRID(ST_MakePoint(72.5714, 23.0225), 4326), 
    'Ashram Road, Ahmedabad', 
    'RTSP', 
    'rtsp://demo:demo@192.168.1.101:554/stream1', 
    '720p', 
    15, 
    'H.265', 
    'OFFLINE'
FROM departments WHERE name = 'Ahmedabad City Police' LIMIT 1;
