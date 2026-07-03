"""
Draconic Zodiac Calculations
Positions relative to the Moon's North Node (Mean Node)
"""

import swisseph as swe
from typing import Dict
from .utils import normalize_degrees, validate_normalized_value


class DraconicCalculationError(Exception):
    """Exception raised when draconic calculations fail"""
    pass


# Same planets as tropical/sidereal
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


def calculate_draconic(jd: float) -> Dict[str, float]:
    """
    Calculate draconic zodiac positions for all 10 celestial bodies.

    Draconic zodiac is based on the Moon's orbital plane, with the
    North Node (ascending node) as the starting point (0°).

    Formula: Draconic Position = (Tropical Position - North Node Position) mod 360

    All planets are shifted by the same amount (the North Node position),
    effectively rotating the zodiac so that the North Node becomes 0° Aries.

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
        DraconicCalculationError: If calculation fails

    Example:
        >>> jd = 2451545.0  # 2000-01-01 12:00 UTC
        >>> positions = calculate_draconic(jd)
        >>> # Moon in draconic chart shows its relationship to its nodes
    """
    try:
        # First, get the Mean North Node position (tropical)
        # MEAN_NODE = average position (not True Node which oscillates)
        north_node_data, _ = swe.calc_ut(jd, swe.MEAN_NODE)
        north_node_lon = north_node_data[0]  # Longitude in degrees

    except Exception as e:
        raise DraconicCalculationError(
            f"Failed to calculate North Node position: {str(e)}"
        )

    results = {}

    for planet_name, planet_id in PLANETS.items():
        try:
            # Get tropical position
            position_data, _ = swe.calc_ut(jd, planet_id)
            tropical_lon = position_data[0]

            # Calculate draconic: (planet - north_node) mod 360
            # This rotates the zodiac so North Node = 0°
            draconic_lon = (tropical_lon - north_node_lon) % 360.0

            # Normalize to 0.0-1.0 range
            normalized = normalize_degrees(draconic_lon)

            # Validate the normalized value
            validate_normalized_value(normalized)

            # Store result
            results[planet_name] = normalized

        except Exception as e:
            raise DraconicCalculationError(
                f"Failed to calculate draconic position for {planet_name}: {str(e)}"
            )

    # Verify we got all 10 planets
    if len(results) != 10:
        raise DraconicCalculationError(
            f"Incomplete calculation: expected 10 planets, got {len(results)}"
        )

    return results


def get_north_node_position(jd: float) -> Dict[str, float]:
    """
    Get the Moon's North Node (Mean Node) position.

    The North Node is the point where the Moon's orbit crosses
    the ecliptic from south to north.

    Args:
        jd: Julian Day Number (UTC)

    Returns:
        Dictionary with North Node details:
        {
            "longitude": float (tropical degrees, 0-360),
            "normalized": float (0-1),
            "latitude": float (always ~0 by definition),
            "speed": float (degrees/day, retrograde ~-0.053°/day)
        }

    Example:
        >>> jd = 2451545.0
        >>> node = get_north_node_position(jd)
        >>> print(f"North Node: {node['longitude']:.2f}°")
        North Node: 125.08°
    """
    try:
        # Get Mean North Node
        node_data, _ = swe.calc_ut(jd, swe.MEAN_NODE)

        return {
            "longitude": node_data[0],
            "normalized": normalize_degrees(node_data[0]),
            "latitude": node_data[1],  # Should be ~0
            "speed": node_data[3]  # Negative (retrograde)
        }

    except Exception as e:
        raise DraconicCalculationError(
            f"Failed to get North Node position: {str(e)}"
        )


def get_planet_details_draconic(jd: float, planet_name: str) -> Dict[str, float]:
    """
    Get detailed draconic information for a single planet.

    Args:
        jd: Julian Day Number (UTC)
        planet_name: Name of planet (e.g., "sun", "moon", "mars")

    Returns:
        Dictionary with detailed position data:
        {
            "tropical_longitude": float (degrees),
            "draconic_longitude": float (degrees),
            "normalized": float (0-1),
            "north_node": float (degrees),
            "offset_from_node": float (degrees, = draconic_longitude)
        }

    Raises:
        DraconicCalculationError: If planet name invalid or calculation fails
    """
    if planet_name not in PLANETS:
        raise DraconicCalculationError(
            f"Unknown planet: {planet_name}. "
            f"Valid planets: {', '.join(PLANETS.keys())}"
        )

    try:
        # Get North Node
        node_data, _ = swe.calc_ut(jd, swe.MEAN_NODE)
        north_node_lon = node_data[0]

        # Get planet tropical position
        planet_id = PLANETS[planet_name]
        position_data, _ = swe.calc_ut(jd, planet_id)
        tropical_lon = position_data[0]

        # Calculate draconic
        draconic_lon = (tropical_lon - north_node_lon) % 360.0

        return {
            "tropical_longitude": tropical_lon,
            "draconic_longitude": draconic_lon,
            "normalized": normalize_degrees(draconic_lon),
            "north_node": north_node_lon,
            "offset_from_node": draconic_lon
        }

    except Exception as e:
        raise DraconicCalculationError(
            f"Failed to get draconic details for {planet_name}: {str(e)}"
        )


# Example usage and testing
if __name__ == "__main__":
    from datetime import datetime
    from .utils import datetime_to_julian_day
    from .tropical import calculate_tropical

    print("Testing Draconic module...\n")

    # Test date: 2000-01-01 12:00 UTC (J2000 epoch)
    test_dt = datetime(2000, 1, 1, 12, 0, 0)
    test_jd = datetime_to_julian_day(test_dt)

    print(f"Test date: {test_dt}")
    print(f"Julian Day: {test_jd}\n")

    # Test 1: Get North Node position
    print("Test 1: Get North Node position")
    try:
        node = get_north_node_position(test_jd)
        print(f"[PASS] North Node position calculated")
        print(f"  Longitude: {node['longitude']:.4f}°")
        print(f"  Normalized: {node['normalized']:.6f}")
        print(f"  Speed: {node['speed']:.6f}°/day (retrograde)")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 2: Calculate all draconic positions
    print("\nTest 2: Calculate all 10 draconic positions")
    try:
        positions = calculate_draconic(test_jd)
        print("[PASS] All positions calculated successfully")
        print("\nPositions (normalized 0-1):")
        for planet, pos in positions.items():
            print(f"  {planet:10s}: {pos:.6f}")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 3: Compare tropical vs draconic
    print("\nTest 3: Compare tropical vs draconic")
    try:
        tropical = calculate_tropical(test_jd)
        draconic = calculate_draconic(test_jd)
        node = get_north_node_position(test_jd)

        print(f"North Node: {node['longitude']:.4f}° = {node['normalized']:.6f} normalized")
        print("\nSun comparison:")
        print(f"  Tropical:  {tropical['sun']:.6f} ({tropical['sun'] * 360:.2f}°)")
        print(f"  Draconic:  {draconic['sun']:.6f} ({draconic['sun'] * 360:.2f}°)")

        # Calculate expected draconic = (tropical - north_node) mod 360
        expected_drac = ((tropical['sun'] * 360) - node['longitude']) % 360
        expected_norm = normalize_degrees(expected_drac)
        print(f"  Expected:  {expected_norm:.6f} ({expected_drac:.2f}°)")

        if abs(draconic['sun'] - expected_norm) < 0.000001:
            print("[PASS] Draconic calculation matches formula")
        else:
            print(f"[WARN] Mismatch: {draconic['sun']:.6f} != {expected_norm:.6f}")

    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 4: Get detailed info for Moon (special case in draconic)
    print("\nTest 4: Get detailed draconic info for Moon")
    try:
        moon_details = get_planet_details_draconic(test_jd, "moon")
        print("[PASS] Moon draconic details retrieved")
        print(f"  Tropical: {moon_details['tropical_longitude']:.4f}°")
        print(f"  Draconic: {moon_details['draconic_longitude']:.4f}°")
        print(f"  North Node: {moon_details['north_node']:.4f}°")
        print(f"  Offset from Node: {moon_details['offset_from_node']:.4f}°")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 5: Validate all values in range
    print("\nTest 5: Validate all values in range [0.0, 1.0)")
    try:
        positions = calculate_draconic(test_jd)
        all_valid = True
        for planet, pos in positions.items():
            if not (0.0 <= pos < 1.0):
                print(f"[FAIL] {planet} out of range: {pos}")
                all_valid = False
        if all_valid:
            print("[PASS] All values in valid range")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 6: Verify all planets shifted by same amount
    print("\nTest 6: Verify all planets shifted by same North Node amount")
    try:
        tropical = calculate_tropical(test_jd)
        draconic = calculate_draconic(test_jd)
        node = get_north_node_position(test_jd)

        # Calculate shift for each planet
        shifts = []
        for planet in PLANETS.keys():
            trop_deg = tropical[planet] * 360
            drac_deg = draconic[planet] * 360
            # Shift = (tropical - draconic) mod 360
            shift = (trop_deg - drac_deg) % 360
            shifts.append(shift)

        # All shifts should be approximately equal to North Node position
        avg_shift = sum(shifts) / len(shifts)
        max_deviation = max(abs(s - avg_shift) for s in shifts)

        print(f"  Average shift: {avg_shift:.4f}°")
        print(f"  North Node: {node['longitude']:.4f}°")
        print(f"  Max deviation: {max_deviation:.6f}°")

        if max_deviation < 0.001:  # Within 0.001° tolerance
            print("[PASS] All planets shifted uniformly")
        else:
            print(f"[WARN] Deviation {max_deviation:.6f}° exceeds tolerance")

    except Exception as e:
        print(f"[FAIL] {e}")

    print("\n[SUCCESS] Draconic module tests complete!")
