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

import threading
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import airportsdata

"""
CityAirportSearch
------------------
This module provides a Kivy Popup dialog for searching airports by city name.
Features:
- User can enter a city name (partial matches allowed)
- Results are shown in a scrollable table with airport name and identifier
- Clicking an identifier inserts it into the main ICAO/IATA input field
- Entry field is focused when popup opens, and pressing Enter triggers search
"""

# Main class for the city airport search popup
class CityAirportSearch(Popup):
    def __init__(self, main_layout, **kwargs):
        """
        Initialize the popup dialog and its widgets.
        main_layout: Reference to the main app layout (for updating ICAO/IATA field)
        """
        super().__init__(**kwargs)
        self.main_layout = main_layout
        self.title = "City Airport Search"
        self.size_hint = (0.8, 0.8)

        # Main vertical layout for the popup
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Load airports database once for performance
        self.airports = airportsdata.load('ICAO')

        # TextInput for city name entry
        self.search_input = TextInput(
            hint_text="Enter city name",
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.search_input)

        # Button to trigger airport search
        search_btn = Button(
            text="Search",
            size_hint_y=None,
            height=40
        )
        search_btn.bind(on_press=self.search_airports)
        layout.add_widget(search_btn)

        # ScrollView and GridLayout for displaying search results
        self.scroll_view = ScrollView()
        self.table_layout = GridLayout(cols=2, size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))
        self.scroll_view.add_widget(self.table_layout)
        layout.add_widget(self.scroll_view)

        # Label for status/info messages
        self.info_label = Label(text="", size_hint_y=None, height=30)
        layout.add_widget(self.info_label)

        # Set the popup content
        self.content = layout

    def on_open(self):
        """
        Called when the popup is opened.
        Sets focus to the entry field and binds Enter key to search.
        """
        super().on_open()
        self.search_input.focus = True
        self.search_input.bind(on_text_validate=self.search_airports)

    def search_airports(self, *args):
        """
        Search for airports matching the entered city name (partial matches allowed).
        Populates the table with airport name and identifier.
        """
        city_name = self.search_input.text.strip().lower()
        self.table_layout.clear_widgets()
        # Add table headers
        self.table_layout.add_widget(Label(text="Airport Name", bold=True, size_hint_y=None, height=30))
        self.table_layout.add_widget(Label(text="Identifier", bold=True, size_hint_y=None, height=30))

        airports = airportsdata.load('ICAO')
        found = []
        # Search for airports where the city name contains the entered phrase
        for ident, data in airports.items():
            city = data.get('city', '').lower()
            if city_name in city:
                found.append((data.get('name', ''), ident))

        if not found:
            self.info_label.text = "No airports found for this city."
            return
        self.info_label.text = f"Found {len(found)} airports."

        # Add each found airport to the table
        for name, ident in found:
            name_lbl = Label(text=name, size_hint_y=None, height=30)
            ident_btn = Button(text=ident, size_hint_y=None, height=30)
            # Bind button to select_airport to insert identifier into main input
            ident_btn.bind(on_press=lambda btn, i=ident: self.select_airport(i))
            self.table_layout.add_widget(name_lbl)
            self.table_layout.add_widget(ident_btn)

    def _search_airports_thread(self, city_phrase):
        found = []
        if city_phrase:
            for ident, data in self.airports.items():
                city = data.get('city', '').lower()
                if city_phrase in city:
                    found.append((data.get('name', ''), ident))
        # Schedule UI update on the main thread
        Clock.schedule_once(lambda dt: self._update_results(found, city_phrase))

    def _update_results(self, found, city_phrase):
        self.table_layout.clear_widgets()
        # Add table headers
        self.table_layout.add_widget(Label(text="Airport Name", bold=True, size_hint_y=None, height=30))
        self.table_layout.add_widget(Label(text="Identifier", bold=True, size_hint_y=None, height=30))

        if not city_phrase:
            self.info_label.text = "Enter a city name to search."
            return

        if not found:
            self.info_label.text = "No airports found for this city."
            return
        self.info_label.text = f"Found {len(found)} airports."

        # Add each found airport to the table
        for name, ident in found:
            name_lbl = Label(text=name, size_hint_y=None, height=30)
            ident_btn = Button(text=ident, size_hint_y=None, height=30)
            # Bind button to select_airport to insert identifier
            ident_btn.bind(on_press=lambda btn, i=ident: self.select_airport(i))
            self.table_layout.add_widget(name_lbl)
            self.table_layout.add_widget(ident_btn)

    def select_airport(self, ident):
        """
        Insert the selected airport identifier into the main ICAO/IATA input field.
        Uses '-' as a separator if needed, then closes the popup.
        """
        current_text = self.main_layout.icao_input.text.strip()
        if current_text and not current_text.endswith('-') and current_text:
            current_text += '-'
        self.main_layout.icao_input.text = current_text + ident
        self.dismiss()
