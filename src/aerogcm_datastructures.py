""""
AeroGCM - A Application to visualize and analyze flight routes
    Copyright (C) 2025  MaxQ22

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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

#Object to represent a distance ring
class DistanceRing:
    def __init__(self,start_code,startcoord , distance, linestyle='line', color=(19.6/100, 64.3/100,80.8/100,1)):
        self.start_code = start_code
        self.startcoord = startcoord
        self.linestyle = linestyle
        self.color = color
        self.distance = distance

#Object to represent a flight route distance
class FlightRouteDistance:
    def __init__(self, route, distance):
        self.route = route
        self.distancekm = distance
        self.distancenm = distance * 0.539957

