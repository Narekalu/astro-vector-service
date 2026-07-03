"""
Input Validation Module
Validates date, time, and place inputs for astrological calculations
"""

import re
from datetime import datetime, date, time
from typing import Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_date(date_str: str) -> date:
    """
    Validate date string in YYYY-MM-DD format.

    Args:
        date_str: Date string to validate

    Returns:
        datetime.date object

    Raises:
        ValidationError: If date format is invalid or date doesn't exist

    Examples:
        >>> validate_date("1984-09-23")
        datetime.date(1984, 9, 23)
        >>> validate_date("2024-02-30")  # Invalid date
        ValidationError: Invalid date value: 2024-02-30
    """
    if not date_str:
        raise ValidationError("Date is required")

    # Check format with regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise ValidationError(
            f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD format (e.g., 1984-09-23)"
        )

    # Try to parse the date
    try:
        year, month, day = map(int, date_str.split('-'))
        parsed_date = date(year, month, day)
    except ValueError as e:
        raise ValidationError(
            f"Invalid date value: '{date_str}'. {str(e)}"
        )

    # Check date is within Swiss Ephemeris range (1900-2100)
    if parsed_date.year < 1900 or parsed_date.year > 2100:
        raise ValidationError(
            f"Date year {parsed_date.year} is outside valid range (1900-2100)"
        )

    return parsed_date


def validate_time(time_str: Optional[str]) -> Tuple[time, str]:
    """
    Validate time string in HH:MM format.
    If None, defaults to 12:00 and returns "low" accuracy.

    Args:
        time_str: Time string to validate (optional)

    Returns:
        Tuple of (datetime.time object, time_accuracy flag)
        time_accuracy is "high" if time provided, "low" if defaulted

    Raises:
        ValidationError: If time format is invalid or time doesn't exist

    Examples:
        >>> validate_time("14:35")
        (datetime.time(14, 35), "high")
        >>> validate_time(None)
        (datetime.time(12, 0), "low")
        >>> validate_time("25:00")  # Invalid time
        ValidationError: Invalid time value
    """
    # If no time provided, default to 12:00 with low accuracy
    if time_str is None or time_str == "":
        return time(12, 0), "low"

    # Check format with regex
    if not re.match(r'^\d{1,2}:\d{2}$', time_str):
        raise ValidationError(
            f"Invalid time format: '{time_str}'. Expected HH:MM format (e.g., 14:35)"
        )

    # Try to parse the time
    try:
        hour, minute = map(int, time_str.split(':'))
        parsed_time = time(hour, minute)
    except ValueError as e:
        raise ValidationError(
            f"Invalid time value: '{time_str}'. Hours must be 0-23, minutes 0-59"
        )

    return parsed_time, "high"


def validate_place(place_str: str) -> str:
    """
    Validate place string is non-empty.

    Args:
        place_str: Place name to validate

    Returns:
        Cleaned place string

    Raises:
        ValidationError: If place is empty or only whitespace

    Examples:
        >>> validate_place("Paris, France")
        "Paris, France"
        >>> validate_place("  ")
        ValidationError: Place is required
    """
    if not place_str:
        raise ValidationError("Place is required")

    # Strip whitespace
    cleaned_place = place_str.strip()

    if not cleaned_place:
        raise ValidationError("Place cannot be empty or only whitespace")

    # Basic sanity check - at least 2 characters
    if len(cleaned_place) < 2:
        raise ValidationError("Place name too short (minimum 2 characters)")

    return cleaned_place


def validate_all_inputs(date_str: str, time_str: Optional[str], place_str: str) -> dict:
    """
    Validate all inputs and return structured data.

    Args:
        date_str: Date string in YYYY-MM-DD format
        time_str: Time string in HH:MM format (optional)
        place_str: Place name

    Returns:
        Dictionary with validated inputs:
        {
            "date": datetime.date object,
            "time": datetime.time object,
            "place": str,
            "time_accuracy": "high" | "low",
            "date_str": str (original),
            "time_str": str (original or "12:00")
        }

    Raises:
        ValidationError: If any validation fails
    """
    # Validate each input
    validated_date = validate_date(date_str)
    validated_time, time_accuracy = validate_time(time_str)
    validated_place = validate_place(place_str)

    # Determine the time string to echo back
    echo_time_str = time_str if time_str else "12:00"

    return {
        "date": validated_date,
        "time": validated_time,
        "place": validated_place,
        "time_accuracy": time_accuracy,
        "date_str": date_str,
        "time_str": echo_time_str
    }


def format_datetime_for_display(date_obj: date, time_obj: time) -> str:
    """
    Format date and time for display.

    Args:
        date_obj: datetime.date object
        time_obj: datetime.time object

    Returns:
        Formatted string "YYYY-MM-DD HH:MM"
    """
    return f"{date_obj.isoformat()} {time_obj.strftime('%H:%M')}"


# Example usage and testing
if __name__ == "__main__":
    # Test valid inputs
    print("Testing valid inputs:")
    result = validate_all_inputs("1984-09-23", "14:35", "Paris, France")
    print(f"[PASS] Valid input: {result}")

    # Test missing time
    print("\nTesting missing time (should default to 12:00):")
    result = validate_all_inputs("1990-06-15", None, "Tokyo, Japan")
    print(f"[PASS] Missing time: {result}")
    print(f"  Time accuracy: {result['time_accuracy']}")

    # Test invalid date format
    print("\nTesting invalid date format:")
    try:
        validate_date("23-09-1984")
    except ValidationError as e:
        print(f"[PASS] Caught error: {e}")

    # Test invalid date value
    print("\nTesting invalid date value (Feb 30):")
    try:
        validate_date("2024-02-30")
    except ValidationError as e:
        print(f"[PASS] Caught error: {e}")

    # Test invalid time
    print("\nTesting invalid time (25:00):")
    try:
        validate_time("25:00")
    except ValidationError as e:
        print(f"[PASS] Caught error: {e}")

    # Test empty place
    print("\nTesting empty place:")
    try:
        validate_place("   ")
    except ValidationError as e:
        print(f"[PASS] Caught error: {e}")

    print("\n[SUCCESS] All validation tests passed!")
