from geopy.geocoders import Nominatim


class Geolocation:

    def __init__(self):
        self.geolocation_client = self.geolocation_client

    def start_geolocation_client(self):
        geolocator = Nominatim(user_agent="padopia")
        return geolocator

    def get_address(self, property_address):
        location = self.geolocation_client.geocode(property_address, language='en')
        if location is not None:
            result = location.address
        else:
            result = property_address
        return result

    def get_coordinates(self, property_address):
        location = self.geolocation_client.geocode(property_address)
        if location is not None:
            result = {
                'latitude': location.latitude,
                'longitude': location.longitude,
            }
        else:
            result = None
        return result

    def get_address_from_coordinates(self, latitude, longitude):
        if latitude is not None and longitude is not None:
            coordinates = latitude + ', ' + longitude
            location = self.geolocation_client.reverse(coordinates, language='en')
            result = location.address
            return result
        else:
            return None
