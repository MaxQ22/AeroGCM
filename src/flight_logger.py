"""
AeroGCM - Flight Logger
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

import os
import csv
import io
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserIconView

class FlightLogger(Popup):
    # Class variable to persist CSV string between popups
    csv_data = None

    def __init__(self, main_layout, **kwargs):
        super().__init__(**kwargs)
        self.title = "Flight Logger"
        self.size_hint = (0.9, 0.9)
        self.main_layout = main_layout

        # Main layout for the popup
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Table to display logged flights
        self.flight_table_scroll_view = ScrollView()
        self.flight_table_layout = GridLayout(cols=10, size_hint_y=None)
        self.flight_table_layout.bind(minimum_height=self.flight_table_layout.setter('height'))
        self.flight_table_scroll_view.add_widget(self.flight_table_layout)
        layout.add_widget(self.flight_table_scroll_view)

        # Buttons for file operations and adding new flights
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        open_button = Button(text="Open File", size_hint=(1, None), height=50)
        open_button.bind(on_press=self.open_file)
        button_layout.add_widget(open_button)

        save_button = Button(text="Save File", size_hint=(1, None), height=50)
        save_button.bind(on_press=self.save_file)
        button_layout.add_widget(save_button)

        add_button = Button(text="Add Flight", size_hint=(1, None), height=50)
        add_button.bind(on_press=self.add_flight)
        button_layout.add_widget(add_button)

        plot_button = Button(text="Plot", size_hint=(1, None), height=50)
        plot_button.bind(on_press=self.plot_flights)
        button_layout.add_widget(plot_button)

        layout.add_widget(button_layout)

        # Close Button
        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 50),
            background_color=(19.6/100, 64.3/100, 80.8/100, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        close_button.bind(on_press=self.dismiss)

        # Adjust layout to position the Close button at the bottom left
        layout.add_widget(close_button)

        self.content = layout

        # List to store flight data
        self.flights = []
        # Load from csv_data if available
        if FlightLogger.csv_data:
            self._load_from_csv_string(FlightLogger.csv_data)
            self.update_table()

    def _save_to_csv_string(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(self.flights)
        FlightLogger.csv_data = output.getvalue()

    def _load_from_csv_string(self, csv_string):
        input_io = io.StringIO(csv_string)
        reader = csv.reader(input_io)
        self.flights = list(reader)

    def open_file(self, *args):
        file_chooser = FileChooserIconView()
        file_chooser.path = os.getcwd()
        file_chooser.filters = [lambda folder, filename: filename.endswith('.csv')]
        file_chooser.bind(selection=lambda instance, selection: self.load_file(selection))

        self.file_popup = Popup(title='Open Flight Log File', content=file_chooser, size_hint=(0.9, 0.9))
        self.file_popup.open()

    def load_file(self, selection):
        if selection:
            file_path = selection[0]
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                self.flights = list(reader)

            self.update_table()
        self.file_popup.dismiss()

    def save_file(self, *args):
        file_chooser = FileChooserIconView()
        file_chooser.path = os.getcwd()
        file_chooser.filters = [lambda folder, filename: filename.endswith('.csv')]
        file_chooser.bind(selection=lambda instance, selection: self.save_to_file(selection))

        # Create a BoxLayout to hold the filename input and save button
        filename_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)

        # Filename TextInput
        self.filename_input = TextInput(hint_text='Enter filename', multiline=False)
        filename_layout.add_widget(self.filename_input)

        # Save Button
        save_button = Button(text='Save', size_hint=(None, None), size=(100, 50))
        save_button.bind(on_press=lambda instance: self.save_to_file([os.path.join(file_chooser.path, self.filename_input.text + '.csv')]))
        filename_layout.add_widget(save_button)

        # Create a popup and add the file chooser and filename layout to it
        self.file_popup = Popup(title='Save Flight Log File', content=BoxLayout(orientation='vertical', spacing=10, padding=10), size_hint=(0.9, 0.9))
        self.file_popup.content.add_widget(file_chooser)
        self.file_popup.content.add_widget(filename_layout)

        # Open the file chooser popup
        self.file_popup.open()

    def save_to_file(self, selection):
        if selection:
            file_path = selection[0]
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(self.flights)
        self.file_popup.dismiss()

    def add_flight(self, *args):
        add_popup = AddFlightPopup(self)
        add_popup.open()

    def remove_flight(self, flight):
        self.flights.remove(flight)
        self._save_to_csv_string()
        self.update_table()


    def update_table(self):
        self.flight_table_layout.clear_widgets()

        headers = ["Departure Time", "Arrival Time", "Airline", "Callsign", "Airplane Type", "Registration", "Origin", "Destination", "Remove", "Edit"]
        for header in headers:
            self.flight_table_layout.add_widget(Label(text=header, size_hint_y=None, height=40, bold=True))

        for idx, flight in enumerate(self.flights):
            # Add all 8 fields
            for field in flight:
                self.flight_table_layout.add_widget(Label(text=field, size_hint_y=None, height=30))
            # Add Remove and Edit buttons in the same row
            remove_button = Button(text="Remove", size_hint_y=None, height=30)
            remove_button.bind(on_press=lambda instance, f=flight: self.remove_flight(f))
            edit_button = Button(text="Edit", size_hint_y=None, height=30)
            edit_button.bind(on_press=lambda instance, i=idx: self.edit_flight(i))
            self.flight_table_layout.add_widget(remove_button)
            self.flight_table_layout.add_widget(edit_button)

        self._save_to_csv_string()
    def edit_flight(self, flight_index):
        edit_popup = EditFlightPopup(self, flight_index)
        edit_popup.open()

    def plot_flights(self, *args):
        routes = [f"{flight[6]}-{flight[7]}" for flight in self.flights]
        self.main_layout.icao_input.text = ','.join(routes)
        self.main_layout.update_map(None)
        self._save_to_csv_string()
        self.dismiss()


class AddFlightPopup(Popup):
    def __init__(self, flight_logger, **kwargs):
        super().__init__(**kwargs)
        self.title = "Add Flight"
        self.size_hint = (0.8, 0.8)
        self.flight_logger = flight_logger

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.fields = {}
        self.field_names = ["Departure Time", "Arrival Time", "Airline", "Callsign", "Airplane Type", "Registration", "Origin", "Destination"]
        for field in self.field_names:
            field_layout = BoxLayout(size_hint_y=None, height=50)
            field_layout.add_widget(Label(text=field, size_hint_x=0.4))
            text_input = TextInput(size_hint_x=0.6)
            field_layout.add_widget(text_input)
            self.fields[field] = text_input
            layout.add_widget(field_layout)

        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        add_button = Button(text="Add", size_hint=(1, None), height=50)
        add_button.bind(on_press=self.add_flight)
        button_layout.add_widget(add_button)

        cancel_button = Button(text="Cancel", size_hint=(1, None), height=50)
        cancel_button.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.content = layout

    def add_flight(self, *args):
        flight = [self.fields[field].text for field in self.field_names]
        self.flight_logger.flights.append(flight)
        self.flight_logger.update_table()
        self.dismiss()


# New popup for editing flights
class EditFlightPopup(Popup):
    def __init__(self, flight_logger, flight_index, **kwargs):
        super().__init__(**kwargs)
        self.title = "Edit Flight"
        self.size_hint = (0.8, 0.8)
        self.flight_logger = flight_logger
        self.flight_index = flight_index

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.fields = {}
        self.field_names = ["Departure Time", "Arrival Time", "Airline", "Callsign", "Airplane Type", "Registration", "Origin", "Destination"]
        flight_data = self.flight_logger.flights[self.flight_index]
        for i, field in enumerate(self.field_names):
            field_layout = BoxLayout(size_hint_y=None, height=50)
            field_layout.add_widget(Label(text=field, size_hint_x=0.4))
            text_input = TextInput(size_hint_x=0.6)
            # Pre-fill with existing data
            if i < len(flight_data):
                text_input.text = flight_data[i]
            field_layout.add_widget(text_input)
            self.fields[field] = text_input
            layout.add_widget(field_layout)

        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        save_button = Button(text="Save", size_hint=(1, None), height=50)
        save_button.bind(on_press=self.save_flight)
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", size_hint=(1, None), height=50)
        cancel_button.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.content = layout

    def save_flight(self, *args):
        updated_flight = [self.fields[field].text for field in self.field_names]
        self.flight_logger.flights[self.flight_index] = updated_flight
        self.flight_logger.update_table()
        self.dismiss()