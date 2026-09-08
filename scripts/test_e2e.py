import sys
import json
import urllib.request
import urllib.error
import time

BASE_URL = "http://localhost:8000/api/v1"

# ANSI escape codes for colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_result(test_name, success, message=""):
    if success:
        print(f"[{Colors.GREEN}PASS{Colors.RESET}] {Colors.BOLD}{test_name}{Colors.RESET} {message}")
    else:
        print(f"[{Colors.RED}FAIL{Colors.RESET}] {Colors.BOLD}{test_name}{Colors.RESET} {message}")
        
def run_test_1_registry():
    try:
        req = urllib.request.Request(f"{BASE_URL}/cameras")
        with urllib.request.urlopen(req) as res:
            if res.status != 200:
                return False, f"Expected status 200, got {res.status}"
            
            data = json.loads(res.read().decode())
            if len(data) < 1:
                return False, f"Expected cameras in registry, got {len(data)}"
            return True, f"Found {len(data)} cameras in registry"
    except Exception as e:
        return False, str(e)

def run_test_2_health():
    try:
        req = urllib.request.Request(f"{BASE_URL.split('/api')[0]}/health")
        with urllib.request.urlopen(req) as res:
            if res.status != 200:
                return False, f"Expected 200, got {res.status}"
            data = json.loads(res.read().decode())
            if data.get("status") != "ok":
                return False, "Health status not ok"
            if "database" not in data:
                return False, "Database health missing"
            return True, "Health telemetry verified (Real health endpoint reachable)"
    except Exception as e:
        return False, str(e)

def run_test_3_normalization():
    try:
        import sys
        import os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from services.ai.plate_normalizer import IndianPlateNormalizer
        
        corrupted = "GJO1ER884Z"
        expected = "GJ01ER8842"
        result = IndianPlateNormalizer.normalize(corrupted)
        if result != expected:
            return False, f"Expected {expected}, got {result}"
        return True, f"Canonical resolution to {expected} verified"
    except Exception as e:
        return False, str(e)

def run_test_4_route():
    try:
        data = json.dumps({"plate_number": "GJ01ER8842"}).encode("utf-8")
        req = urllib.request.Request(f"{BASE_URL}/tracking/route", data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as res:
            if res.status != 200:
                return False, f"Expected 200, got {res.status}"
            resp_data = json.loads(res.read().decode())
            if "waypoints" not in resp_data:
                return False, "Missing waypoints in response"
            return True, f"Reconstructed route with {len(resp_data.get('waypoints', []))} nodes"
    except Exception as e:
        return False, str(e)

def run_test_5_report():
    try:
        req = urllib.request.Request(f"{BASE_URL}/reports/export?format=csv&plate_number=GJ01ER8842")
        with urllib.request.urlopen(req) as res:
            if res.status != 200:
                return False, f"Expected 200 for CSV, got {res.status}"
            if 'Content-Disposition' not in res.headers:
                return False, "Missing Content-Disposition header in CSV"
                
        req2 = urllib.request.Request(f"{BASE_URL}/reports/export?format=pdf&plate_number=GJ01ER8842")
        with urllib.request.urlopen(req2) as res2:
            if res2.status != 200:
                return False, f"Expected 200 for PDF, got {res2.status}"
            if 'Content-Disposition' not in res2.headers:
                return False, "Missing Content-Disposition header in PDF"
                
        return True, "CSV and PDF report generations succeeded"
    except Exception as e:
        return False, str(e)

def run_test_6_stream():
    try:
        # Get first camera ID
        req = urllib.request.Request(f"{BASE_URL}/cameras")
        with urllib.request.urlopen(req) as res:
            cameras = json.loads(res.read().decode())
            if not cameras:
                return False, "No cameras available to test stream"
            cam_id = cameras[0]['id']
            
        req2 = urllib.request.Request(f"{BASE_URL}/stream/simulate-feed/{cam_id}")
        with urllib.request.urlopen(req2) as res2:
            if res2.status != 200:
                return False, f"Expected 200 for stream, got {res2.status}"
            # Read first few bytes to verify multipart stream
            chunk = res2.read(100)
            if b'--frame' not in chunk:
                return False, "Did not receive multipart boundary in stream"
            
        return True, "MJPEG boundary bytes verified"
    except Exception as e:
        return False, str(e)

def main():
    print(f"{Colors.BOLD}=================================================={Colors.RESET}")
    print(f"{Colors.BOLD}  VIGILIS AUTOMATED END-TO-END SMOKE TEST SUITE   {Colors.RESET}")
    print(f"{Colors.BOLD}=================================================={Colors.RESET}")
    print("Ensuring services are reachable...\n")
    
    # Wait for service to be up
    retries = 5
    while retries > 0:
        try:
            urllib.request.urlopen(f"{BASE_URL}/cameras")
            break
        except:
            retries -= 1
            time.sleep(2)
            
    if retries == 0:
        print(f"[{Colors.RED}FATAL{Colors.RESET}] API is not reachable at {BASE_URL}. Ensure servers are running.")
        sys.exit(1)

    tests = [
        ("[TEST 1] Camera Registry", run_test_1_registry),
        ("[TEST 2] Health Telemetry", run_test_2_health),
        ("[TEST 3] Plate Normalization", run_test_3_normalization),
        ("[TEST 4] Route Reconstruction", run_test_4_route),
        ("[TEST 5] Report Generation", run_test_5_report),
        ("[TEST 6] Video Stream Availability", run_test_6_stream),
    ]

    all_passed = True
    for name, test_func in tests:
        success, msg = test_func()
        print_result(name, success, f"- {msg}")
        if not success:
            all_passed = False

    print(f"\n{Colors.BOLD}=================================================={Colors.RESET}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED SUCCESSFULLY!{Colors.RESET} System is ready for production.")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}SOME TESTS FAILED.{Colors.RESET} Please review the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
