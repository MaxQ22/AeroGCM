# Coordinate object to hold latitude and longitude
class Coordinate:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

# Object to represent the parsed data for each ICAO/IATA pair before plotting
class AirportPair:
    def __init__(self, start_code, end_code, startcoord, endcoord, linestyle='blue'):
        self.start_code = start_code
        self.end_code = end_code
        self.startcoord = startcoord
        self.endcoord = endcoord
        self.linestyle = linestyle