from astro_vector_service.geocoding import geocode_place, AmbiguousLocationError

try:
    geocode_place('Springfield')
    print('[FAIL] Should have raised AmbiguousLocationError')
except AmbiguousLocationError as e:
    print('[PASS] Ambiguous location detected!')
    print(f'Message: {e}')
    print('Candidates:')
    for c in e.candidates:
        print(f'  - {c["place"]} ({c["lat"]}, {c["lon"]})')
