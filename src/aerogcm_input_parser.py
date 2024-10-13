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
        Each object contains start_code, end_code, startcoord, endcoord, and linestyle.
        Supports multiple destinations per input in the format MUC-TPE/SIN.
        """
        pairs = [pair.strip() for pair in input_text.split(',') if '-' in pair]
        parsed_pairs = []

        # Iterate over each ICAO/IATA pair
        for pair in pairs:
            try:
                start_code, destinations = pair.split('-')
                start_code = start_code.strip().upper()

                # Split multiple destinations separated by '/'
                destination_codes = [dest.strip().upper() for dest in destinations.split('/')]

                # Retrieve start airport coordinates
                start_coord = self.get_airport_info(start_code)

                if start_coord:
                    # Iterate over each destination and create an AirportPair object
                    for end_code in destination_codes:
                        end_coord = self.get_airport_info(end_code)

                        if end_coord:
                            parsed_pairs.append(AirportPair(start_code, end_code, start_coord, end_coord))
                        else:
                            print(f"Invalid destination code: {end_code}")
                else:
                    print(f"Invalid start code: {start_code}")
            except ValueError:
                print(f"Invalid input format: {pair}")

        return parsed_pairs
