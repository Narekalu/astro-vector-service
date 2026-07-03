"""
Geocoding and Timezone Module
Converts place names to coordinates and determines timezone

CRITICAL REQUIREMENT: Ambiguous locations MUST return error with candidate list.
NO silent defaulting to most populous or first match.
"""

import pytz
from datetime import datetime, date, time
from typing import Tuple, Optional, List, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder


class GeocodingError(Exception):
    """Base exception for geocoding errors"""
    pass


class AmbiguousLocationError(GeocodingError):
    """
    Exception raised when multiple locations match the query.
    Contains list of candidate locations for user to choose from.
    """
    def __init__(self, message: str, candidates: List[Dict]):
        super().__init__(message)
        self.candidates = candidates


class LocationNotFoundError(GeocodingError):
    """Exception raised when location cannot be found"""
    pass


# Initialize geocoder with an identifying user agent (Nominatim usage policy).
# Set GEOCODER_USER_AGENT to include your deployment's contact info, e.g.
# "astro-vector-service/1.0 (you@example.com)"
import os
geocoder = Nominatim(
    user_agent=os.environ.get("GEOCODER_USER_AGENT", "astro-vector-service/1.0")
)

# Initialize timezone finder
tz_finder = TimezoneFinder()


def geocode_place(place: str, timeout: int = 10) -> Tuple[float, float, str]:
    """
    Convert place name to coordinates.

    CRITICAL: If multiple matches found with similar confidence,
    raises AmbiguousLocationError with candidate list.
    NO SILENT DEFAULTING.

    Args:
        place: Place name as "City, Country" or similar
        timeout: Timeout for geocoding request in seconds

    Returns:
        Tuple of (latitude, longitude, display_name)

    Raises:
        LocationNotFoundError: If location not found
        AmbiguousLocationError: If multiple similar matches found (with candidate list)
        GeocodingError: If geocoding service fails

    Examples:
        >>> geocode_place("Paris, France")
        (48.8566, 2.3522, "Paris, Île-de-France, France")

        >>> geocode_place("Paris")  # Ambiguous!
        AmbiguousLocationError with candidates:
        - Paris, France
        - Paris, Texas, USA
        - Paris, Ontario, Canada
    """
    if not place:
        raise GeocodingError("Place name cannot be empty")

    try:
        # Get multiple results to check for ambiguity
        # exactly_one=False returns a list of all matches
        results = geocoder.geocode(
            place,
            exactly_one=False,
            limit=10,  # Get up to 10 matches
            timeout=timeout,
            addressdetails=True
        )

    except GeocoderTimedOut:
        raise GeocodingError(
            f"Geocoding request timed out after {timeout} seconds. "
            "Please check your internet connection and try again."
        )
    except GeocoderServiceError as e:
        raise GeocodingError(f"Geocoding service error: {str(e)}")

    # No results found
    if not results:
        raise LocationNotFoundError(
            f"Unable to resolve location: '{place}'. "
            "Please check spelling or be more specific (e.g., 'Paris, France')"
        )

    # Single unambiguous result - return it
    if len(results) == 1:
        location = results[0]
        return (
            location.latitude,
            location.longitude,
            location.address
        )

    # Multiple results - check if they're truly different or just formatting differences
    # Group results by rough location (within ~10km = ~0.1 degrees)
    location_groups = _group_similar_locations(results, threshold=0.1)

    # If all results are in the same location (just different formatting),
    # return the first one
    if len(location_groups) == 1:
        location = location_groups[0][0]  # First location from the single group
        return (
            location.latitude,
            location.longitude,
            location.address
        )

    # Multiple distinct locations found - AMBIGUOUS
    # Build candidate list for user to choose from
    candidates = []
    for group in location_groups[:5]:  # Limit to top 5 distinct locations
        loc = group[0]  # Representative location from each group
        candidates.append({
            "place": _format_location_name(loc),
            "lat": round(loc.latitude, 4),
            "lon": round(loc.longitude, 4)
        })

    # Raise AmbiguousLocationError with candidate list
    raise AmbiguousLocationError(
        f"Multiple locations found for '{place}'. Please specify which location you mean.",
        candidates=candidates
    )


def _group_similar_locations(locations: List, threshold: float = 0.1) -> List[List]:
    """
    Group locations that are within threshold degrees of each other.

    Args:
        locations: List of geopy Location objects
        threshold: Maximum distance in degrees to consider "same location"

    Returns:
        List of location groups (each group is a list of similar locations)
    """
    groups = []

    for loc in locations:
        # Check if this location fits into an existing group
        placed = False
        for group in groups:
            # Compare with first location in group
            ref_loc = group[0]
            lat_diff = abs(loc.latitude - ref_loc.latitude)
            lon_diff = abs(loc.longitude - ref_loc.longitude)

            if lat_diff < threshold and lon_diff < threshold:
                group.append(loc)
                placed = True
                break

        # If doesn't fit any existing group, create new group
        if not placed:
            groups.append([loc])

    return groups


def _format_location_name(location) -> str:
    """
    Format location name for display in candidate list.

    Extracts key components: District, City, State/Region, Country
    Includes enough detail to differentiate similar locations.

    Args:
        location: Geopy Location object with address details

    Returns:
        Formatted location string
    """
    addr = location.raw.get('address', {})

    # Try to get meaningful components in order of specificity
    district = (addr.get('suburb') or
                addr.get('neighbourhood') or
                addr.get('district') or
                addr.get('quarter'))

    city = (addr.get('city') or
            addr.get('town') or
            addr.get('village') or
            addr.get('municipality') or
            addr.get('county'))

    state = (addr.get('state') or
             addr.get('region') or
             addr.get('province'))

    country = addr.get('country')

    # Build name with enough detail to differentiate
    parts = []

    # Add district if available and different from city
    if district and district != city:
        parts.append(district)

    # Always add city
    if city:
        parts.append(city)

    # Add state if available and different from city
    if state and state != city:
        parts.append(state)

    # Always add country
    if country:
        parts.append(country)

    # Fallback to full address if we couldn't build a good name
    formatted = ", ".join(parts) if parts else location.address

    # Add coordinates in parentheses to help differentiate identical-looking names
    formatted += f" ({location.latitude:.4f}°N, {location.longitude:.4f}°E)"

    return formatted


def get_timezone_name(lat: float, lon: float) -> str:
    """
    Determine timezone name from coordinates.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        Timezone name (e.g., "Europe/Paris", "America/New_York")

    Raises:
        GeocodingError: If timezone cannot be determined
    """
    try:
        tz_name = tz_finder.timezone_at(lat=lat, lng=lon)

        if not tz_name:
            # Try ocean timezone
            tz_name = tz_finder.closest_timezone_at(lat=lat, lng=lon)

        if not tz_name:
            raise GeocodingError(
                f"Unable to determine timezone for coordinates: {lat}, {lon}"
            )

        return tz_name

    except Exception as e:
        raise GeocodingError(f"Timezone determination failed: {str(e)}")


def convert_local_to_utc(
    local_date: date,
    local_time: time,
    timezone_name: str
) -> datetime:
    """
    Convert local birth datetime to UTC, accounting for DST.

    Args:
        local_date: Local date
        local_time: Local time
        timezone_name: Timezone name (e.g., "Europe/Paris")

    Returns:
        UTC datetime

    Raises:
        GeocodingError: If timezone is invalid or conversion fails
    """
    try:
        # Get timezone object
        tz = pytz.timezone(timezone_name)

        # Create naive datetime
        naive_dt = datetime.combine(local_date, local_time)

        # Localize to timezone (handles DST ambiguity)
        # is_dst=None raises exception if ambiguous, which is correct behavior
        local_dt = tz.localize(naive_dt, is_dst=None)

        # Convert to UTC
        utc_dt = local_dt.astimezone(pytz.UTC)

        return utc_dt

    except pytz.exceptions.UnknownTimeZoneError:
        raise GeocodingError(f"Unknown timezone: {timezone_name}")

    except pytz.exceptions.AmbiguousTimeError as e:
        # This happens during DST transitions
        # Use is_dst=False (standard time) as default
        local_dt = tz.localize(naive_dt, is_dst=False)
        utc_dt = local_dt.astimezone(pytz.UTC)
        return utc_dt

    except pytz.exceptions.NonExistentTimeError as e:
        # This happens during "spring forward" DST gap
        # Use is_dst=True (daylight time) as default
        local_dt = tz.localize(naive_dt, is_dst=True)
        utc_dt = local_dt.astimezone(pytz.UTC)
        return utc_dt

    except Exception as e:
        raise GeocodingError(f"Failed to convert local time to UTC: {str(e)}")


def geocode_and_convert(
    date_obj: date,
    time_obj: time,
    place: str
) -> Tuple[float, float, str, datetime]:
    """
    Complete geocoding and time conversion pipeline.

    Args:
        date_obj: Birth date
        time_obj: Birth time (local)
        place: Birth place name

    Returns:
        Tuple of (latitude, longitude, timezone_name, utc_datetime)

    Raises:
        LocationNotFoundError: If location not found
        AmbiguousLocationError: If location is ambiguous (with candidate list)
        GeocodingError: If any other geocoding/timezone error
    """
    # Step 1: Geocode place to coordinates
    lat, lon, display_name = geocode_place(place)

    # Step 2: Get timezone for coordinates
    timezone_name = get_timezone_name(lat, lon)

    # Step 3: Convert local time to UTC
    utc_dt = convert_local_to_utc(date_obj, time_obj, timezone_name)

    return lat, lon, timezone_name, utc_dt


# Example usage and testing
if __name__ == "__main__":
    print("Testing geocoding module...\n")

    # Test 1: Unambiguous location
    print("Test 1: Unambiguous location (Paris, France)")
    try:
        lat, lon, tz, utc = geocode_and_convert(
            date(1984, 9, 23),
            time(14, 35),
            "Paris, France"
        )
        print(f"[PASS] Lat: {lat:.4f}, Lon: {lon:.4f}")
        print(f"       Timezone: {tz}")
        print(f"       UTC: {utc}")
    except Exception as e:
        print(f"[FAIL] {e}")

    # Test 2: Ambiguous location (should raise error with candidates)
    print("\nTest 2: Ambiguous location (Paris without country)")
    try:
        lat, lon, tz, utc = geocode_and_convert(
            date(1984, 9, 23),
            time(14, 35),
            "Paris"
        )
        print(f"[FAIL] Should have raised AmbiguousLocationError!")
    except AmbiguousLocationError as e:
        print(f"[PASS] Caught ambiguous location error:")
        print(f"       Message: {e}")
        print(f"       Candidates:")
        for c in e.candidates:
            print(f"         - {c['place']} ({c['lat']}, {c['lon']})")
    except Exception as e:
        print(f"[FAIL] Wrong exception: {e}")

    # Test 3: Location not found
    print("\nTest 3: Location not found")
    try:
        lat, lon, tz, utc = geocode_and_convert(
            date(1984, 9, 23),
            time(14, 35),
            "XYZ123NotARealPlace"
        )
        print(f"[FAIL] Should have raised LocationNotFoundError!")
    except LocationNotFoundError as e:
        print(f"[PASS] Caught not found error: {e}")
    except Exception as e:
        print(f"[FAIL] Wrong exception: {e}")

    print("\n[SUCCESS] Geocoding module tests complete!")
