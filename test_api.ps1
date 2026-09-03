$seed = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/watchlists/seed"
Write-Host "Seed result:" ($seed | ConvertTo-Json -Depth 10)

$eventJson = '{"event_type": "PLATE_CONFIRMED", "camera_id": "TEST_CAM", "payload": {"track_id": "TEST_TRACK_001", "plate": {"normalized_text": "GJ01AB1234", "confidence": 0.98, "raw_text": "GJ01AB1234"}}}'
$event1 = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/internal/events/" -ContentType "application/json" -Body $eventJson
Write-Host "Event 1 result:" ($event1 | ConvertTo-Json -Depth 10)

$alerts1 = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/alerts/"
Write-Host "Alerts 1 result:" ($alerts1 | ConvertTo-Json -Depth 10)

$event2 = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/internal/events/" -ContentType "application/json" -Body $eventJson
Write-Host "Event 2 result:" ($event2 | ConvertTo-Json -Depth 10)

$alerts2 = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/alerts/"
Write-Host "Alerts 2 result:" ($alerts2 | ConvertTo-Json -Depth 10)
