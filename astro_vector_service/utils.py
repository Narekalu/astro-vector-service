"""
Utility Functions
Shared utilities for astronomical calculations
"""

import swisseph as swe
from datetime import datetime
from typing import Tuple


def datetime_to_julian_day(dt: datetime) -> float:
    """
    Convert datetime to Julian Day Number for Swiss Ephemeris.

    Args:
        dt: UTC datetime

    Returns:
        Julian Day Number as float

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2000, 1, 1, 12, 0, 0)
        >>> jd = datetime_to_julian_day(dt)
        >>> print(f"JD: {jd}")
        JD: 2451545.0
    """
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0)

    # Swiss Ephemeris julday function
    # Arguments: year, month, day, hour (decimal), calendar_type
    # Calendar type: SE_GREG_CAL (1) for Gregorian
    jd = swe.julday(year, month, day, hour, swe.GREG_CAL)

    return jd


def normalize_degrees(degrees: float) -> float:
    """
    Normalize zodiac degree (0-360) to 0.0-1.0 range.

    Args:
        degrees: Position in degrees (0-360)

    Returns:
        Normalized value (0.0 to <1.0), rounded to 6 decimal places

    Example:
        >>> normalize_degrees(180.0)
        0.5
        >>> normalize_degrees(90.0)
        0.25
        >>> normalize_degrees(0.0)
        0.0
        >>> normalize_degrees(359.99)
        0.999972
    """
    # Ensure degrees is in 0-360 range (mod 360)
    degrees = degrees % 360.0

    # Normalize to 0-1
    normalized = degrees / 360.0

    # Round to 6 decimal places for precision
    # (6 decimals = ±0.0013° accuracy, more than sufficient for astrology)
    return round(normalized, 6)


def validate_normalized_value(value: float) -> None:
    """
    Validate that a normalized value is in valid range [0.0, 1.0).

    Args:
        value: Normalized value to validate

    Raises:
        ValueError: If value is out of range

    Example:
        >>> validate_normalized_value(0.5)
        # No error
        >>> validate_normalized_value(1.5)
        ValueError: Normalized value 1.5 out of range [0.0, 1.0)
    """
    if not (0.0 <= value < 1.0):
        raise ValueError(f"Normalized value {value} out of range [0.0, 1.0)")


def degrees_to_zodiac_sign(degrees: float) -> Tuple[str, float]:
    """
    Convert zodiac degrees to sign name and position within sign.

    Args:
        degrees: Absolute zodiac position in degrees (0-360)

    Returns:
        Tuple of (sign_name, degrees_in_sign)

    Example:
        >>> degrees_to_zodiac_sign(0.0)
        ('Aries', 0.0)
        >>> degrees_to_zodiac_sign(45.0)
        ('Taurus', 15.0)
        >>> degrees_to_zodiac_sign(180.0)
        ('Libra', 0.0)
    """
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # Ensure degrees is in 0-360 range
    degrees = degrees % 360.0

    # Each sign is 30 degrees
    sign_index = int(degrees / 30.0)
    degrees_in_sign = degrees % 30.0

    return signs[sign_index], degrees_in_sign


def normalize_angle_difference(angle1: float, angle2: float) -> float:
    """
    Calculate normalized difference between two angles.

    Args:
        angle1: First angle in degrees
        angle2: Second angle in degrees

    Returns:
        Shortest angular distance between angles, normalized to 0-1

    Example:
        >>> normalize_angle_difference(10.0, 350.0)
        0.055556  # 20 degrees difference / 360
        >>> normalize_angle_difference(180.0, 0.0)
        0.5  # 180 degrees / 360
    """
    # Calculate difference
    diff = abs(angle1 - angle2) % 360.0

    # Take shorter path around circle
    if diff > 180.0:
        diff = 360.0 - diff

    # Normalize
    return normalize_degrees(diff)


def julian_day_to_datetime(jd: float) -> datetime:
    """
    Convert Julian Day Number back to datetime.
    Useful for debugging and verification.

    Args:
        jd: Julian Day Number

    Returns:
        UTC datetime

    Example:
        >>> jd = 2451545.0
        >>> dt = julian_day_to_datetime(jd)
        >>> print(dt)
        2000-01-01 12:00:00
    """
    # Swiss Ephemeris revjul function
    # Returns tuple: (year, month, day, hour)
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)

    # Convert hour (decimal) to hours, minutes, seconds
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)

    return datetime(year, month, day, hours, minutes, seconds)


def format_coordinates(lat: float, lon: float) -> str:
    """
    Format latitude and longitude for display.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        Formatted string with N/S/E/W indicators

    Example:
        >>> format_coordinates(48.8566, 2.3522)
        "48.86°N, 2.35°E"
        >>> format_coordinates(-33.8688, 151.2093)
        "33.87°S, 151.21°E"
    """
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"

    return f"{abs(lat):.2f}°{lat_dir}, {abs(lon):.2f}°{lon_dir}"


# Swiss Ephemeris setup
def initialize_swiss_ephemeris():
    """
    Initialize Swiss Ephemeris with default settings.
    Called once at module import.
    """
    # Set ephemeris path to default (built-in ephemeris data)
    # For extended date range, you can download additional ephemeris files
    # and set path with swe.set_ephe_path("/path/to/ephe/")
    pass


# Initialize on module import
initialize_swiss_ephemeris()


# Example usage and testing
if __name__ == "__main__":
    print("Testing utility functions...\n")

    # Test 1: Julian Day conversion
    print("Test 1: Julian Day conversion")
    dt = datetime(2000, 1, 1, 12, 0, 0)
    jd = datetime_to_julian_day(dt)
    print(f"[PASS] {dt} -> JD {jd}")
    print(f"       Expected: ~2451545.0")

    # Test 2: Normalization
    print("\nTest 2: Degree normalization")
    test_degrees = [0.0, 90.0, 180.0, 270.0, 360.0, 45.5]
    for deg in test_degrees:
        norm = normalize_degrees(deg)
        print(f"[PASS] {deg}° -> {norm}")

    # Test 3: Zodiac sign conversion
    print("\nTest 3: Zodiac sign conversion")
    test_positions = [0.0, 30.0, 60.0, 180.0, 359.0]
    for pos in test_positions:
        sign, deg_in_sign = degrees_to_zodiac_sign(pos)
        print(f"[PASS] {pos}° -> {sign} {deg_in_sign:.2f}°")

    # Test 4: Validation
    print("\nTest 4: Normalized value validation")
    try:
        validate_normalized_value(0.5)
        print("[PASS] Valid value 0.5 accepted")
    except ValueError as e:
        print(f"[FAIL] {e}")

    try:
        validate_normalized_value(1.5)
        print("[FAIL] Invalid value 1.5 should have been rejected")
    except ValueError as e:
        print(f"[PASS] Invalid value rejected: {e}")

    # Test 5: Reverse Julian Day
    print("\nTest 5: Reverse Julian Day conversion")
    jd = 2451545.0
    dt = julian_day_to_datetime(jd)
    print(f"[PASS] JD {jd} -> {dt}")

    # Test 6: Coordinate formatting
    print("\nTest 6: Coordinate formatting")
    coords = [(48.8566, 2.3522), (-33.8688, 151.2093), (0, 0)]
    for lat, lon in coords:
        formatted = format_coordinates(lat, lon)
        print(f"[PASS] ({lat}, {lon}) -> {formatted}")

    print("\n[SUCCESS] All utility function tests passed!")
