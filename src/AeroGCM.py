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
from kivy.uix.dropdown import DropDown
from kivy.uix.accordion import Accordion, AccordionItem

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
        map_style_layout.add_widget(Label(text="Show Country Lines"))
        map_style_layout.add_widget(self.country_lines_toggle_switch)

        # Create File section
        file_item = AccordionItem(title='File')
        # Exit Button
        self.exit_button = Button(
            text="Exit",
            size_hint=(1,None),
            height=50,
            background_color=(0.3, 0.5, 0.7, 1),
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

        # Button to plot the great circles
        self.map_button = Button(
            text="Map Routes",
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            bold=True)
        self.map_button.bind(on_press=self.update_map)
        right_layout.add_widget(self.map_button)

        # Default: Show labels (switch default to 'on')
        self.show_labels = True

        # Default: Show country lines (switch default to 'off')
        self.show_country_lines = False

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
    
    def calc_bounding_box(self, parsed_pairs):
        # Initialize lists to store latitudes and longitudes for bounding box calculation
        all_lats = []
        all_lons = []

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

            # Convert latitude and longitude to map projection coordinates
            x, y = self.m(lons, lats)

            # Plot the great circle on the map using the projected coordinates
            self.m.plot(x, y, linewidth=2, color=pair.linestyle)

        # Determine the bounds of the great circle paths with padding
        min_lat = max(min(all_lats) - 5, -90)
        max_lat = min(max(all_lats) + 5, 90)
        min_lon = max(min(all_lons) - 5, -180)
        max_lon = min(max(all_lons) + 5, 180)

        return min_lat, max_lat, min_lon, max_lon
    
    def plot_airports(self, parsed_pairs):
        if self.show_labels:
            for pair in parsed_pairs:
            # Plot airport labels if the switch is on (self.show_labels is True)
                # Get airport coordinates
                start_coord = self.m(pair.startcoord.lon, pair.startcoord.lat)
                end_coord = self.m(pair.endcoord.lon, pair.endcoord.lat)

                # Add labels next to the airports
                self.map_ax.text(start_coord[0], start_coord[1], pair.start_code, fontsize=10, ha='right', color='blue')
                self.map_ax.text(end_coord[0], end_coord[1], pair.end_code, fontsize=10, ha='left', color='blue')
                self.map_ax.plot(start_coord[0], start_coord[1], 'o', color='blue', markersize=5)  
                self.map_ax.plot(end_coord[0], end_coord[1], 'o', color='blue', markersize=5)  

    
    def plot_great_circles(self, parsed_pairs):
        for pair in parsed_pairs:
            # Sample points along the great circle
            lats, lons = self.sample_great_circle((pair.startcoord.lat, pair.startcoord.lon), 
                                                (pair.endcoord.lat, pair.endcoord.lon), 500)

            # Convert latitude and longitude to map projection coordinates
            x, y = self.m(lons, lats)

            # Plot the great circle
            self.m.plot(x, y, linewidth=2, color=pair.linestyle)

    def update_map(self, instance):
        """
        Updates the map by drawing great circles based on the parsed ICAO/IATA pairs
        and adjusts the map boundaries to fit all great circles.
        """
        # Get the parsed ICAO/IATA pairs from the input
        input_text = self.icao_input.text.strip()
        parsed_pairs = self.parser.parseInput(input_text)

        # If no valid pairs, skip updating
        if not parsed_pairs:
            return

        min_lat, max_lat, min_lon, max_lon = self.calc_bounding_box(parsed_pairs)

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

        # Plot the airports
        self.plot_airports(parsed_pairs)

        # Refresh the map with the new great circles
        self.map_canvas.draw()


# Main Kivy App
class AeroGCMApp(App):
    def build(self):
        return MainLayout()

# Run the application
if __name__ == "__main__":
    AeroGCMApp().run()
