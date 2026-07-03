"""
Astro Vector Service — 5-system astrological calculation microservice.

Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
Source code: see the SOURCE_URL environment variable / the "/" endpoint.
"""

import os

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time

from astro_vector_service.validators import validate_date, validate_time, validate_place, ValidationError
from astro_vector_service.geocoding import AmbiguousLocationError
from astro_vector_service.formatter import calculate_astro_vector, format_error_response, FormatterError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
SOURCE_URL = os.environ.get(
    "SOURCE_URL", "https://github.com/CHANGEME/astro-vector-service"
)

app = FastAPI(
    title="Astro Vector Service",
    description=(
        "Calculates astrological positions across 5 systems "
        "(Tropical, Sidereal, Draconic, Chinese, Mayan). "
        f"Free software under AGPL-3.0 — source: {SOURCE_URL}"
    ),
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AstroVectorRequest(BaseModel):
    """Request model for astro vector calculation"""
    date: str = Field(..., description="Birth date in YYYY-MM-DD format", example="1984-09-23")
    time: Optional[str] = Field(None, description="Birth time in HH:MM format (optional)", example="14:35")
    place: str = Field(..., description="Birth place as 'City, Country'", example="Paris, France")


class Coordinates(BaseModel):
    """Geographic coordinates"""
    latitude: float
    longitude: float


class InputEcho(BaseModel):
    """Echoes the input with calculated metadata"""
    date: str
    time: str
    place: str
    coordinates: Coordinates
    timezone: str
    utc_datetime: str
    julian_day: float
    time_accuracy: str  # "high" or "low"


class TropicalPositions(BaseModel):
    """Normalized tropical zodiac positions (0.0-1.0)"""
    sun: float
    moon: float
    mercury: float
    venus: float
    mars: float
    jupiter: float
    saturn: float
    uranus: float
    neptune: float
    pluto: float


class SiderealPositions(BaseModel):
    """Normalized sidereal zodiac positions (0.0-1.0) - Lahiri ayanamsa"""
    sun: float
    moon: float
    mercury: float
    venus: float
    mars: float
    jupiter: float
    saturn: float
    uranus: float
    neptune: float
    pluto: float


class DraconicPositions(BaseModel):
    """Normalized draconic zodiac positions (0.0-1.0) - relative to North Node"""
    sun: float
    moon: float
    mercury: float
    venus: float
    mars: float
    jupiter: float
    saturn: float
    uranus: float
    neptune: float
    pluto: float


class ChineseData(BaseModel):
    """Chinese Sexagenary cycle data"""
    animal: str
    element: str
    yin_yang: str
    stem_number: int
    branch_number: int


class MayanData(BaseModel):
    """Mayan Tzolkin calendar data"""
    day_number: int
    day_sign: str
    day_sign_number: int
    tzolkin_position: int
    full_name: str


class AstroVectorResponse(BaseModel):
    """Complete response with all 5 astrological systems"""
    input: InputEcho
    tropical: TropicalPositions
    sidereal: SiderealPositions
    draconic: DraconicPositions
    chinese: ChineseData
    mayan: MayanData


class LocationCandidate(BaseModel):
    """Candidate location for ambiguous place resolution"""
    place: str
    latitude: float
    longitude: float


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool
    error_type: str
    message: str
    candidates: Optional[List[LocationCandidate]] = None


# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Astro Vector Service",
        "version": "1.0.0",
        "status": "running",
        "license": "AGPL-3.0",
        "source": SOURCE_URL,
        "endpoints": ["/health", "/astro_vector", "/docs", "/redoc"]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker/Kubernetes"""
    return {
        "status": "healthy",
        "service": "astro-vector-service"
    }


# Main calculation endpoint
@app.post("/astro_vector", tags=["Calculations"])
async def astro_vector_endpoint(request: AstroVectorRequest):
    """
    Calculate astrological positions across all 5 systems

    - **date**: Birth date in YYYY-MM-DD format (required)
    - **time**: Birth time in HH:MM format (optional, defaults to 12:00)
    - **place**: Birth place as "City, Country" (required)

    Returns normalized positions for:
    - Tropical zodiac (Western)
    - Sidereal zodiac (Lahiri ayanamsa)
    - Draconic zodiac (North Node relative)
    - Chinese Sexagenary (60-year cycle)
    - Mayan Tzolkin (260-day calendar)

    **Error Handling:**
    - Validation errors (400): Invalid date/time format or out of range
    - Ambiguous location (409): Multiple locations found, returns candidate list
    - Not found (404): Location could not be resolved
    - Server error (500): Calculation or system error
    """
    logger.info(f"Received request: date={request.date}, time={request.time}, place={request.place}")

    try:
        # Step 1: Validate inputs
        try:
            birth_date = validate_date(request.date)
            logger.debug(f"Validated date: {birth_date}")
        except ValidationError as e:
            logger.warning(f"Date validation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        try:
            birth_time, time_accuracy = validate_time(request.time)
            logger.debug(f"Validated time: {birth_time} (accuracy: {time_accuracy})")
        except ValidationError as e:
            logger.warning(f"Time validation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        try:
            place = validate_place(request.place)
            logger.debug(f"Validated place: {place}")
        except ValidationError as e:
            logger.warning(f"Place validation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        # Step 2: Calculate astro vector using formatter
        try:
            result = calculate_astro_vector(
                birth_date=birth_date,
                birth_time=birth_time if birth_time else None,
                birth_place=place,
                time_accuracy=time_accuracy
            )
            logger.info(f"Calculation successful for {place}")
            return result

        except AmbiguousLocationError as e:
            # Return 409 Conflict with candidate list
            logger.warning(f"Ambiguous location: {place}")
            error_response = format_error_response(e)
            raise HTTPException(
                status_code=409,
                detail=error_response
            )

        except FormatterError as e:
            # Check if it's a geocoding "not found" error
            if "Unable to resolve location" in str(e):
                logger.warning(f"Location not found: {place}")
                raise HTTPException(status_code=404, detail=str(e))
            else:
                # Other formatter errors are server errors
                logger.error(f"Formatter error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    except HTTPException:
        # Re-raise HTTPExceptions (already formatted)
        raise

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
