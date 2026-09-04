-- VIGILIS Initial Seed Data

-- Departments
INSERT INTO departments (id, name, description, region) VALUES
(uuid_generate_v4(), 'Home Department', 'Police and Internal Security', 'Statewide'),
(uuid_generate_v4(), 'RTO Gujarat', 'Regional Transport Office', 'Statewide'),
(uuid_generate_v4(), 'Food & Civil Supplies', 'PDS and Godowns', 'Statewide'),
(uuid_generate_v4(), 'Urban Development', 'Municipal Corporations', 'Statewide');

-- Watchlists
INSERT INTO watchlists (id, name, category, description) VALUES
(uuid_generate_v4(), 'eGujCop Wanted Persons / Stolen Vehicles', 'STOLEN_VEHICLE', 'Statewide stolen vehicles and wanted suspects'),
(uuid_generate_v4(), 'VAHAN Blacklist / Tax Default', 'BLACKLISTED_VEHICLE', 'Vehicles with unpaid taxes or blacklisted'),
(uuid_generate_v4(), 'High-Risk Surveillance Suspects', 'WANTED_PERSON', 'Suspects under active high-risk surveillance');

-- Watchlist Entries
INSERT INTO watchlist_entries (id, watchlist_id, entity_type, entity_value, notes)
SELECT uuid_generate_v4(), id, 'VEHICLE', 'GJ01ER8842', 'White Toyota Fortuner - Marked STOLEN in eGujCop' 
FROM watchlists WHERE name = 'eGujCop Wanted Persons / Stolen Vehicles' LIMIT 1;

INSERT INTO watchlist_entries (id, watchlist_id, entity_type, entity_value, notes)
SELECT uuid_generate_v4(), id, 'VEHICLE', 'GJ05XY9876', 'Suspect in recent robbery' 
FROM watchlists WHERE name = 'High-Risk Surveillance Suspects' LIMIT 1;

-- Roles
INSERT INTO roles (id, name, description) VALUES
(uuid_generate_v4(), 'SUPER_ADMIN', 'Full system access'),
(uuid_generate_v4(), 'POLICE', 'Standard police access'),
(uuid_generate_v4(), 'TRAFFIC_POLICE', 'Traffic monitoring access'),
(uuid_generate_v4(), 'RTO', 'RTO specific access'),
(uuid_generate_v4(), 'INVESTIGATOR', 'Access to historical tracking and events'),
(uuid_generate_v4(), 'DEPARTMENT_VIEWER', 'View only access for specific department');

-- Cameras
INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad SG Highway Toll', ST_SetSRID(ST_MakePoint(72.5255, 23.0312), 4326), 'Ahmedabad SG Highway Toll, Gujarat', 'RTSP', 'rtsp://demo:demo@10.0.0.0:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Gandhinagar CH-0', ST_SetSRID(ST_MakePoint(72.6369, 23.2156), 4326), 'Gandhinagar CH-0, Gujarat', 'RTSP', 'rtsp://demo:demo@10.0.0.1:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Vadodara Express Highway Start', ST_SetSRID(ST_MakePoint(73.1812, 22.3072), 4326), 'Vadodara Express Highway Start, Gujarat', 'HLS_RELAY', 'rtsp://demo:demo@10.0.0.2:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Vadodara Express Highway End', ST_SetSRID(ST_MakePoint(73.1312, 22.2572), 4326), 'Vadodara Express Highway End, Gujarat', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.3:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Bharuch Narmada Bridge', ST_SetSRID(ST_MakePoint(72.9959, 21.7051), 4326), 'Bharuch Narmada Bridge, Gujarat', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.4:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Surat Kadodara Checkpost', ST_SetSRID(ST_MakePoint(72.8311, 21.1702), 4326), 'Surat Kadodara Checkpost, Gujarat', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.5:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dahod Home Cam 7', ST_SetSRID(ST_MakePoint(74.2199, 22.8423), 4326), 'Location 7, Dahod', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.6:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad RTO Cam 8', ST_SetSRID(ST_MakePoint(72.5775, 23.0327), 4326), 'Location 8, Ahmedabad', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.7:554/stream', '1080p', 30, 'H.265', 'OFFLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dahod Urban Cam 9', ST_SetSRID(ST_MakePoint(74.2976, 22.8422), 4326), 'Location 9, Dahod', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.8:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad RTO Cam 10', ST_SetSRID(ST_MakePoint(72.5429, 23.0003), 4326), 'Location 10, Ahmedabad', 'VENDOR_SDK_DAHUA', 'rtsp://demo:demo@10.0.0.9:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Valsad Food Cam 11', ST_SetSRID(ST_MakePoint(72.9201, 20.5872), 4326), 'Location 11, Valsad', 'RTSP', 'rtsp://demo:demo@10.0.0.10:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Jamnagar Food Cam 12', ST_SetSRID(ST_MakePoint(70.0202, 22.4666), 4326), 'Location 12, Jamnagar', 'RTSP', 'rtsp://demo:demo@10.0.0.11:554/stream', '1080p', 30, 'H.265', 'DEGRADED'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Somnath Home Cam 13', ST_SetSRID(ST_MakePoint(70.4131, 20.9389), 4326), 'Location 13, Somnath', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.12:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Valsad Food Cam 14', ST_SetSRID(ST_MakePoint(72.8888, 20.6197), 4326), 'Location 14, Valsad', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.13:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Surat Food Cam 15', ST_SetSRID(ST_MakePoint(72.8191, 21.2068), 4326), 'Location 15, Surat', 'RTSP', 'rtsp://demo:demo@10.0.0.14:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Somnath Food Cam 16', ST_SetSRID(ST_MakePoint(70.4182, 20.8915), 4326), 'Location 16, Somnath', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.15:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dahod Home Cam 17', ST_SetSRID(ST_MakePoint(74.2896, 22.8004), 4326), 'Location 17, Dahod', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.16:554/stream', '1080p', 30, 'H.265', 'DEGRADED'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Surat Urban Cam 18', ST_SetSRID(ST_MakePoint(72.8451, 21.2192), 4326), 'Location 18, Surat', 'VENDOR_SDK_DAHUA', 'rtsp://demo:demo@10.0.0.17:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dwarka RTO Cam 19', ST_SetSRID(ST_MakePoint(68.9217, 22.2171), 4326), 'Location 19, Dwarka', 'HLS_RELAY', 'rtsp://demo:demo@10.0.0.18:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Jamnagar Urban Cam 20', ST_SetSRID(ST_MakePoint(70.1020, 22.4418), 4326), 'Location 20, Jamnagar', 'HLS_RELAY', 'rtsp://demo:demo@10.0.0.19:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dahod Food Cam 21', ST_SetSRID(ST_MakePoint(74.3052, 22.8332), 4326), 'Location 21, Dahod', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.20:554/stream', '1080p', 30, 'H.265', 'DEGRADED'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dahod Urban Cam 22', ST_SetSRID(ST_MakePoint(74.2912, 22.7973), 4326), 'Location 22, Dahod', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.21:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dwarka Food Cam 23', ST_SetSRID(ST_MakePoint(68.9584, 22.2840), 4326), 'Location 23, Dwarka', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.22:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Surat RTO Cam 24', ST_SetSRID(ST_MakePoint(72.7858, 21.1293), 4326), 'Location 24, Surat', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.23:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad RTO Cam 25', ST_SetSRID(ST_MakePoint(72.5278, 23.0147), 4326), 'Location 25, Ahmedabad', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.24:554/stream', '1080p', 30, 'H.265', 'DEGRADED'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Somnath Urban Cam 26', ST_SetSRID(ST_MakePoint(70.4373, 20.9531), 4326), 'Location 26, Somnath', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.25:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad Home Cam 27', ST_SetSRID(ST_MakePoint(72.5554, 23.0494), 4326), 'Location 27, Ahmedabad', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.26:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Jamnagar Urban Cam 28', ST_SetSRID(ST_MakePoint(70.0799, 22.4210), 4326), 'Location 28, Jamnagar', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.27:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dahod Food Cam 29', ST_SetSRID(ST_MakePoint(74.2273, 22.8341), 4326), 'Location 29, Dahod', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.28:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dahod Food Cam 30', ST_SetSRID(ST_MakePoint(74.2541, 22.8032), 4326), 'Location 30, Dahod', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.29:554/stream', '1080p', 30, 'H.265', 'OFFLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Surat Home Cam 31', ST_SetSRID(ST_MakePoint(72.7923, 21.1691), 4326), 'Location 31, Surat', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.30:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Jamnagar Food Cam 32', ST_SetSRID(ST_MakePoint(70.0644, 22.4448), 4326), 'Location 32, Jamnagar', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.31:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad Home Cam 33', ST_SetSRID(ST_MakePoint(72.5747, 23.0703), 4326), 'Location 33, Ahmedabad', 'VENDOR_SDK_DAHUA', 'rtsp://demo:demo@10.0.0.32:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Surat RTO Cam 34', ST_SetSRID(ST_MakePoint(72.8339, 21.1367), 4326), 'Location 34, Surat', 'VENDOR_SDK_DAHUA', 'rtsp://demo:demo@10.0.0.33:554/stream', '1080p', 30, 'H.265', 'OFFLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dwarka Urban Cam 35', ST_SetSRID(ST_MakePoint(68.9875, 22.2697), 4326), 'Location 35, Dwarka', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.34:554/stream', '1080p', 30, 'H.265', 'OFFLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dahod Food Cam 36', ST_SetSRID(ST_MakePoint(74.2605, 22.8483), 4326), 'Location 36, Dahod', 'VENDOR_SDK_DAHUA', 'rtsp://demo:demo@10.0.0.35:554/stream', '1080p', 30, 'H.265', 'DEGRADED'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dwarka Urban Cam 37', ST_SetSRID(ST_MakePoint(68.9523, 22.2167), 4326), 'Location 37, Dwarka', 'RTSP', 'rtsp://demo:demo@10.0.0.36:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dwarka RTO Cam 38', ST_SetSRID(ST_MakePoint(68.9893, 22.1949), 4326), 'Location 38, Dwarka', 'VENDOR_SDK_HIKVISION', 'rtsp://demo:demo@10.0.0.37:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad RTO Cam 39', ST_SetSRID(ST_MakePoint(72.5285, 23.0585), 4326), 'Location 39, Ahmedabad', 'RTSP', 'rtsp://demo:demo@10.0.0.38:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Surat Food Cam 40', ST_SetSRID(ST_MakePoint(72.8534, 21.1741), 4326), 'Location 40, Surat', 'VENDOR_SDK_DAHUA', 'rtsp://demo:demo@10.0.0.39:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Dwarka Urban Cam 41', ST_SetSRID(ST_MakePoint(68.9375, 22.2749), 4326), 'Location 41, Dwarka', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.40:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad Urban Cam 42', ST_SetSRID(ST_MakePoint(72.6078, 23.0136), 4326), 'Location 42, Ahmedabad', 'HLS_RELAY', 'rtsp://demo:demo@10.0.0.41:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad Home Cam 43', ST_SetSRID(ST_MakePoint(72.6015, 23.0453), 4326), 'Location 43, Ahmedabad', 'RTSP', 'rtsp://demo:demo@10.0.0.42:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad RTO Cam 44', ST_SetSRID(ST_MakePoint(72.5354, 23.0261), 4326), 'Location 44, Ahmedabad', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.43:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Surat Food Cam 45', ST_SetSRID(ST_MakePoint(72.7886, 21.2076), 4326), 'Location 45, Surat', 'VENDOR_SDK_DAHUA', 'rtsp://demo:demo@10.0.0.44:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Food & Civil Supplies' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Valsad Home Cam 46', ST_SetSRID(ST_MakePoint(72.9678, 20.6491), 4326), 'Location 46, Valsad', 'RTSP', 'rtsp://demo:demo@10.0.0.45:554/stream', '1080p', 30, 'H.265', 'DEGRADED'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Ahmedabad RTO Cam 47', ST_SetSRID(ST_MakePoint(72.5428, 23.0211), 4326), 'Location 47, Ahmedabad', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.46:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'RTO Gujarat' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Somnath Home Cam 48', ST_SetSRID(ST_MakePoint(70.3902, 20.8562), 4326), 'Location 48, Somnath', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.47:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Home Department' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Valsad Urban Cam 49', ST_SetSRID(ST_MakePoint(72.9573, 20.6189), 4326), 'Location 49, Valsad', 'HLS_RELAY', 'rtsp://demo:demo@10.0.0.48:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

INSERT INTO cameras (id, department_id, name, location, address, protocol, url, resolution, fps, codec, status)
SELECT uuid_generate_v4(), id, 'Valsad Urban Cam 50', ST_SetSRID(ST_MakePoint(72.9811, 20.5789), 4326), 'Location 50, Valsad', 'ONVIF_PROFILE_S', 'rtsp://demo:demo@10.0.0.49:554/stream', '1080p', 30, 'H.265', 'ONLINE'
FROM departments WHERE name = 'Urban Development' LIMIT 1;

