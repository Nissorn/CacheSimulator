import tkinter as tk
from tkinter import ttk, messagebox 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import OrderedDict
import numpy as np 
from mock_data_loader import MockDataLoader

class CacheSimulator:
    def __init__(self):
        self.cache = OrderedDict() #track insertion order
        self.hits = 0
        self.misses = 0
        self.cache_size = 0
        self.block_size = 0
        self.associativity = 'Direct'
        self.replacement_policy = 'LRU'

    def reset(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def access_memory(self, address):
        if address in self.cache:
            self.hits += 1
            if self.replacement_policy == 'LRU':
                self.cache.move_to_end(address) #Move to end to mark as recently used
        else:
            self.misses += 1
            if len(self.cache) >= self.cache_size:
                self.cache.popitem(last=False) #Remove the first item (oldest)
            self.cache[address] = True

    def get_hit_rate(self):
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0

class CacheSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Cache Simulator')
        self.root.geometry('800x600')
        self.simulator = CacheSimulator()
        self.setup_gui()

    def setup_gui(self):
        #Main Container for left size
        left_container = ttk.Frame(self.root)
        left_container.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        #input Frame
        input_frame = ttk.LabelFrame(left_container, text='Cache Configureation', padding='5')
        input_frame.pack(fill=tk.X, padx=0, pady=5)

        #Cache Size
        ttk.Label(input_frame, text='Cache Size:').grid(row=0, column=0, padx=5, pady=5)
        self.cache_size_var = tk.StringVar(value='4')
        cache_size_entry = ttk.Entry(input_frame, textvariable=self.cache_size_var)
        cache_size_entry.grid(row=0, column=1, padx=5, pady=5)

        #Block Size
        ttk.Label(input_frame, text='Block Size:').grid(row=1, column=0, padx=5, pady=5)
        self.block_size_var = tk.StringVar(value='16')
        block_size_entry = ttk.Entry(input_frame, textvariable=self.block_size_var)
        block_size_entry.grid(row=1, column=1, padx=5, pady=5)

        #Associativity
        ttk.Label(input_frame, text='Associativity:').grid(row=2, column=0, padx=5, pady=5)
        self.associativity_var = tk.StringVar(value='Direct')
        associativity_combo = ttk.Combobox(input_frame, textvariable=self.associativity_var)
        associativity_combo['values'] = ('Direct', 'Set-Associative', 'Fully-Associative')
        associativity_combo.grid(row=2, column=1, padx=5, pady=5)

        #Replacement Policy
        ttk.Label(input_frame, text='Replacement Policy:').grid(row=3, column=0, padx=5, pady=5)
        self.policy_var = tk.StringVar(value='LRU')
        policy_combo = ttk.Combobox(input_frame, textvariable=self.policy_var)
        policy_combo['values'] = ('LRU', 'FIFO')
        policy_combo.grid(row=3, column=1, padx=5, pady=5)

        #Memory Access Pattern
        ttk.Label(input_frame, text='Access Pattern:').grid(row=4, column=0, padx=5, pady=5)
        self.access_pattern_var = tk.StringVar()
        access_pattern_entry = ttk.Entry(input_frame, textvariable=self.access_pattern_var)
        access_pattern_entry.grid(row=4, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text='Start Simulation', command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Reset', command=self.reset_simulation).pack(side=tk.LEFT, padx=5)

        # Create and add the mock data loader
        self.mock_loader = MockDataLoader(self.root, self.access_pattern_var)
        self.mock_loader.create_loader_ui(left_container)

        # Cache State Frame
        cache_frame = ttk.LabelFrame(self.root, text='Cache State', padding='5')
        cache_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        self.cache_text = tk.Text(cache_frame, width=30, height=10)
        self.cache_text.pack(padx=5, pady=5)

        # Statistics Frame
        stats_frame = ttk.LabelFrame(self.root, text='Statistics', padding='5')
        stats_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=stats_frame)
        self.canvas.get_tk_widget().pack()

    def update_cache_display(self):
        self.cache_text.delete('1.0', tk.END)
        for addr in self.simulator.cache:
            self.cache_text.insert(tk.END, f'Block {addr}\n')

    def update_statistics(self):
        self.ax.clear()
        stats = [self.simulator.hits, self.simulator.misses]
        labels = ['Hits', 'Misses']
        self.ax.bar(labels, stats)
        self.ax.set_title('Cache Performance')
        self.canvas.draw()

    def start_simulation(self):
        try:
            self.simulator.cache_size = int(self.cache_size_var.get())
            self.simulator.block_size = int(self.block_size_var.get())
            self.simulator.associativity = self.associativity_var.get()
            self.simulator.replacement_policy = self.policy_var.get()

            access_pattern = self.access_pattern_var.get().split()
            for addr in access_pattern:
                self.simulator.access_memory(int(addr))
                self.update_cache_display()
            self.update_statistics()

        except ValueError as e:
            tk.messagebox.showerror('Error', 'Please enter valid numeric values')

    def reset_simulation(self):
        self.simulator.reset()
        self.update_cache_display()
        self.update_statistics()


if __name__ == "__main__":
    root = tk.Tk()
    app = CacheSimulatorGUI(root)
    root.mainloop()