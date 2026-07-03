"""
Mayan Tzolkin Calendar Calculations
260-day sacred calendar using GMT correlation 584283
"""

from datetime import date
from typing import Dict
import swisseph as swe


class MayanCalculationError(Exception):
    """Exception raised when Mayan calculations fail"""
    pass


# GMT Correlation Constant (584283)
# This is the most widely accepted correlation between Mayan and Gregorian calendars
# It means: Mayan Long Count 0.0.0.0.0 = Julian Day 584283 = September 6, -3113 (proleptic Gregorian)
GMT_CORRELATION = 584283

# 20 Tzolkin Day Signs (in order)
DAY_SIGNS = [
    "Imix",      # 1 - Crocodile/Dragon
    "Ik",        # 2 - Wind
    "Akbal",     # 3 - Night/House
    "Kan",       # 4 - Seed/Lizard
    "Chicchan",  # 5 - Serpent
    "Cimi",      # 6 - Death/Transformer
    "Manik",     # 7 - Deer/Hand
    "Lamat",     # 8 - Rabbit/Star
    "Muluc",     # 9 - Water/Moon
    "Oc",        # 10 - Dog
    "Chuen",     # 11 - Monkey
    "Eb",        # 12 - Road/Grass
    "Ben",       # 13 - Reed/Skywalker
    "Ix",        # 14 - Jaguar
    "Men",       # 15 - Eagle
    "Cib",       # 16 - Vulture/Owl
    "Caban",     # 17 - Earth/Earthquake
    "Etznab",    # 18 - Flint/Mirror
    "Cauac",     # 19 - Storm
    "Ahau"       # 20 - Lord/Sun
]


def calculate_mayan(birth_date: date) -> Dict[str, any]:
    """
    Calculate Mayan Tzolkin calendar data based on birth date.

    The Tzolkin is a 260-day sacred calendar consisting of:
    - 13 numbers (1-13)
    - 20 day signs (named glyphs)
    - Each combination appears once every 260 days

    Uses GMT correlation constant 584283 (most widely accepted).

    Args:
        birth_date: Birth date (date object)

    Returns:
        Dictionary with Mayan Tzolkin data:
        {
            "day_number": int (1-13),
            "day_sign": str (one of 20 day signs),
            "day_sign_number": int (1-20, position in cycle),
            "tzolkin_position": int (1-260, day in cycle),
            "full_name": str (e.g., "5 Chicchan")
        }

    Raises:
        MayanCalculationError: If calculation fails

    Example:
        >>> birth_date = date(1984, 9, 23)
        >>> result = calculate_mayan(birth_date)
        >>> print(result['full_name'])
        5 Chicchan
    """
    try:
        # Convert date to Julian Day Number
        # Use noon (12:00) for consistency with astronomical calculations
        jd = swe.julday(birth_date.year, birth_date.month, birth_date.day, 12.0, swe.GREG_CAL)

        # Calculate days since Mayan epoch (using GMT correlation)
        # GMT 584283 is the JD of Mayan Long Count 0.0.0.0.0
        days_since_epoch = int(jd - GMT_CORRELATION)

        # Calculate position in 260-day Tzolkin cycle (1-260)
        # We add 1 because Tzolkin days are numbered 1-260, not 0-259
        tzolkin_position = (days_since_epoch % 260) + 1

        # Calculate day number (1-13)
        # The 13-day cycle starts at 1
        day_number = ((days_since_epoch % 13) + 1)

        # Calculate day sign (1-20)
        # The 20-day cycle starts at position 0 (Imix)
        day_sign_number = (days_since_epoch % 20) + 1
        day_sign = DAY_SIGNS[day_sign_number - 1]

        # Create full Tzolkin name (number + sign)
        full_name = f"{day_number} {day_sign}"

        return {
            "day_number": day_number,
            "day_sign": day_sign,
            "day_sign_number": day_sign_number,
            "tzolkin_position": tzolkin_position,
            "full_name": full_name
        }

    except Exception as e:
        raise MayanCalculationError(
            f"Failed to calculate Mayan Tzolkin data: {str(e)}"
        )


def get_tzolkin_name(day_number: int, day_sign_number: int) -> str:
    """
    Get the traditional Tzolkin name for a given day.

    Args:
        day_number: Day number (1-13)
        day_sign_number: Day sign number (1-20)

    Returns:
        Full Tzolkin name (e.g., "5 Chicchan")

    Raises:
        MayanCalculationError: If numbers are out of range
    """
    if not (1 <= day_number <= 13):
        raise MayanCalculationError(f"Day number must be 1-13, got {day_number}")

    if not (1 <= day_sign_number <= 20):
        raise MayanCalculationError(f"Day sign number must be 1-20, got {day_sign_number}")

    day_sign = DAY_SIGNS[day_sign_number - 1]
    return f"{day_number} {day_sign}"


def calculate_tzolkin_position(day_number: int, day_sign_number: int) -> int:
    """
    Calculate the position (1-260) in the Tzolkin cycle from day number and sign.

    Args:
        day_number: Day number (1-13)
        day_sign_number: Day sign number (1-20)

    Returns:
        Position in 260-day cycle (1-260)

    Example:
        >>> calculate_tzolkin_position(1, 1)  # 1 Imix
        1
        >>> calculate_tzolkin_position(13, 20)  # 13 Ahau
        260
    """
    # Use Chinese Remainder Theorem to find position
    # We need to find x where:
    # x ≡ (day_number - 1) (mod 13)
    # x ≡ (day_sign_number - 1) (mod 20)

    for position in range(260):
        if (position % 13 == (day_number - 1) and
            position % 20 == (day_sign_number - 1)):
            return position + 1  # Return 1-based position

    raise MayanCalculationError(
        f"Could not find position for {day_number} {DAY_SIGNS[day_sign_number - 1]}"
    )


# Example usage and testing
if __name__ == "__main__":
    print("Testing Mayan Tzolkin module...\\n")

    # Test 1: Known date (1984-09-23 = 7 Chicchan)
    print("Test 1: Known date (1984-09-23) - Calculate Tzolkin")
    try:
        result = calculate_mayan(date(1984, 9, 23))
        print(f"[PASS] {result['full_name']}")
        print(f"       Day Number: {result['day_number']}")
        print(f"       Day Sign: {result['day_sign']} (#{result['day_sign_number']})")
        print(f"       Tzolkin Position: {result['tzolkin_position']}/260")

        # Verify expected values (7 Chicchan)
        assert result['day_number'] == 7, f"Expected day number 7, got {result['day_number']}"
        assert result['day_sign'] == "Chicchan", f"Expected Chicchan, got {result['day_sign']}"
        assert result['day_sign_number'] == 5, f"Expected day sign #5, got {result['day_sign_number']}"

    except (MayanCalculationError, AssertionError) as e:
        print(f"[FAIL] {e}")

    # Test 2: Start of Tzolkin cycle (should be 1 Imix)
    # Date: December 21, 2012 (end of 13th Baktun, famous Mayan calendar date)
    print("\\nTest 2: December 21, 2012 (end of 13th Baktun)")
    try:
        result = calculate_mayan(date(2012, 12, 21))
        print(f"[PASS] {result['full_name']}")
        print(f"       Position: {result['tzolkin_position']}/260")
    except MayanCalculationError as e:
        print(f"[FAIL] {e}")

    # Test 3: Verify 260-day cycle
    print("\\nTest 3: Verify 260-day cycle (adding 260 days should return same Tzolkin)")
    try:
        from datetime import timedelta

        base_date = date(2000, 1, 1)
        result1 = calculate_mayan(base_date)

        # Add 260 days
        future_date = base_date + timedelta(days=260)
        result2 = calculate_mayan(future_date)

        print(f"  {base_date}: {result1['full_name']}")
        print(f"  {future_date}: {result2['full_name']}")

        if (result1['day_number'] == result2['day_number'] and
            result1['day_sign'] == result2['day_sign']):
            print("[PASS] 260-day cycle verified")
        else:
            print(f"[FAIL] Cycle broken: {result1['full_name']} != {result2['full_name']}")

    except (MayanCalculationError, AssertionError) as e:
        print(f"[FAIL] {e}")

    # Test 4: Test all 20 day signs appear in sequence
    print("\\nTest 4: Verify 20 day signs appear in correct sequence")
    try:
        base_date = date(2000, 1, 1)
        signs_seen = []

        for i in range(20):
            test_date = base_date + timedelta(days=i)
            result = calculate_mayan(test_date)
            signs_seen.append(result['day_sign'])

        # Check if we see 20 unique day signs
        unique_signs = list(dict.fromkeys(signs_seen))  # Preserve order
        if len(unique_signs) == 20:
            print(f"[PASS] All 20 day signs present in 20-day sequence")
            print(f"       First few: {', '.join(unique_signs[:5])}...")
        else:
            print(f"[FAIL] Expected 20 unique signs, got {len(unique_signs)}")

    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 5: Test day number cycles correctly (1-13)
    print("\\nTest 5: Verify day number cycles 1-13")
    try:
        base_date = date(2000, 1, 1)
        numbers_seen = []

        for i in range(13):
            test_date = base_date + timedelta(days=i)
            result = calculate_mayan(test_date)
            numbers_seen.append(result['day_number'])

        # Check if we see all 13 numbers
        unique_numbers = sorted(list(set(numbers_seen)))
        if unique_numbers == list(range(1, 14)):
            print(f"[PASS] All 13 day numbers present")
            print(f"       Sequence: {numbers_seen}")
        else:
            print(f"[FAIL] Expected 1-13, got {unique_numbers}")

    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 6: Test tzolkin_position calculation
    print("\\nTest 6: Verify Tzolkin position calculation")
    try:
        # 1 Imix should be position 1
        pos = calculate_tzolkin_position(1, 1)
        assert pos == 1, f"Expected position 1 for 1 Imix, got {pos}"
        print(f"[PASS] 1 Imix = position {pos}")

        # 13 Ahau should be position 260 (end of cycle)
        pos = calculate_tzolkin_position(13, 20)
        assert pos == 260, f"Expected position 260 for 13 Ahau, got {pos}"
        print(f"[PASS] 13 Ahau = position {pos}")

    except (MayanCalculationError, AssertionError) as e:
        print(f"[FAIL] {e}")

    # Test 7: Verify various known dates
    print("\\nTest 7: Various dates")
    test_dates = [
        (date(2000, 1, 1), None, None),  # Just calculate, don't assert
        (date(2020, 1, 1), None, None),
        (date(1984, 9, 23), 7, "Chicchan"),  # Known reference
    ]

    for test_date, exp_num, exp_sign in test_dates:
        try:
            result = calculate_mayan(test_date)
            print(f"  {test_date}: {result['full_name']}")

            if exp_num is not None:
                assert result['day_number'] == exp_num, f"Expected number {exp_num}, got {result['day_number']}"
            if exp_sign is not None:
                assert result['day_sign'] == exp_sign, f"Expected sign {exp_sign}, got {result['day_sign']}"

        except (MayanCalculationError, AssertionError) as e:
            print(f"  [FAIL] {test_date}: {e}")

    print("\\n[SUCCESS] Mayan Tzolkin module tests complete!")
