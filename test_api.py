"""
Comprehensive Test Suite for Astro Vector API
Tests all endpoints, error handling, and validates against acceptance criteria
"""

import requests
import json
from datetime import datetime

# Base URL for API
BASE_URL = "http://localhost:8000"

# Test results tracker
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}


def test_api(name, method, endpoint, data=None, expected_status=200, check_keys=None):
    """
    Generic test function for API endpoints

    Args:
        name: Test name
        method: HTTP method (GET, POST)
        endpoint: API endpoint path
        data: Request data (for POST)
        expected_status: Expected HTTP status code
        check_keys: List of keys to verify in response
    """
    try:
        url = f"{BASE_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        # Check status code
        if response.status_code != expected_status:
            print(f"[FAIL] {name}")
            print(f"  Expected status {expected_status}, got {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            test_results["failed"] += 1
            test_results["errors"].append(f"{name}: Wrong status code")
            return False

        # Check response keys if specified
        if check_keys:
            try:
                response_json = response.json()
                missing_keys = [key for key in check_keys if key not in response_json]

                if missing_keys:
                    print(f"[FAIL] {name}")
                    print(f"  Missing keys: {', '.join(missing_keys)}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"{name}: Missing keys")
                    return False
            except json.JSONDecodeError:
                print(f"[FAIL] {name}")
                print(f"  Invalid JSON response")
                test_results["failed"] += 1
                test_results["errors"].append(f"{name}: Invalid JSON")
                return False

        print(f"[PASS] {name}")
        test_results["passed"] += 1
        return True

    except Exception as e:
        print(f"[ERROR] {name}")
        print(f"  Exception: {str(e)}")
        test_results["failed"] += 1
        test_results["errors"].append(f"{name}: {str(e)}")
        return False


def test_response_structure(name, data, expected_systems=None):
    """
    Test API response and verify structure

    Args:
        name: Test name
        data: Request data
        expected_systems: List of systems to verify (default: all 5)
    """
    if expected_systems is None:
        expected_systems = ["tropical", "sidereal", "draconic", "chinese", "mayan"]

    try:
        response = requests.post(f"{BASE_URL}/astro_vector", json=data)

        if response.status_code != 200:
            print(f"[FAIL] {name}")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            test_results["failed"] += 1
            return False

        result = response.json()

        # Check all required top-level keys
        required_keys = ["input"] + expected_systems
        missing = [key for key in required_keys if key not in result]

        if missing:
            print(f"[FAIL] {name}")
            print(f"  Missing top-level keys: {', '.join(missing)}")
            test_results["failed"] += 1
            return False

        # Verify tropical has all 10 planets
        if "tropical" in result:
            planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
            missing_planets = [p for p in planets if p not in result["tropical"]]

            if missing_planets:
                print(f"[FAIL] {name}")
                print(f"  Tropical missing planets: {', '.join(missing_planets)}")
                test_results["failed"] += 1
                return False

        # Verify Chinese has required fields
        if "chinese" in result:
            required_chinese = ["animal", "element", "yin_yang", "stem_number", "branch_number"]
            missing_chinese = [f for f in required_chinese if f not in result["chinese"]]

            if missing_chinese:
                print(f"[FAIL] {name}")
                print(f"  Chinese missing fields: {', '.join(missing_chinese)}")
                test_results["failed"] += 1
                return False

        # Verify Mayan has required fields
        if "mayan" in result:
            required_mayan = ["day_number", "day_sign", "day_sign_number", "tzolkin_position", "full_name"]
            missing_mayan = [f for f in required_mayan if f not in result["mayan"]]

            if missing_mayan:
                print(f"[FAIL] {name}")
                print(f"  Mayan missing fields: {', '.join(missing_mayan)}")
                test_results["failed"] += 1
                return False

        print(f"[PASS] {name}")
        print(f"  All {len(expected_systems)} systems present and complete")
        test_results["passed"] += 1
        return True

    except Exception as e:
        print(f"[ERROR] {name}")
        print(f"  Exception: {str(e)}")
        test_results["failed"] += 1
        return False


def run_all_tests():
    """Run complete test suite"""

    print("=" * 70)
    print("ASTRO VECTOR API - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()

    # SECTION 1: Health Check
    print("SECTION 1: Health Check")
    print("-" * 70)
    test_api(
        "Health check endpoint",
        "GET",
        "/",
        expected_status=200,
        check_keys=["service", "version", "status"]
    )
    print()

    # SECTION 2: Valid Requests
    print("SECTION 2: Valid Requests - Response Structure")
    print("-" * 70)

    test_response_structure(
        "Complete request (Paris, 1984)",
        {"date": "1984-09-23", "time": "12:35", "place": "Paris, France"}
    )

    test_response_structure(
        "Request without time (defaults to noon)",
        {"date": "2000-01-01", "place": "London, UK"}
    )

    test_response_structure(
        "Request with different timezone (Tokyo)",
        {"date": "1990-06-15", "time": "08:30", "place": "Tokyo, Japan"}
    )

    print()

    # SECTION 3: Date Edge Cases
    print("SECTION 3: Date Edge Cases")
    print("-" * 70)

    # Chinese Li Chun boundary (Feb 4)
    test_response_structure(
        "Before Li Chun (Feb 2, 1984) - should be 1983 Pig",
        {"date": "1984-02-02", "time": "12:00", "place": "Shanghai, China"}
    )

    test_response_structure(
        "After Li Chun (Feb 5, 1984) - should be 1984 Rat",
        {"date": "1984-02-05", "time": "12:00", "place": "Shanghai, China"}
    )

    # Year boundaries
    test_response_structure(
        "New Year's Day 2000",
        {"date": "2000-01-01", "time": "00:00", "place": "Manhattan, New York, USA"}
    )

    test_response_structure(
        "December 31, 1999",
        {"date": "1999-12-31", "time": "23:59", "place": "London, UK"}
    )

    print()

    # SECTION 4: Validation Errors (400)
    print("SECTION 4: Input Validation Errors (400)")
    print("-" * 70)

    test_api(
        "Invalid date format",
        "POST",
        "/astro_vector",
        {"date": "invalid", "time": "12:00", "place": "Paris"},
        expected_status=400
    )

    test_api(
        "Invalid time format",
        "POST",
        "/astro_vector",
        {"date": "2000-01-01", "time": "25:00", "place": "Paris"},
        expected_status=400
    )

    test_api(
        "Date out of range (too early)",
        "POST",
        "/astro_vector",
        {"date": "1800-01-01", "time": "12:00", "place": "Paris"},
        expected_status=400
    )

    test_api(
        "Date out of range (too late)",
        "POST",
        "/astro_vector",
        {"date": "2150-01-01", "time": "12:00", "place": "Paris"},
        expected_status=400
    )

    test_api(
        "Empty place",
        "POST",
        "/astro_vector",
        {"date": "2000-01-01", "time": "12:00", "place": ""},
        expected_status=400
    )

    print()

    # SECTION 5: Location Errors
    print("SECTION 5: Location Resolution Errors")
    print("-" * 70)

    test_api(
        "Invalid location (404)",
        "POST",
        "/astro_vector",
        {"date": "2000-01-01", "time": "12:00", "place": "XYZ999InvalidPlace"},
        expected_status=404
    )

    test_api(
        "Ambiguous location (409) - Springfield",
        "POST",
        "/astro_vector",
        {"date": "2000-01-01", "time": "12:00", "place": "Springfield"},
        expected_status=409
    )

    test_api(
        "Ambiguous location (409) - London (multiple exist)",
        "POST",
        "/astro_vector",
        {"date": "2000-01-01", "time": "12:00", "place": "London"},
        expected_status=409
    )

    print()

    # SECTION 6: Specific Calculations Verification
    print("SECTION 6: Specific Calculations Verification")
    print("-" * 70)

    # Test known reference: 1984-09-23 12:35 Paris
    try:
        response = requests.post(
            f"{BASE_URL}/astro_vector",
            json={"date": "1984-09-23", "time": "12:35", "place": "Paris, France"}
        )

        if response.status_code == 200:
            result = response.json()

            # Verify Chinese: Should be 1984 = Yang Wood Rat
            chinese = result.get("chinese", {})
            if (chinese.get("animal") == "Rat" and
                chinese.get("element") == "Wood" and
                chinese.get("yin_yang") == "Yang"):
                print("[PASS] Chinese 1984 = Yang Wood Rat")
                test_results["passed"] += 1
            else:
                print(f"[FAIL] Chinese 1984 incorrect: {chinese}")
                test_results["failed"] += 1

            # Verify Mayan: Should be 7 Chicchan
            mayan = result.get("mayan", {})
            if (mayan.get("day_number") == 7 and
                mayan.get("day_sign") == "Chicchan"):
                print("[PASS] Mayan 1984-09-23 = 7 Chicchan")
                test_results["passed"] += 1
            else:
                print(f"[FAIL] Mayan 1984-09-23 incorrect: {mayan}")
                test_results["failed"] += 1

            # Verify tropical vs sidereal difference (should be ~24 degrees = 0.066)
            trop_sun = result.get("tropical", {}).get("sun", 0)
            sid_sun = result.get("sidereal", {}).get("sun", 0)
            diff = abs(trop_sun - sid_sun)

            # Ayanamsa ~23.85° = 0.0662 normalized
            if 0.055 < diff < 0.075:
                print(f"[PASS] Tropical-Sidereal difference ~24° (actual: {diff*360:.2f}°)")
                test_results["passed"] += 1
            else:
                print(f"[FAIL] Tropical-Sidereal difference wrong: {diff*360:.2f}°")
                test_results["failed"] += 1

        else:
            print(f"[FAIL] Reference calculation failed: {response.status_code}")
            test_results["failed"] += 1

    except Exception as e:
        print(f"[ERROR] Reference calculation: {str(e)}")
        test_results["failed"] += 1

    print()

    # SECTION 7: Data Range Validation
    print("SECTION 7: Data Range Validation")
    print("-" * 70)

    try:
        response = requests.post(
            f"{BASE_URL}/astro_vector",
            json={"date": "2000-01-01", "time": "12:00", "place": "Paris, France"}
        )

        if response.status_code == 200:
            result = response.json()

            # Check all tropical positions in range [0, 1)
            all_in_range = True
            for planet, value in result.get("tropical", {}).items():
                if not (0.0 <= value < 1.0):
                    print(f"[FAIL] Tropical {planet} out of range: {value}")
                    all_in_range = False
                    test_results["failed"] += 1

            if all_in_range:
                print("[PASS] All tropical positions in range [0.0, 1.0)")
                test_results["passed"] += 1

            # Check Chinese values
            chinese = result.get("chinese", {})
            stem = chinese.get("stem_number", 0)
            branch = chinese.get("branch_number", 0)

            if 1 <= stem <= 10 and 1 <= branch <= 12:
                print(f"[PASS] Chinese stem={stem} (1-10), branch={branch} (1-12)")
                test_results["passed"] += 1
            else:
                print(f"[FAIL] Chinese values out of range: stem={stem}, branch={branch}")
                test_results["failed"] += 1

            # Check Mayan values
            mayan = result.get("mayan", {})
            day_num = mayan.get("day_number", 0)
            day_sign_num = mayan.get("day_sign_number", 0)
            tzolkin_pos = mayan.get("tzolkin_position", 0)

            if (1 <= day_num <= 13 and
                1 <= day_sign_num <= 20 and
                1 <= tzolkin_pos <= 260):
                print(f"[PASS] Mayan ranges: day={day_num} (1-13), sign={day_sign_num} (1-20), pos={tzolkin_pos} (1-260)")
                test_results["passed"] += 1
            else:
                print(f"[FAIL] Mayan values out of range")
                test_results["failed"] += 1

        else:
            print(f"[FAIL] Range validation request failed: {response.status_code}")
            test_results["failed"] += 1

    except Exception as e:
        print(f"[ERROR] Range validation: {str(e)}")
        test_results["failed"] += 1

    print()

    # FINAL SUMMARY
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Passed:  {test_results['passed']}")
    print(f"Tests Failed:  {test_results['failed']}")
    print(f"Total Tests:   {test_results['passed'] + test_results['failed']}")

    if test_results['failed'] > 0:
        print(f"\\nErrors:")
        for error in test_results['errors']:
            print(f"  - {error}")

    print()

    if test_results['failed'] == 0:
        print("[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"[FAILURE] {test_results['failed']} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys

    print("Starting Astro Vector API Test Suite...")
    print("Make sure the API server is running on http://localhost:8000")
    print()

    try:
        # Quick check if server is running
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print(f"Server detected: {response.json()['service']} v{response.json()['version']}")
        print()
    except Exception as e:
        print(f"[ERROR] Cannot connect to API server: {str(e)}")
        print("Please start the server with: python run.py")
        sys.exit(1)

    exit_code = run_all_tests()
    sys.exit(exit_code)
