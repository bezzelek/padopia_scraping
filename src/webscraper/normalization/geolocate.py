from geopy.geocoders import Nominatim


class Geolocation:

    def __init__(self):
        self.geolocation_client = self.geolocation_client

    def start_geolocation_client(self):
        geolocator = Nominatim(user_agent="padopia")
        return geolocator

    def get_address(self, property_address):
        location = self.geolocation_client.geocode(property_address, language='en')
        result = location.address
        return result

    def get_coordinates(self, property_address):
        location = self.geolocation_client.geocode(property_address)
        result = {
            'latitude': location.latitude,
            'longitude': location.longitude,
        }
        return result
