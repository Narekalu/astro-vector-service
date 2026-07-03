# Astro Vector Service

A self-contained FastAPI microservice that calculates astrological positions for a
birth date, time, and place across **five independent systems**:

| System | Description |
|---|---|
| **Tropical** | Western zodiac, season-aligned (10 planets, normalized longitudes) |
| **Sidereal** | Vedic zodiac, Lahiri ayanamsa (~24° correction) |
| **Draconic** | Positions relative to the Moon's North Node |
| **Chinese Sexagenary** | 60-year stem/branch cycle with Li Chun (Feb 4) year boundary |
| **Mayan Tzolkin** | 260-day sacred calendar (GMT 584283 correlation) |

Planetary longitudes are computed with the Swiss Ephemeris (`pyswisseph`) and
returned normalized to `[0, 1)` (0° Aries = 0.0, 360° = 1.0). Geocoding uses
OpenStreetMap Nominatim; timezones are resolved offline with `timezonefinder`.

## API

### `POST /astro_vector`

```json
{
  "date": "1984-09-23",
  "time": "14:35",
  "place": "Paris, France"
}
```

- `date` (required): `YYYY-MM-DD`, supported range 1900–2100
- `time` (optional): `HH:MM`; defaults to 12:00 and marks `time_accuracy: "low"`
- `place` (required): free-text place name

Response contains an `input` echo block (coordinates, timezone, UTC datetime,
Julian day, time accuracy) plus one block per system. Errors: `400` validation,
`404` place not found, `409` ambiguous place (returns a `candidates` list —
clients should let the user pick and resubmit with the disambiguated name).

Interactive docs at `/docs` (Swagger) and `/redoc`.

## Running

```bash
pip install -r requirements.txt
python run.py            # serves on $PORT (default 8000)
```

Or with Docker:

```bash
docker build -t astro-vector-service .
docker run -p 8000:8000 astro-vector-service
```

### Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `PORT` | Listen port | `8000` |
| `GEOCODER_USER_AGENT` | Identifying User-Agent for Nominatim (include contact info per the [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)) | `astro-vector-service/1.0` |
| `SOURCE_URL` | URL of this source repository, surfaced at `/` | this repo |

## Tests

```bash
python run.py &          # server must be running on localhost:8000
python test_api.py
```

## License

This project is free software, licensed under the
**GNU Affero General Public License v3.0** (see [LICENSE](LICENSE)).

It depends on [pyswisseph](https://github.com/astrorigin/pyswisseph) /
the Swiss Ephemeris by Astrodienst AG, which is available under the AGPL.
If you run a modified version of this service for network users, the AGPL
requires you to offer them the corresponding source code (§13) — the `/`
endpoint's `source` field exists for that purpose; point `SOURCE_URL` at
your fork.
