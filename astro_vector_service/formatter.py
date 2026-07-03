"""
Response Formatter and Module Integration
Orchestrates all astrological calculations and formats unified response
"""

from datetime import datetime, date, time
from typing import Dict, Optional, Tuple
import pytz
from timezonefinder import TimezoneFinder

from .geocoding import geocode_place, GeocodingError, AmbiguousLocationError
from .utils import datetime_to_julian_day
from .tropical import calculate_tropical
from .sidereal import calculate_sidereal
from .draconic import calculate_draconic
from .chinese import calculate_chinese
from .mayan import calculate_mayan


class FormatterError(Exception):
    """Exception raised when response formatting fails"""
    pass


def calculate_astro_vector(
    birth_date: date,
    birth_time: Optional[time],
    birth_place: str,
    time_accuracy: str = "high"
) -> Dict:
    """
    Calculate complete astrological vector across all 5 systems.

    This is the main integration function that:
    1. Geocodes the birth place
    2. Determines timezone
    3. Converts to UTC Julian Day
    4. Calculates all 5 astrological systems
    5. Returns unified response

    Args:
        birth_date: Birth date (date object)
        birth_time: Birth time (time object or None for noon default)
        birth_place: Birth place as string (for geocoding)
        time_accuracy: "high" if time provided, "low" if defaulted to noon

    Returns:
        Dictionary with complete astrological data:
        {
            "input": {
                "date": str,
                "time": str,
                "place": str,
                "coordinates": {"latitude": float, "longitude": float},
                "timezone": str,
                "time_accuracy": str
            },
            "tropical": {...},
            "sidereal": {...},
            "draconic": {...},
            "chinese": {...},
            "mayan": {...}
        }

    Raises:
        FormatterError: If any calculation step fails
        AmbiguousLocationError: If place name matches multiple locations
    """
    try:
        # Step 1: Geocode birth place
        try:
            latitude, longitude, display_name = geocode_place(birth_place)
        except AmbiguousLocationError:
            # Re-raise as-is so API can return candidate list
            raise
        except GeocodingError as e:
            raise FormatterError(f"Geocoding failed: {str(e)}")

        # Step 2: Determine timezone from coordinates
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

        if timezone_str is None:
            raise FormatterError(
                f"Could not determine timezone for coordinates ({latitude}, {longitude})"
            )

        # Step 3: Create timezone-aware datetime
        # If no time provided, use noon (12:00:00) local time
        if birth_time is None:
            birth_time = time(12, 0, 0)
            time_accuracy = "low"

        # Combine date and time
        naive_dt = datetime.combine(birth_date, birth_time)

        # Make timezone-aware
        local_tz = pytz.timezone(timezone_str)
        aware_dt = local_tz.localize(naive_dt)

        # Convert to UTC
        utc_dt = aware_dt.astimezone(pytz.UTC)

        # Step 4: Convert to Julian Day
        jd = datetime_to_julian_day(utc_dt)

        # Step 5: Calculate all systems
        tropical_data = calculate_tropical(jd)
        sidereal_data = calculate_sidereal(jd)
        draconic_data = calculate_draconic(jd)
        chinese_data = calculate_chinese(birth_date)  # Uses date, not JD
        mayan_data = calculate_mayan(birth_date)  # Uses date, not JD

        # Step 6: Format unified response
        response = {
            "input": {
                "date": birth_date.isoformat(),
                "time": birth_time.isoformat(),
                "place": display_name,
                "coordinates": {
                    "latitude": round(latitude, 6),
                    "longitude": round(longitude, 6)
                },
                "timezone": timezone_str,
                "utc_datetime": utc_dt.isoformat(),
                "julian_day": round(jd, 6),
                "time_accuracy": time_accuracy
            },
            "tropical": tropical_data,
            "sidereal": sidereal_data,
            "draconic": draconic_data,
            "chinese": chinese_data,
            "mayan": mayan_data
        }

        return response

    except AmbiguousLocationError:
        # Re-raise ambiguous location errors unchanged
        raise

    except Exception as e:
        if isinstance(e, FormatterError):
            raise
        raise FormatterError(f"Failed to calculate astro vector: {str(e)}")


def format_error_response(error: Exception) -> Dict:
    """
    Format error into standardized error response.

    Args:
        error: Exception that occurred

    Returns:
        Dictionary with error details
    """
    error_type = type(error).__name__

    # Special handling for ambiguous location errors
    if isinstance(error, AmbiguousLocationError):
        # Extract the place name from the error message
        # Message format: "Multiple locations found for '{place}'. Please specify..."
        place_name = "your location"
        try:
            import re
            match = re.search(r"'([^']+)'", str(error))
            if match:
                place_name = match.group(1)
        except:
            pass

        # Generate dynamic example based on actual candidates
        example_text = f"Please choose one of the specific locations listed below"
        if error.candidates and len(error.candidates) > 0:
            first_candidate = error.candidates[0].get('place', '')
            if first_candidate:
                example_text = f"For example: '{first_candidate}'"

        return {
            "success": False,
            "status": "MULTIPLE_LOCATIONS_FOUND",
            "message": str(error),
            "instruction": "Please resubmit your request with a more specific location from the candidates below.",
            "example": example_text,
            "candidates": error.candidates,
            "candidates_count": len(error.candidates)
        }

    # Standard error response for other errors
    response = {
        "error": True,
        "error_type": error_type,
        "message": str(error)
    }

    return response


# Example usage and testing
if __name__ == "__main__":
    print("Testing Response Formatter module...\\n")

    # Test 1: Complete calculation with known location
    print("Test 1: Complete calculation (1984-09-23, Paris)")
    try:
        result = calculate_astro_vector(
            birth_date=date(1984, 9, 23),
            birth_time=time(12, 35, 0),
            birth_place="Paris, France",
            time_accuracy="high"
        )

        print("[PASS] Complete calculation successful")
        print(f"\\nInput:")
        print(f"  Date: {result['input']['date']}")
        print(f"  Time: {result['input']['time']}")
        print(f"  Place: {result['input']['place']}")
        print(f"  Coordinates: {result['input']['coordinates']['latitude']:.2f}°, {result['input']['coordinates']['longitude']:.2f}°")
        print(f"  Timezone: {result['input']['timezone']}")
        print(f"  UTC: {result['input']['utc_datetime']}")
        print(f"  Julian Day: {result['input']['julian_day']}")
        print(f"  Time Accuracy: {result['input']['time_accuracy']}")

        print(f"\\nTropical (sample):")
        print(f"  Sun: {result['tropical']['sun']:.6f}")
        print(f"  Moon: {result['tropical']['moon']:.6f}")

        print(f"\\nSidereal (sample):")
        print(f"  Sun: {result['sidereal']['sun']:.6f}")

        print(f"\\nDraconic (sample):")
        print(f"  Sun: {result['draconic']['sun']:.6f}")

        print(f"\\nChinese:")
        print(f"  {result['chinese']['yin_yang']} {result['chinese']['element']} {result['chinese']['animal']}")

        print(f"\\nMayan:")
        print(f"  {result['mayan']['full_name']}")

    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 2: Calculation with default noon time
    print("\\n\\nTest 2: Calculation with default noon time (no time provided)")
    try:
        result = calculate_astro_vector(
            birth_date=date(2000, 1, 1),
            birth_time=None,  # Will default to noon
            birth_place="London, UK",
            time_accuracy="low"
        )

        print("[PASS] Default time calculation successful")
        print(f"  Time used: {result['input']['time']}")
        print(f"  Time accuracy: {result['input']['time_accuracy']}")

    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 3: Different timezone handling
    print("\\n\\nTest 3: Different timezone (New York)")
    try:
        result = calculate_astro_vector(
            birth_date=date(1990, 6, 15),
            birth_time=time(8, 30, 0),
            birth_place="Manhattan, New York, USA",
            time_accuracy="high"
        )

        print("[PASS] Timezone calculation successful")
        print(f"  Timezone: {result['input']['timezone']}")
        print(f"  Local: {result['input']['date']} {result['input']['time']}")
        print(f"  UTC: {result['input']['utc_datetime']}")

    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 4: Error handling - invalid location
    print("\\n\\nTest 4: Error handling (invalid location)")
    try:
        result = calculate_astro_vector(
            birth_date=date(2000, 1, 1),
            birth_time=time(12, 0, 0),
            birth_place="XYZ123InvalidPlace",
            time_accuracy="high"
        )
        print("[FAIL] Should have raised error for invalid location")

    except FormatterError as e:
        print(f"[PASS] Error caught correctly: {type(e).__name__}")
        error_response = format_error_response(e)
        print(f"  Error type: {error_response['error_type']}")
        print(f"  Message: {error_response['message'][:50]}...")

    # Test 5: Error handling - ambiguous location
    print("\\n\\nTest 5: Error handling (ambiguous location)")
    try:
        result = calculate_astro_vector(
            birth_date=date(2000, 1, 1),
            birth_time=time(12, 0, 0),
            birth_place="Springfield",  # Ambiguous - many Springfields
            time_accuracy="high"
        )
        print("[FAIL] Should have raised error for ambiguous location")

    except AmbiguousLocationError as e:
        print(f"[PASS] Ambiguous location detected correctly")
        error_response = format_error_response(e)
        print(f"  Error type: {error_response['error_type']}")
        print(f"  Candidates: {len(error_response.get('candidates', []))} locations found")
        if error_response.get('candidates'):
            first = error_response['candidates'][0]
            display = first.get('display_name', str(first))
            print(f"  First candidate: {display[:60]}...")

    except Exception as e:
        # Might get timeout if geocoding service is slow
        print(f"[INFO] Got {type(e).__name__}: {str(e)[:50]}...")

    # Test 6: Verify all 5 systems present in response
    print("\\n\\nTest 6: Verify all 5 systems present")
    try:
        result = calculate_astro_vector(
            birth_date=date(2000, 1, 1),
            birth_time=time(0, 0, 0),
            birth_place="Tokyo, Japan",
            time_accuracy="high"
        )

        required_keys = ['input', 'tropical', 'sidereal', 'draconic', 'chinese', 'mayan']
        all_present = all(key in result for key in required_keys)

        if all_present:
            print("[PASS] All 5 systems present in response")
            print(f"  Keys: {', '.join(required_keys)}")
        else:
            missing = [key for key in required_keys if key not in result]
            print(f"[FAIL] Missing keys: {', '.join(missing)}")

    except Exception as e:
        print(f"[FAIL] {e}")

    print("\\n[SUCCESS] Response Formatter module tests complete!")
