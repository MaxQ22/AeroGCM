# Import the Kivy framework for the App
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.gridlayout import GridLayout

#Import numpy for some general maths vector handling
import numpy as np

#Import geodesic, to calcualte some map metrics
from geopy.distance import geodesic


# Import Matplotlib to draw the map
import matplotlib.pyplot as plt

# Import Basemap for the plotting of the world map
from mpl_toolkits.basemap import Basemap

# Import airportsdata to get the lat and long coordinates of each airport based on its ICAO/IATA code
import airportsdata

# Import NumPy for numerical operations
import numpy as np

# Import all the global datastructures
from aerogcm_datastructures import *

# Import the input parser that parses the inputs into the dataset for plotting
from aerogcm_input_parser import AirportInputParser

# Set the default window size
Window.size = (1200, 800)

# Main Application Layout
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'  # Layout is now horizontal to fit the map and settings sections

        # Initialize the Input Parser
        self.parser = AirportInputParser()

        # Left side: Settings Menu using Accordion
        settings_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1), padding=10, spacing=10)
        self.add_widget(settings_layout)

        # Accordion for expandable sections
        settings_accordion = Accordion(orientation='vertical')

        # Create Map Style section
        map_style_item = AccordionItem(title='Map Style',orientation = 'vertical')
        map_style_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        map_style_item.add_widget(map_style_layout)

         # Add the On/Off switch to toggle airport labels
        self.airport_label_toggle_switch = Switch(active=True)  # Default is 'on'
        self.airport_label_toggle_switch.bind(active=self.on_airport_label_toggle)  # Bind switch to toggle labels
        # Add label and switch to toggle airport labels
        map_style_layout.add_widget(Label(text="Airport Identifiers"))
        map_style_layout.add_widget(self.airport_label_toggle_switch)      

        # Add the On/Off switch to toggle country lines
        self.country_lines_toggle_switch = Switch(active=False)  # Default is 'off'
        self.country_lines_toggle_switch.bind(active=self.on_country_lines_toggle)  # Bind switch to toggle labels
        # Add label and switch to toggle country lines
        map_style_layout.add_widget(Label(text="Country Lines"))
        map_style_layout.add_widget(self.country_lines_toggle_switch)

        # Add the On/Off switch to toggle city names
        self.city_names_toggle_switch = Switch(active=False)  # Default is 'off'
        self.city_names_toggle_switch.bind(active=self.on_city_names_toggle)  # Bind switch to toggle labels
        # Add label and switch to toggle country lines
        map_style_layout.add_widget(Label(text="City Names"))
        map_style_layout.add_widget(self.city_names_toggle_switch)

        # Create File section
        file_item = AccordionItem(title='File')
        # Exit Button
        self.exit_button = Button(
            text="Exit",
            size_hint=(1,None),
            height=50,
            background_color = (19.6/100, 64.3/100,80.8/100,1),
            color=(1, 1, 1, 1),
            bold=True)
        self.exit_button.bind(on_press=self.exit)
        file_item.add_widget(self.exit_button)

        #Add all items to the accordion
        settings_accordion.add_widget(file_item)
        settings_accordion.add_widget(map_style_item)
        # Add accordion to the settings layout
        settings_layout.add_widget(settings_accordion)

        # Right side: World map (using Matplotlib with Basemap)
        self.map_fig, self.map_ax = plt.subplots()
        self.map_canvas = FigureCanvasKivyAgg(self.map_fig)

        # Initialize the world map
        self.m = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90,
                        llcrnrlon=-180, urcrnrlon=180, resolution='c', ax=self.map_ax)
        # Set the figure background color to black
        self.map_fig.patch.set_facecolor('black')

        # Draw the map boundary with black fill
        self.m.drawmapboundary(fill_color='black')

        # Draw coastlines with white color
        self.m.drawcoastlines(color='white')

        # Fill continents and lakes with colors
        self.m.fillcontinents(color='gray', lake_color='black')

        # Add the map canvas
        self.add_widget(self.map_canvas)

        # Right side: Input section for ICAO/IATA code pairs
        right_layout = BoxLayout(orientation='vertical', size_hint=(0.4, 1), padding=10, spacing=10)
        self.add_widget(right_layout)

        # Title Label
        right_layout.add_widget(Label(
            text="[b]Aero GCM[/b]", 
            markup=True, 
            font_size=24, 
            size_hint_y=None, 
            height=50,
            color=(1, 1, 1, 1),
            bold=True))

        # Instruction Label
        right_layout.add_widget(Label(
            text="Enter ICAO/IATA pairs (e.g., SFO-TPE, KLAX-KEWR)",
            font_size=16,
            size_hint_y=None,
            height=30,
            color=(0.9, 0.9, 0.9, 1)))

        # Scrollable Text input field for ICAO/IATA code pairs
        scroll_view = ScrollView(size_hint=(1, 1))
        self.icao_input = TextInput(
            hint_text="Enter airport code pairs separated by commas",
            size_hint=(1, None),
            height=200,
            multiline=True,
            font_size=16,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1))
        scroll_view.add_widget(self.icao_input)
        right_layout.add_widget(scroll_view)

        #Table to display the flight route lengths
         # Create a ScrollView to make the table scrollable
        self.distance_table_scroll_view = ScrollView()

        # Create a GridLayout with two columns
        self.flight_route_table_layout = GridLayout(cols=2, size_hint_y=None)
        self.flight_route_table_layout.bind(minimum_height=self.flight_route_table_layout.setter('height'))

        # Add headers to the table
        self.flight_route_table_layout.add_widget(Label(text="Flight Route", size_hint_y=None, height=40, bold=True))
        self.flight_route_table_layout.add_widget(Label(text="Distance", size_hint_y=None, height=40, bold=True))
     
        # Add the table layout to the scroll view
        self.distance_table_scroll_view.add_widget(self.flight_route_table_layout)

        #Add the table to the main layout:
        right_layout.add_widget(self.distance_table_scroll_view)        
        
        # Button to plot the great circles
        self.map_button = Button(
            text="Map Routes",
            size_hint_y=None,
            height=50,
            background_color=(19.6/100, 64.3/100,80.8/100,1),
            color=(1, 1, 1, 1),
            bold=True)
        self.map_button.bind(on_press=self.update_map)
        right_layout.add_widget(self.map_button)

        # Default: Show labels (switch default to 'on')
        self.show_labels = True

        # Default: Show country lines (switch default to 'off')
        self.show_country_lines = False

        # Default: Show city names (switch default to 'off')
        self.show_city_names = False

    def exit(self, *args):
        """
        Function to close the Kivy application.
        """
        App.get_running_app().stop()  # Stop the app

    def on_airport_label_toggle(self, instance, value):
        """
        Toggle airport labels based on the switch value.
        True means on, False means off.
        """
        self.show_labels = value
        self.update_map(None)  # Update map when switch is changed
    
    def on_country_lines_toggle(self, instance, value):
        """
        Toggle airport labels based on the switch value.
        True means on, False means off.
        """
        self.show_country_lines = value
        self.update_map(None)  # Update map when switch is changed
    
    def on_city_names_toggle(self, instance, value):
        """
        Toggle city names based on the switch value.
        True means on, False means off.
        """
        self.show_city_names = value
        self.update_map(None)  # Update map when switch is changed

    def sample_great_circle(self, start, end, num_points=100):
        """
        Samples `num_points` along the great circle between two coordinates.
        Uses spherical interpolation for accurate representation.
        Returns two lists: latitudes and longitudes of the sampled points.
        """
        lat1, lon1 = np.radians(start)  # Start point in radians
        lat2, lon2 = np.radians(end)    # End point in radians

        # Compute the great circle points
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        # Compute the angular distance
        a = (np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        # Sample points along the great circle
        lat_points = []
        lon_points = []
        for i in range(num_points + 1):
            f = i / num_points
            A = np.sin((1 - f) * c) / np.sin(c)
            B = np.sin(f * c) / np.sin(c)

            x = A * np.cos(lat1) * np.cos(lon1) + B * np.cos(lat2) * np.cos(lon2)
            y = A * np.cos(lat1) * np.sin(lon1) + B * np.cos(lat2) * np.sin(lon2)
            z = A * np.sin(lat1) + B * np.sin(lat2)

            lat_points.append(np.degrees(np.arctan2(z, np.sqrt(x**2 + y**2))))
            lon_points.append(np.degrees(np.arctan2(y, x)))

        return lat_points, lon_points
    
    def calc_bounding_box(self, parsed_pairs, all_lats, all_lons):
        """
        Function calculates the bounding box of all the great circles, to zoom into the section of the map, that is showing the mapped great circles
        """
        # Initialize lists to store latitudes and longitudes for bounding box calculation by taking the values of the distance rings
        all_lats = all_lats
        all_lons = all_lons

        # Clear the map
        self.map_ax.clear()
        
        # Initialize the world map again
        self.m = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90,
                        llcrnrlon=-180, urcrnrlon=180, resolution='c', ax=self.map_ax)

        # Iterate over parsed pairs and draw great circles manually
        for pair in parsed_pairs:
            # Sample points along the great circle
            start = (pair.startcoord.lat, pair.startcoord.lon)
            end = (pair.endcoord.lat, pair.endcoord.lon)
            lats, lons = self.sample_great_circle(start, end, 100)

            # Add the sampled latitudes and longitudes to the list for bounds calculation
            all_lats.extend(lats)
            all_lons.extend(lons)

        # Determine the bounds of the great circle paths with padding
        min_lat = max(min(all_lats) - 5, -90)
        max_lat = min(max(all_lats) + 5, 90)
        min_lon = max(min(all_lons) - 5, -180)
        max_lon = min(max(all_lons) + 5, 180)

        return min_lat, max_lat, min_lon, max_lon
    
    def plot_airports(self, parsed_pairs, parsed_rings):
        """
        Function plots the airport labels and a dot on every airport.
        Ensures that each airport is plotted only once, even if it appears in multiple lists.
        """
        # Set to store unique airport codes that have already been plotted
        plotted_airports = set()

        # Plot airports from parsed_pairs
        for pair in parsed_pairs:
            # Check if the start airport has been plotted already
            if pair.start_code not in plotted_airports:
                start_coord = self.m(pair.startcoord.lon, pair.startcoord.lat)
                self.map_ax.text(start_coord[0], start_coord[1], pair.start_code, fontsize=10, ha='right', color=pair.color)
                self.map_ax.plot(start_coord[0], start_coord[1], 'o', color=pair.color, markersize=5)
                plotted_airports.add(pair.start_code)  # Add to plotted set

            # Check if the end airport has been plotted already
            if pair.end_code not in plotted_airports:
                end_coord = self.m(pair.endcoord.lon, pair.endcoord.lat)
                self.map_ax.text(end_coord[0], end_coord[1], pair.end_code, fontsize=10, ha='left', color=pair.color)
                self.map_ax.plot(end_coord[0], end_coord[1], 'o', color=pair.color, markersize=5)
                plotted_airports.add(pair.end_code)  # Add to plotted set

        # Plot airports from parsed_rings
        for ring in parsed_rings:
            # Check if the ring's starting airport has been plotted already
            if ring.start_code not in plotted_airports:
                start_coord = self.m(ring.startcoord.lon, ring.startcoord.lat)
                self.map_ax.text(start_coord[0], start_coord[1], ring.start_code, fontsize=10, ha='right', color=ring.color)
                self.map_ax.plot(start_coord[0], start_coord[1], 'o', color=ring.color, markersize=5)
                plotted_airports.add(ring.start_code)  # Add to plotted set
        
    def plot_cities(self):
        """
        Plots markers and names of important world cities on the Basemap instance (self.m).
        """
        # List of major cities with their coordinates (latitude, longitude) and names
        major_cities = [
            {"name": "New York", "lat": 40.7128, "lon": -74.0060},
            {"name": "London", "lat": 51.5074, "lon": -0.1278},
            {"name": "Tokyo", "lat": 35.6895, "lon": 139.6917},
            {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
            {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
            {"name": "Moscow", "lat": 55.7558, "lon": 37.6176},
            {"name": "Cairo", "lat": 30.0444, "lon": 31.2357},
            {"name": "Beijing", "lat": 39.9042, "lon": 116.4074},
            {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
            {"name": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729}
        ]

        # Define marker color in RGBA format
        marker_color = (19.6/100, 64.3/100,80.8/100,1) # Custom color (dark blue-grey)

        # Plot each city on the map
        for city in major_cities:
            # Convert city coordinates to map projection
            x, y = self.m(city["lon"], city["lat"])
            
            # Plot a marker for the city
            self.m.plot(x, y, marker='o', markersize=5, markerfacecolor=marker_color, markeredgewidth=0)
            
            # Add the city name next to the marker
            plt.text(x, y, city["name"], fontsize=10, ha='right', color=marker_color)

    def plot_distance_rings(self, distance_rings):
        """
        Plots the specified distance rings on the Basemap without connecting points across the map boundary.

        Parameters:
        distance_rings (list): List of DistanceRing objects to be plotted.
        """

        all_lats = []
        all_lons = []
        for ring in distance_rings:
            try:
                lat = ring.startcoord.lat 
                lon = ring.startcoord.lon 
                distance_km = ring.distance  # Already in kilometers

                # Generate points every degree around the circle (360 degrees)
                num_points = 360
                circle_points = []

                for angle in np.linspace(0, 360, num_points):
                    # Use geopy's geodesic method to calculate the destination point from the center
                    destination = geodesic(kilometers=distance_km).destination((lat, lon), angle)
                    circle_points.append((destination.latitude, destination.longitude))

                # Extract lats and lons separately for plotting
                circle_lats, circle_lons = zip(*circle_points)

                # Project these lat/lon points to map coordinates
                map_x, map_y = self.m(circle_lons, circle_lats)

                # Check for large jumps in both x and y coordinates to detect boundary crossings
                split_indices = [0]  # Start index for each segment
                for i in range(1, len(map_x)):
                    if (abs(map_x[i] - map_x[i - 1]) > self.m.xmax / 2) or (abs(map_y[i] - map_y[i - 1]) > self.m.ymax / 2):
                        # If a large jump is detected in x or y, add a new segment
                        split_indices.append(i)

                split_indices.append(len(map_x))  # End of the last segment

                # Plot each segment separately to avoid connecting across boundaries
                for i in range(len(split_indices) - 1):
                    start_idx = split_indices[i]
                    end_idx = split_indices[i + 1]
                    self.m.plot(map_x[start_idx:end_idx], map_y[start_idx:end_idx], linewidth=1.5, color=ring.color)

            except Exception as e:
                print(f"Failed to plot ring for {ring.startcoord}: {e}")

            all_lats.extend(circle_lats)
            all_lons.extend(circle_lons)

            #Add the coordinates of the airport of the distance ring, in case the ring is so big, that it does not encompass the destination (eg. 14000km@LAX)
            all_lats.append(lat)
            all_lons.append(lon)

        return all_lats, all_lons

                
    def plot_great_circles(self, parsed_pairs):
        """
        Function plots the great circles onto the map without connecting 
        points across the map boundary in longitude and latitude.
        """
        for pair in parsed_pairs:
            # Sample points along the great circle
            lats, lons = self.sample_great_circle((pair.startcoord.lat, pair.startcoord.lon), 
                                                (pair.endcoord.lat, pair.endcoord.lon), 500)

            # Convert latitude and longitude to map projection coordinates
            x, y = self.m(lons, lats)

            # Check for large jumps in both x and y coordinates
            split_indices = [0]  # Start index for each segment
            for i in range(1, len(x)):
                if (abs(x[i] - x[i - 1]) > self.m.xmax / 2) or (abs(y[i] - y[i - 1]) > self.m.ymax / 2): 
                    # If a large jump is detected in longitude (x) or latitude (y)
                    split_indices.append(i)  # Start a new segment

            split_indices.append(len(x))  # End of the last segment

            print(split_indices)
            # Plot each segment separately to avoid connecting across boundaries
            for i in range(len(split_indices) - 1):
                start_idx = split_indices[i]
                end_idx = split_indices[i + 1]
                self.m.plot(x[start_idx:end_idx], y[start_idx:end_idx], linewidth=2, color=pair.color)

     # Function to update the flight route distance table with new data
    def update_flight_route_table(self, flight_data_list):
        """
        Updates the flight route table with the current routes and corresponding distances
        """
        # Clear existing data rows (keeping the headers)
        self.flight_route_table_layout.clear_widgets()
        
        # Re-add headers
        self.flight_route_table_layout.add_widget(Label(text="Flight Route", size_hint_y=None, height=40, bold=True))
        self.flight_route_table_layout.add_widget(Label(text="Distance", size_hint_y=None, height=40, bold=True))

        # Populate the table with the new flight data
        for flight in flight_data_list:
            self.flight_route_table_layout.add_widget(Label(text=flight.route, size_hint_y=None, height=30))
            self.flight_route_table_layout.add_widget(Label(text=f"{flight.distancekm:.2f} km", size_hint_y=None, height=30))
    
    def update_map(self, instance):
        """
        Updates the map by drawing great circles based on the parsed ICAO/IATA pairs
        and adjusts the map boundaries to fit all great circles.
        """
        # Get the parsed ICAO/IATA pairs from the input
        input_text = self.icao_input.text.strip()
        parsed_pairs, parsed_rings = self.parser.parseInput(input_text)

        #If the Update Map Button was pressed, also update the Flight Route Distance Table
        self.update_flight_route_table(self.parser.calculate_route_distance(input_text))
        
        # If no valid pairs, skip updating
        if not (parsed_pairs or parsed_rings):
            return

        #Use the plot distance ring function, to calculate the lats and lons of the distance ring for bounding box calculation
        all_lats, all_lons = self.plot_distance_rings(parsed_rings)

        #Calculate the bounding box, in which all the distance rings and great circles are contained to zoom the map
        min_lat, max_lat, min_lon, max_lon = self.calc_bounding_box(parsed_pairs, all_lats, all_lons)

        # Clear the map and reset the map view with new bounds
        self.map_ax.clear()
        self.m = Basemap(projection='mill',
                        llcrnrlat=min_lat, urcrnrlat=max_lat,
                        llcrnrlon=min_lon, urcrnrlon=max_lon,
                        resolution='l', ax=self.map_ax)
        # Set the figure background color to black
        self.map_fig.patch.set_facecolor('black')

        # Draw the map boundary with black fill
        self.m.drawmapboundary(fill_color='black')

        # Draw coastlines with white color
        self.m.drawcoastlines(color='white')

        # Fill continents and lakes with colors
        self.m.fillcontinents(color='gray', lake_color='black')

        #Draw the Country Lines, if desired
        if self.show_country_lines == True:
            # Optionally draw countries
            self.m.drawcountries(color='lightgray')

        # Plot the great circles again after setting the new boundaries
        self.plot_great_circles(parsed_pairs)

        #Plot the distance rings around the airport
        self.plot_distance_rings(parsed_rings)

        # Plot the airports, if desired
        if self.show_labels:
            #Optionally draw airport names
            self.plot_airports(parsed_pairs, parsed_rings)

        #Plot the city names, if that is desired
        if self.show_city_names == True:
            #Optionally draw city names of some known cities
            self.plot_cities()

        # Refresh the map with the new great circles
        self.map_canvas.draw()


# Main Kivy App
class AeroGCMApp(App):
    def build(self):
        return MainLayout()

# Run the application
if __name__ == "__main__":
    AeroGCMApp().run()
