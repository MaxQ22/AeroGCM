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

    def parseInput(self, input_text):
        """
        Parses the input and returns a list of AirportPair objects.
        Supports concatenated legs (e.g., LAX-EWR-MUC), multi-destination options (e.g., LAX-EWR/ORD-MUC),
        and multiple starting points (e.g., LAX/SFO-MUC).
        """
        # Split by commas to handle multiple routes
        routes = [route.strip() for route in input_text.split(',') if '-' in route]
        parsed_pairs = []

        # Iterate over each route (e.g., LAX-EWR/ORD-MUC or LAX/SFO-MUC)
        for route in routes:
            try:
                # Split by '-' to handle legs in series (LAX-EWR-MUC)
                legs = [leg.strip() for leg in route.split('-')]

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
                                    parsed_pairs.append(AirportPair(start_code, end_code, start_coord, end_coord))
                                else:
                                    print(f"Invalid destination code: {end_code}")
                        else:
                            print(f"Invalid start code: {start_code}")

                    # Set the current end_codes as the new start_codes for the next leg
                    start_codes = end_codes  # Move to the destinations for the next leg
            except ValueError:
                print(f"Invalid input format: {route}")

        return parsed_pairs


