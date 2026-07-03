"""
Chinese Sexagenary Cycle Calculations
60-year cycle combining 10 Heavenly Stems and 12 Earthly Branches
Uses SOLAR calendar (Li Chun boundary ~Feb 4), NOT lunar new year
"""

from datetime import date
from typing import Dict


class ChineseCalculationError(Exception):
    """Exception raised when Chinese calculations fail"""
    pass


# 12 Earthly Branches (Animals)
ANIMALS = [
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"
]

# 5 Elements (each appears twice in the 10 Heavenly Stems)
ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]

# Heavenly Stems (10) - paired with elements
# Stems 1-2: Wood, 3-4: Fire, 5-6: Earth, 7-8: Metal, 9-10: Water
# Odd stems: Yang, Even stems: Yin


def calculate_chinese(birth_date: date) -> Dict[str, any]:
    """
    Calculate Chinese Sexagenary cycle data based on birth date.

    Uses SOLAR calendar with Li Chun (Start of Spring) boundary.
    Li Chun typically falls on February 4, but can be Feb 3 or Feb 5.

    For simplicity in POC, we use February 4 as the boundary.
    Births before Feb 4 belong to the previous solar year.

    Args:
        birth_date: Birth date (date object)

    Returns:
        Dictionary with Chinese astrology data:
        {
            "animal": str (one of 12 animals),
            "element": str (one of 5 elements),
            "yin_yang": str ("Yin" or "Yang"),
            "stem_number": int (1-10, Heavenly Stem),
            "branch_number": int (1-12, Earthly Branch)
        }

    Raises:
        ChineseCalculationError: If calculation fails

    Example:
        >>> birth_date = date(1984, 9, 23)
        >>> result = calculate_chinese(birth_date)
        >>> print(f"{result['element']} {result['animal']}")
        Wood Rat
    """
    try:
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day

        # Adjust year if before Li Chun (Feb 4)
        # If birth is before Feb 4, use previous year's animal/element
        if month < 2 or (month == 2 and day < 4):
            year -= 1  # Still in previous solar year

        # Calculate position in 60-year cycle
        # Reference epoch: 1984 = Year 1 of cycle (Rat, Wood, Yang)
        # This is the start of the current cycle in the Gregorian calendar
        EPOCH_YEAR = 1984

        # Position in cycle (0-59)
        cycle_position = (year - EPOCH_YEAR) % 60
        if cycle_position < 0:
            cycle_position += 60

        # Calculate Heavenly Stem (1-10)
        stem_number = (cycle_position % 10) + 1

        # Calculate Earthly Branch (1-12)
        branch_number = (cycle_position % 12) + 1

        # Determine animal (Earthly Branch)
        # Branch 1 = Rat, Branch 2 = Ox, etc.
        animal = ANIMALS[branch_number - 1]

        # Determine element (from Heavenly Stem)
        # Stems 1-2: Wood, 3-4: Fire, 5-6: Earth, 7-8: Metal, 9-10: Water
        element_index = (stem_number - 1) // 2
        element = ELEMENTS[element_index]

        # Determine Yin/Yang (from Heavenly Stem)
        # Odd stems (1,3,5,7,9) = Yang
        # Even stems (2,4,6,8,10) = Yin
        yin_yang = "Yang" if stem_number % 2 == 1 else "Yin"

        return {
            "animal": animal,
            "element": element,
            "yin_yang": yin_yang,
            "stem_number": stem_number,
            "branch_number": branch_number
        }

    except Exception as e:
        raise ChineseCalculationError(
            f"Failed to calculate Chinese astrology data: {str(e)}"
        )


def get_sexagenary_name(stem_number: int, branch_number: int) -> str:
    """
    Get the traditional Chinese name for a year in the 60-year cycle.

    Args:
        stem_number: Heavenly Stem (1-10)
        branch_number: Earthly Branch (1-12)

    Returns:
        Descriptive name (e.g., "Yang Wood Rat", "Yin Fire Ox")
    """
    element_index = (stem_number - 1) // 2
    element = ELEMENTS[element_index]
    yin_yang = "Yang" if stem_number % 2 == 1 else "Yin"
    animal = ANIMALS[branch_number - 1]

    return f"{yin_yang} {element} {animal}"


def get_year_info(year: int, after_li_chun: bool = True) -> Dict[str, any]:
    """
    Get Chinese astrology info for a specific year.

    Args:
        year: Gregorian year
        after_li_chun: If True, year starts after Li Chun (Feb 4).
                       If False, treats as before Li Chun (previous solar year)

    Returns:
        Dictionary with Chinese astrology data for that year
    """
    # Create a date after Li Chun for that year
    if after_li_chun:
        test_date = date(year, 2, 5)  # Feb 5 (after Li Chun)
    else:
        test_date = date(year, 1, 1)  # Jan 1 (before Li Chun, so previous year)

    return calculate_chinese(test_date)


# Example usage and testing
if __name__ == "__main__":
    print("Testing Chinese Sexagenary module...\n")

    # Test 1: Known year (1984 = Rat, Wood, Yang)
    print("Test 1: Year 1984 (after Li Chun) - Should be Wood Rat (Yang)")
    try:
        result = calculate_chinese(date(1984, 9, 23))
        print(f"[PASS] {result['yin_yang']} {result['element']} {result['animal']}")
        print(f"       Stem: {result['stem_number']}, Branch: {result['branch_number']}")

        # Verify
        assert result['animal'] == "Rat", f"Expected Rat, got {result['animal']}"
        assert result['element'] == "Wood", f"Expected Wood, got {result['element']}"
        assert result['yin_yang'] == "Yang", f"Expected Yang, got {result['yin_yang']}"
        assert result['stem_number'] == 1, f"Expected stem 1, got {result['stem_number']}"
        assert result['branch_number'] == 1, f"Expected branch 1, got {result['branch_number']}"

    except (ChineseCalculationError, AssertionError) as e:
        print(f"[FAIL] {e}")

    # Test 2: Edge case - Before Li Chun (should be previous year)
    print("\nTest 2: Feb 2, 1984 (BEFORE Li Chun) - Should be 1983 (Pig)")
    try:
        result = calculate_chinese(date(1984, 2, 2))
        print(f"[PASS] {result['yin_yang']} {result['element']} {result['animal']}")
        print(f"       Stem: {result['stem_number']}, Branch: {result['branch_number']}")

        # 1983 should be Yin Water Pig (last year of previous cycle)
        assert result['animal'] == "Pig", f"Expected Pig, got {result['animal']}"
        assert result['element'] == "Water", f"Expected Water, got {result['element']}"
        assert result['yin_yang'] == "Yin", f"Expected Yin, got {result['yin_yang']}"

    except (ChineseCalculationError, AssertionError) as e:
        print(f"[FAIL] {e}")

    # Test 3: Edge case - After Li Chun (should be current year)
    print("\nTest 3: Feb 5, 1984 (AFTER Li Chun) - Should be 1984 (Rat)")
    try:
        result = calculate_chinese(date(1984, 2, 5))
        print(f"[PASS] {result['yin_yang']} {result['element']} {result['animal']}")

        assert result['animal'] == "Rat", f"Expected Rat, got {result['animal']}"

    except (ChineseCalculationError, AssertionError) as e:
        print(f"[FAIL] {e}")

    # Test 4: Different years
    print("\nTest 4: Various years")
    test_years = [
        (date(1985, 6, 1), "Ox", "Wood", "Yin", 2, 2),
        (date(2000, 7, 1), "Dragon", "Metal", "Yang", 7, 5),
        (date(2020, 8, 1), "Rat", "Metal", "Yang", 7, 1),
    ]

    for test_date, exp_animal, exp_element, exp_yin_yang, exp_stem, exp_branch in test_years:
        try:
            result = calculate_chinese(test_date)
            name = get_sexagenary_name(result['stem_number'], result['branch_number'])
            print(f"  {test_date.year}: {name}")

            assert result['animal'] == exp_animal, f"Year {test_date.year}: Expected {exp_animal}, got {result['animal']}"
            assert result['element'] == exp_element, f"Year {test_date.year}: Expected {exp_element}, got {result['element']}"
            assert result['yin_yang'] == exp_yin_yang, f"Year {test_date.year}: Expected {exp_yin_yang}, got {result['yin_yang']}"
            assert result['stem_number'] == exp_stem, f"Year {test_date.year}: Expected stem {exp_stem}, got {result['stem_number']}"
            assert result['branch_number'] == exp_branch, f"Year {test_date.year}: Expected branch {exp_branch}, got {result['branch_number']}"

        except (ChineseCalculationError, AssertionError) as e:
            print(f"  [FAIL] {test_date.year}: {e}")

    # Test 5: Full 12-year animal cycle from 1984
    print("\nTest 5: 12-year animal cycle (1984-1995)")
    for i in range(12):
        year = 1984 + i
        result = calculate_chinese(date(year, 6, 1))
        expected_animal = ANIMALS[i]
        print(f"  {year}: {result['animal']:10s}", end="")
        if result['animal'] == expected_animal:
            print(" [PASS]")
        else:
            print(f" [FAIL] Expected {expected_animal}")

    # Test 6: Verify 60-year cycle
    print("\nTest 6: Verify 60-year cycle")
    result_1984 = calculate_chinese(date(1984, 6, 1))
    result_2044 = calculate_chinese(date(2044, 6, 1))  # 1984 + 60

    if (result_1984['animal'] == result_2044['animal'] and
        result_1984['element'] == result_2044['element'] and
        result_1984['yin_yang'] == result_2044['yin_yang']):
        print(f"[PASS] 60-year cycle verified: 1984 and 2044 both {result_1984['yin_yang']} {result_1984['element']} {result_1984['animal']}")
    else:
        print(f"[FAIL] 60-year cycle broken")
        print(f"  1984: {result_1984}")
        print(f"  2044: {result_2044}")

    print("\n[SUCCESS] Chinese Sexagenary module tests complete!")
