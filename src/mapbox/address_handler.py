from api_wrapper.geo_api import MapboxAPI
import dotenv
import os

class AddressHandler(MapboxAPI):

    def __init__(self):

        dotenv.load_dotenv()
        self.key = os.environ['MAPBOX_APIKEY']
        super().__init__(self.key)

    def get_address_json(self, address_str):

        address_json = self.get_geocode_json(address_str)

        return address_json

    def get_iso_json(self, lat, lng):

        iso_json = self.get_iso_json(lat, lng)

        return iso_json

    def get_map_features(self, address_str):

        address_json = self.get_address_json(address_str=address_str)
        coordinates = address_json['features'][0]['geometry']['coordinates']
        lng, lat = coordinates

        place_name = address_json['features'][0]['place_name']

        iso_json = self.get_iso_json(lat, lng)

        return place_name, coordinates, iso_json

if __name__ == '__main__':

    add_hand = AddressHandler()

    address_json = add_hand.get_address_json('2329 S Eldridge St Lakewood CO')
    import ipdb; ipdb.set_trace()