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

import sys
import os
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

class LicenseInfo(Popup):
    def __init__(self, **kwargs):
        super(LicenseInfo, self).__init__(**kwargs)
        self.title = 'License'
        self.size_hint = (0.8, 0.8)

        # Determine the path to the LICENSE file
        if hasattr(sys, '_MEIPASS'):
            license_path = os.path.join(sys._MEIPASS, 'LICENSE')
        else:
            license_path = './LICENSE'

        # Load the content of the text file
        with open(license_path, 'r') as file:
            license_text = file.read()

        # Create a layout
        layout = BoxLayout(orientation='vertical')

        # Create a ScrollView for the license text
        scroll_view = ScrollView()
        label = Label(text=license_text, size_hint=(1, None), height=dp(license_text.count('\n') * 19), valign='top')
        scroll_view.add_widget(label)

        # Create an Exit button
        exit_button = Button(text='Close', background_color=(19.6/100, 64.3/100,80.8/100,1),size_hint=(None, None), size=(100, 50))
        exit_button.bind(on_release=self.dismiss)

        # Add widgets to the layout
        layout.add_widget(scroll_view)
        layout.add_widget(exit_button)

        self.add_widget(layout)
