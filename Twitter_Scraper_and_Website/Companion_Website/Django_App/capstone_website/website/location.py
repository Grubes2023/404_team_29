import requests

#using the google maps api key
api_key = 'AIzaSyCR7zdAySylDKuqKwvMNXBIupwBYts4m84'
#zipcode inputs
zip_code = '77840'

# Make API request to Google Maps Geocoding API
url = f'https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={api_key}'
response = requests.get(url)
data = response.json()

# Extract longitude and latitude from API response
if data['status'] == 'OK':
    location = data['results'][0]['geometry']['location']
    longitude = location['lng']
    latitude = location['lat']
    print(f'Longitude: {longitude}')
    print(f'Latitude: {latitude}')
else:
    print('Error: Could not geocode zip code')