import re 
import itertools
from math import radians, sin, cos, sqrt, atan2

#Import airportsdata to get the lat and long coordinates of each airport based on its ICAO/IATA code
import airportsdata

#Import all the global datastructures
from aerogcm_datastructures import *

#Import all the global datastructures
from aerogcm_datastructures import *

class AirportInputParser:
    def __init__(self):
        """ Load the ICAO and IATA airport data. """
        self.airports_icao = airportsdata.load("ICAO")
        self.airports_iata = airportsdata.load("IATA")      
    
    def get_airport_info(self, code):
        """
        Retrieve airport info (latitude and longitude) by ICAO or IATA code.
        Returns a Coordinate object if found, otherwise None.
        """
        code = code.strip().upper()
        if code in self.airports_icao:
            airport = self.airports_icao[code]
            return Coordinate(airport['lat'], airport['lon'])
        elif code in self.airports_iata:
            airport = self.airports_iata[code]
            return Coordinate(airport['lat'], airport['lon'])
        else:
            return None
    
    def haversine_distance(self, coord1, coord2):
        # Calculate great-circle distance using the Haversine formula
        R = 6371.0  # Radius of the Earth in km
        lat1, lon1 = radians(coord1.lat), radians(coord1.lon)
        lat2, lon2 = radians(coord2.lat), radians(coord2.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
    
    def calculate_route_distance(self, route_string):
        routes = route_string.split(',')
        results = []

        for route in routes:
            if '-' not in route:
                continue  # Ignore invalid tokens

            # Split the route into segments, handling '/' separators
            segments = route.split('-')
            expanded_routes = [[]]

            for segment in segments:
                options = segment.split('/')
                expanded_routes = [r + [opt] for r in expanded_routes for opt in options]

            for expanded_route in expanded_routes:
                total_distance = 0
                route_str = '-'.join(expanded_route)

                # Calculate the distance for the full route
                for i in range(len(expanded_route) - 1):
                    start = self.get_airport_info(expanded_route[i])
                    end = self.get_airport_info(expanded_route[i + 1])

                    if start and end:
                        total_distance += self.haversine_distance(start, end)
                    else:
                        total_distance = None
                        break  # If any airport info is missing, skip this route

                if total_distance is not None:
                    results.append(FlightRouteDistance(route_str, total_distance))

        return results
        
     # Helper method to convert color names to RGB format (values from 0 to 1)
    def convert_color_name_to_rgb(self, color_name):
        color_dict = {
            'RED': (1.0, 0.0, 0.0),
            'GREEN': (0.0, 1.0, 0.0),
            'BLUE': (0.0, 0.0, 1.0),
            'YELLOW': (1.0, 1.0, 0.0),
            'WHITE': (1.0, 1.0, 1.0),
            'BLACK': (0.0, 0.0, 0.0),
        }
        return color_dict.get(color_name, None)  # Return None if color is not recognized

    def parseInput(self, input_text):
        """
        Parses the input and returns a list of AirportPair objects and DistanceRing objects with optional color information.
        Colors can be specified by name (e.g., RED, GREEN) and will apply to all subsequent routes and distance rings until another color is provided.
        """
        # Split input by commas to handle multiple routes and color changes
        tokens = [token.strip() for token in input_text.split(',')]
        parsed_pairs = []
        parsed_rings = []  # List for storing DistanceRing objects

        # Set color to default color
        current_color = (19.6/100, 64.3/100,80.8/100,1)

        # Iterate over each token in the input
        for token in tokens:
            # Check if the token is a color (by name)
            if token.upper() in ['RED', 'GREEN', 'BLUE', 'YELLOW', 'WHITE', 'BLACK']:
                current_color = self.convert_color_name_to_rgb(token.upper())
            
            # Check if the token is a valid distance ring (e.g., 900nm@LHR or 1500km@SFO)
            elif '@' in token and ('nm' in token or 'km' in token):
                try:
                    # Split the token into distance and airport code
                    distance_part, airport_code = token.split('@')
                    airport_code = airport_code.strip().upper()
                    distance_part = distance_part.strip().lower()

                    # Convert distance to kilometers if necessary
                    if 'nm' in distance_part:
                        distance = float(distance_part.replace('nm', '')) * 1.852  # Convert nm to km
                    elif 'km' in distance_part:
                        distance = float(distance_part.replace('km', ''))  # Already in km
                    else:
                        raise ValueError(f"Invalid distance format: {distance_part}")

                    # Retrieve coordinates for the start airport
                    start_coord = self.get_airport_info(airport_code)
           
                    parsed_rings.append(DistanceRing(airport_code, start_coord, distance, color=current_color))

                except ValueError:
                    print(f"Invalid input format: {token}")

            elif '-' in token:  # Check if the token is a valid route (contains '-')
                try:
                    # Split by '-' to handle legs in series (e.g., LAX-EWR or SFO-LAX)
                    legs = [leg.strip() for leg in token.split('-')]

                    # First leg can have multiple starting airports, split by '/'
                    start_codes = [start.strip().upper() for start in legs[0].split('/')]

                    # Iterate over the remaining legs in the series
                    for i in range(1, len(legs)):
                        # Split by '/' to handle multiple destination options at each step
                        end_codes = [end.strip().upper() for end in legs[i].split('/')]

                        # Retrieve coordinates for each start airport
                        for start_code in start_codes:
                            start_coord = self.get_airport_info(start_code)

                            if start_coord:
                                # Iterate over each destination option and create AirportPair objects
                                for end_code in end_codes:
                                    end_coord = self.get_airport_info(end_code)

                                    if end_coord:
                                        # Create an AirportPair with the current color
                                        parsed_pairs.append(AirportPair(start_code, end_code, start_coord, end_coord, color=current_color))
                                    else:
                                        print(f"Invalid destination code: {end_code}")
                            else:
                                print(f"Invalid start code: {start_code}")

                        # Set the current end_codes as the new start_codes for the next leg
                        start_codes = end_codes  # Move to the destinations for the next leg

                except ValueError:
                    print(f"Invalid input format: {token}")
            else:
                # If token is neither a color, a distance ring, nor a valid route, print an error message
                print(f"Invalid token: {token}")

        return parsed_pairs, parsed_rings
