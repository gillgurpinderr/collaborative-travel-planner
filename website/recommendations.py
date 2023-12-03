import googlemaps
import requests
from geopy.geocoders import Nominatim
from .secret import GOOGLE_API_KEY

map = googlemaps.Client(GOOGLE_API_KEY)
geolocator = Nominatim(user_agent="place-locator")

def find_locations(location, radius=1000, keyword=None, types=None):
    location_coordinates = geolocator.geocode(location)
    
    if location_coordinates:
        places_result = map.places_nearby(
            location=(location_coordinates.latitude, location_coordinates.longitude),
            radius=radius,
            open_now=False,
            keyword=keyword,
            type=types
        )

        places = places_result.get('results', [])
        return places
    else:
        print("Can't find coordinates the location")
        return []

def get_location_details(place_id):
    url = f'https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={GOOGLE_API_KEY}'

    response = requests.get(url)
    data = response.json()

    if 'result' in data:
        rating = data['result'].get('rating', 'N/A')
        photos = data['result'].get('photos', [])
        
        photo_url = ''
        if photos:
            photo_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photos[0]["photo_reference"]}&key={GOOGLE_API_KEY}'

        return rating, photo_url
    else:
        return 'N/A', ''

def recommend_locations(user_city, distance_filter, keyword):

    recommended_places_with_ratings = []

    places = find_locations(user_city, radius=distance_filter, keyword=keyword, types=keyword)

    for place in places[0:5]:
        place_id = place.get('place_id')
        if place_id:
            rating, photo_url = get_location_details(place_id)
            recommended_places_with_ratings.append({
                'name': place['name'],
                'address': place['vicinity'],
                'rating': rating,
                'photo_url': photo_url
            })

    sorted_places = sorted(recommended_places_with_ratings, key=lambda x: float(x['rating']) if x['rating'] != 'N/A' else None, reverse=True)

    return sorted_places

if __name__ == "__main__":
    search_input = input("Enter what you want to search for: ")

    recommended_places = recommend_locations(user_city="NYC", distance_filter=5000, keyword=search_input)

    print("\nRecommended Places (sorted by rating):")
    for place in recommended_places:
        print(f"{place['name']}: {place['address']} - Rating: {place['rating']}")
        print("Photo URL:")
        print(place['photo_url'])