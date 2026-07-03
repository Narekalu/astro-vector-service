"""
Tropical Zodiac Calculations
Western astrology system - 10 planetary positions (Sun through Pluto)
"""

import swisseph as swe
from typing import Dict
from .utils import normalize_degrees, validate_normalized_value


class TropicalCalculationError(Exception):
    """Exception raised when tropical calculations fail"""
    pass


# Planet constants from Swiss Ephemeris
PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO
}


def calculate_tropical(jd: float) -> Dict[str, float]:
    """
    Calculate tropical zodiac positions for all 10 celestial bodies.

    Tropical zodiac is the standard Western astrology system,
    aligned with the seasons (vernal equinox = 0° Aries).

    Args:
        jd: Julian Day Number (UTC)

    Returns:
        Dictionary with normalized positions (0.0-1.0) for all 10 bodies:
        {
            "sun": 0.xxx,
            "moon": 0.xxx,
            "mercury": 0.xxx,
            "venus": 0.xxx,
            "mars": 0.xxx,
            "jupiter": 0.xxx,
            "saturn": 0.xxx,
            "uranus": 0.xxx,
            "neptune": 0.xxx,
            "pluto": 0.xxx
        }

    Raises:
        TropicalCalculationError: If calculation fails for any planet

    Example:
        >>> jd = 2451545.0  # 2000-01-01 12:00 UTC
        >>> positions = calculate_tropical(jd)
        >>> print(f"Sun: {positions['sun']}")
        Sun: 0.777778  # ~280° (Capricorn)
    """
    results = {}

    for planet_name, planet_id in PLANETS.items():
        try:
            # Calculate planet position
            # swe.calc_ut returns tuple: (position_data, return_flags)
            # position_data[0] = longitude in degrees (0-360)
            # position_data[1] = latitude in degrees
            # position_data[2] = distance in AU
            # position_data[3] = speed in longitude (degrees/day)
            position_data, ret_flags = swe.calc_ut(jd, planet_id)

            # Extract longitude (ecliptic position)
            longitude = position_data[0]

            # Normalize to 0.0-1.0 range
            normalized = normalize_degrees(longitude)

            # Validate the normalized value
            validate_normalized_value(normalized)

            # Store result
            results[planet_name] = normalized

        except Exception as e:
            raise TropicalCalculationError(
                f"Failed to calculate tropical position for {planet_name}: {str(e)}"
            )

    # Verify we got all 10 planets
    if len(results) != 10:
        raise TropicalCalculationError(
            f"Incomplete calculation: expected 10 planets, got {len(results)}"
        )

    return results


def get_planet_details(jd: float, planet_name: str) -> Dict[str, float]:
    """
    Get detailed information for a single planet.
    Useful for debugging and verification.

    Args:
        jd: Julian Day Number (UTC)
        planet_name: Name of planet (e.g., "sun", "moon", "mars")

    Returns:
        Dictionary with detailed position data:
        {
            "longitude": float (degrees, 0-360),
            "normalized": float (0-1),
            "latitude": float (degrees),
            "distance": float (AU),
            "speed": float (degrees/day)
        }

    Raises:
        TropicalCalculationError: If planet name invalid or calculation fails
    """
    if planet_name not in PLANETS:
        raise TropicalCalculationError(
            f"Unknown planet: {planet_name}. "
            f"Valid planets: {', '.join(PLANETS.keys())}"
        )

    try:
        planet_id = PLANETS[planet_name]
        position_data, ret_flags = swe.calc_ut(jd, planet_id)

        return {
            "longitude": position_data[0],
            "normalized": normalize_degrees(position_data[0]),
            "latitude": position_data[1],
            "distance": position_data[2],
            "speed": position_data[3]
        }

    except Exception as e:
        raise TropicalCalculationError(
            f"Failed to get details for {planet_name}: {str(e)}"
        )


# Example usage and testing
if __name__ == "__main__":
    from datetime import datetime
    from .utils import datetime_to_julian_day

    print("Testing Tropical module...\n")

    # Test date: 2000-01-01 12:00 UTC (J2000 epoch)
    test_dt = datetime(2000, 1, 1, 12, 0, 0)
    test_jd = datetime_to_julian_day(test_dt)

    print(f"Test date: {test_dt}")
    print(f"Julian Day: {test_jd}\n")

    # Test 1: Calculate all tropical positions
    print("Test 1: Calculate all 10 tropical positions")
    try:
        positions = calculate_tropical(test_jd)
        print("[PASS] All positions calculated successfully")
        print("\nPositions (normalized 0-1):")
        for planet, pos in positions.items():
            print(f"  {planet:10s}: {pos:.6f}")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 2: Get detailed info for Sun
    print("\nTest 2: Get detailed info for Sun")
    try:
        sun_details = get_planet_details(test_jd, "sun")
        print("[PASS] Sun details retrieved")
        print(f"  Longitude: {sun_details['longitude']:.4f}°")
        print(f"  Normalized: {sun_details['normalized']:.6f}")
        print(f"  Latitude: {sun_details['latitude']:.4f}°")
        print(f"  Distance: {sun_details['distance']:.6f} AU")
        print(f"  Speed: {sun_details['speed']:.4f}°/day")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 3: Historical date (1984-09-23 12:35 UTC)
    print("\nTest 3: Historical date (1984-09-23 14:35 UTC)")
    historical_dt = datetime(1984, 9, 23, 12, 35, 0)
    historical_jd = datetime_to_julian_day(historical_dt)
    try:
        positions = calculate_tropical(historical_jd)
        print("[PASS] Historical calculation successful")
        print(f"  Sun: {positions['sun']:.6f}")
        print(f"  Moon: {positions['moon']:.6f}")
        print(f"  Mars: {positions['mars']:.6f}")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 4: Verify all values are in valid range
    print("\nTest 4: Validate all values in range [0.0, 1.0)")
    try:
        positions = calculate_tropical(test_jd)
        all_valid = True
        for planet, pos in positions.items():
            if not (0.0 <= pos < 1.0):
                print(f"[FAIL] {planet} out of range: {pos}")
                all_valid = False
        if all_valid:
            print("[PASS] All values in valid range")
    except Exception as e:
        print(f"[FAIL] {e}")

    print("\n[SUCCESS] Tropical module tests complete!")
