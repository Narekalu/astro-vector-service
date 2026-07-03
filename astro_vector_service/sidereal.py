"""
Sidereal Zodiac Calculations (Lahiri Ayanamsa)
Vedic astrology system - 10 planetary positions with Lahiri ayanamsa correction
"""

import swisseph as swe
from typing import Dict
from .utils import normalize_degrees, validate_normalized_value


class SiderealCalculationError(Exception):
    """Exception raised when sidereal calculations fail"""
    pass


# Same planets as tropical
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


def calculate_sidereal(jd: float) -> Dict[str, float]:
    """
    Calculate sidereal zodiac positions for all 10 celestial bodies.

    Sidereal zodiac is used in Vedic astrology, aligned with fixed stars
    rather than seasons. Uses Lahiri ayanamsa (most common in Indian astrology).

    The ayanamsa is the difference between tropical and sidereal zodiacs,
    currently about 24 degrees (and slowly increasing).

    Args:
        jd: Julian Day Number (UTC)

    Returns:
        Dictionary with normalized positions (0.0-1.0) for all 10 bodies:
        {
            "sun": 0.xxx,
            "moon": 0.xxx,
            ...
        }

    Raises:
        SiderealCalculationError: If calculation fails for any planet

    Example:
        >>> jd = 2451545.0  # 2000-01-01 12:00 UTC
        >>> positions = calculate_sidereal(jd)
        >>> print(f"Sun: {positions['sun']}")
        Sun: 0.711111  # ~256° (Sagittarius in sidereal)
        # Note: About 24° less than tropical position
    """
    # Set sidereal mode with Lahiri ayanamsa
    # SE_SIDM_LAHIRI = Lahiri ayanamsa (Chitrapaksha)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    results = {}

    for planet_name, planet_id in PLANETS.items():
        try:
            # Calculate planet position with sidereal flag
            # FLG_SIDEREAL tells Swiss Ephemeris to apply ayanamsa correction
            position_data, ret_flags = swe.calc_ut(
                jd,
                planet_id,
                swe.FLG_SIDEREAL  # Enable sidereal mode
            )

            # Extract longitude (already corrected for ayanamsa)
            longitude = position_data[0]

            # Normalize to 0.0-1.0 range
            normalized = normalize_degrees(longitude)

            # Validate the normalized value
            validate_normalized_value(normalized)

            # Store result
            results[planet_name] = normalized

        except Exception as e:
            raise SiderealCalculationError(
                f"Failed to calculate sidereal position for {planet_name}: {str(e)}"
            )

    # Verify we got all 10 planets
    if len(results) != 10:
        raise SiderealCalculationError(
            f"Incomplete calculation: expected 10 planets, got {len(results)}"
        )

    return results


def get_ayanamsa(jd: float) -> float:
    """
    Get the Lahiri ayanamsa value for a given Julian Day.

    The ayanamsa is the offset between tropical and sidereal zodiacs.
    It increases by about 50 arcseconds per year (precession of equinoxes).

    Args:
        jd: Julian Day Number (UTC)

    Returns:
        Ayanamsa value in degrees

    Example:
        >>> jd = 2451545.0  # 2000-01-01
        >>> ayanamsa = get_ayanamsa(jd)
        >>> print(f"Ayanamsa: {ayanamsa:.2f}°")
        Ayanamsa: 23.85°  # Approximately
    """
    # Set Lahiri mode
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Get ayanamsa value
    ayanamsa = swe.get_ayanamsa_ut(jd)

    return ayanamsa


def get_planet_details_sidereal(jd: float, planet_name: str) -> Dict[str, float]:
    """
    Get detailed sidereal information for a single planet.

    Args:
        jd: Julian Day Number (UTC)
        planet_name: Name of planet (e.g., "sun", "moon", "mars")

    Returns:
        Dictionary with detailed position data:
        {
            "longitude": float (sidereal degrees, 0-360),
            "normalized": float (0-1),
            "latitude": float (degrees),
            "distance": float (AU),
            "speed": float (degrees/day),
            "ayanamsa": float (correction applied, degrees)
        }

    Raises:
        SiderealCalculationError: If planet name invalid or calculation fails
    """
    if planet_name not in PLANETS:
        raise SiderealCalculationError(
            f"Unknown planet: {planet_name}. "
            f"Valid planets: {', '.join(PLANETS.keys())}"
        )

    try:
        # Set sidereal mode
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        planet_id = PLANETS[planet_name]
        position_data, ret_flags = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)

        # Get ayanamsa
        ayanamsa = get_ayanamsa(jd)

        return {
            "longitude": position_data[0],
            "normalized": normalize_degrees(position_data[0]),
            "latitude": position_data[1],
            "distance": position_data[2],
            "speed": position_data[3],
            "ayanamsa": ayanamsa
        }

    except Exception as e:
        raise SiderealCalculationError(
            f"Failed to get sidereal details for {planet_name}: {str(e)}"
        )


# Example usage and testing
if __name__ == "__main__":
    from datetime import datetime
    from .utils import datetime_to_julian_day
    from .tropical import calculate_tropical

    print("Testing Sidereal module...\n")

    # Test date: 2000-01-01 12:00 UTC (J2000 epoch)
    test_dt = datetime(2000, 1, 1, 12, 0, 0)
    test_jd = datetime_to_julian_day(test_dt)

    print(f"Test date: {test_dt}")
    print(f"Julian Day: {test_jd}\n")

    # Test 1: Get ayanamsa
    print("Test 1: Get Lahiri ayanamsa")
    try:
        ayanamsa = get_ayanamsa(test_jd)
        print(f"[PASS] Ayanamsa: {ayanamsa:.4f}° (~23.85° expected for 2000)")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 2: Calculate all sidereal positions
    print("\nTest 2: Calculate all 10 sidereal positions")
    try:
        positions = calculate_sidereal(test_jd)
        print("[PASS] All positions calculated successfully")
        print("\nPositions (normalized 0-1):")
        for planet, pos in positions.items():
            print(f"  {planet:10s}: {pos:.6f}")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 3: Compare tropical vs sidereal
    print("\nTest 3: Compare tropical vs sidereal (should differ by ~24°)")
    try:
        tropical = calculate_tropical(test_jd)
        sidereal = calculate_sidereal(test_jd)
        ayanamsa = get_ayanamsa(test_jd)

        print(f"Ayanamsa: {ayanamsa:.4f}° = {ayanamsa/360:.6f} normalized")
        print("\nSun comparison:")
        print(f"  Tropical:  {tropical['sun']:.6f}")
        print(f"  Sidereal:  {sidereal['sun']:.6f}")
        diff = abs(tropical['sun'] - sidereal['sun'])
        print(f"  Difference: {diff:.6f} ({diff * 360:.2f}°)")
        print(f"  Expected:   ~{ayanamsa/360:.6f} ({ayanamsa:.2f}°)")

        # Check if difference is approximately equal to ayanamsa
        expected_diff = ayanamsa / 360
        if abs(diff - expected_diff) < 0.001:  # Within 0.36° tolerance
            print("[PASS] Difference matches ayanamsa")
        else:
            print(f"[WARN] Difference {diff:.6f} != expected {expected_diff:.6f}")

    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 4: Get detailed info for Sun (sidereal)
    print("\nTest 4: Get detailed sidereal info for Sun")
    try:
        sun_details = get_planet_details_sidereal(test_jd, "sun")
        print("[PASS] Sun sidereal details retrieved")
        print(f"  Longitude: {sun_details['longitude']:.4f}°")
        print(f"  Normalized: {sun_details['normalized']:.6f}")
        print(f"  Ayanamsa applied: {sun_details['ayanamsa']:.4f}°")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 5: Validate all values in range
    print("\nTest 5: Validate all values in range [0.0, 1.0)")
    try:
        positions = calculate_sidereal(test_jd)
        all_valid = True
        for planet, pos in positions.items():
            if not (0.0 <= pos < 1.0):
                print(f"[FAIL] {planet} out of range: {pos}")
                all_valid = False
        if all_valid:
            print("[PASS] All values in valid range")
    except Exception as e:
        print(f"[FAIL] {e}")

    print("\n[SUCCESS] Sidereal module tests complete!")
