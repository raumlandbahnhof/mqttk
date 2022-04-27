"""
MQTTk - Lightweight graphical MQTT client and message analyser

Copyright (C) 2022  Máté Szabó

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
import tkinter.ttk as ttk
from mqttk.widgets.scrolled_text import CustomScrolledText


class LogTab(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.master = master
        self.log_output = CustomScrolledText(self, font="Courier 14", exportselection=False, state='disabled',
                                             background="white", foreground="black")
        self.log_output.pack(fill='both', expand=1, padx=3, pady=3)
        self.selected = False

    def add_message(self, message):
        self.log_output.configure(state="normal")
        self.log_output.insert(tk.END, message)
        self.log_output.see(tk.END)
        self.log_output.configure(state="disabled")
        if self.selected:
            self.mark_as_read()

    def mark_as_read(self, *args, **kwargs):
        self.master.tab(self, text="Log")

    def notify(self):
        self.master.tab(self, text="* Log *")

    def tab_selected(self):
        self.selected = True
        self.mark_as_read()

    def tab_deselected(self):
        self.selected = False
