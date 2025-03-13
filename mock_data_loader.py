import tkinter as tk
from tkinter import ttk

class MockDataLoader:
    def __init__ (self, root, access_pattern_var):
        self.root = root
        self.access_pattern_var = access_pattern_var
        self.patterns = {
            'Sequential': '0 1 2 3 4 5 6 7 8 9',
            'Random': '3 1 4 1 5 9 2 6 5 3',
            'Loop': '0 1 2 3 0 1 2 3 0 1',
            'Repeated': '1 1 1 2 2 2 3 3 3 4',
            'Mixed': '0 1 0 2 0 3 0 4 0 5'
        }

    def create_loader_ui(self, container):
        loader_frame = ttk.LabelFrame(container, text='Mock Data Patterns', padding='5')
        loader_frame.pack(fill=tk.X, padx=0, pady=5)

        for i, (pattern_name, pattern) in enumerate(self.patterns.items()):
            ttk.Button(
                loader_frame,
                text=pattern_name,
                command=lambda p=pattern: self.load_pattern(p)
            ).grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')

    def load_pattern(self, pattern):
        self.access_pattern_var.set(pattern)