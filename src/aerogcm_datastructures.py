# Coordinate object to hold latitude and longitude
class Coordinate:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

# Object to represent the parsed data for each ICAO/IATA pair before plotting
class AirportPair:
    def __init__(self, start_code, end_code, startcoord, endcoord, linestyle='line', color=(19.6/100, 64.3/100,80.8/100,1)):
        self.start_code = start_code
        self.end_code = end_code
        self.startcoord = startcoord
        self.endcoord = endcoord
        self.linestyle = linestyle
        self.color = color

class DistanceRing:
    def __init__(self,start_code,startcoord , distance, linestyle='line', color=(19.6/100, 64.3/100,80.8/100,1)):
        self.start_code = start_code
        self.startcoord = startcoord
        self.linestyle = linestyle
        self.color = color
        self.distance = distance

