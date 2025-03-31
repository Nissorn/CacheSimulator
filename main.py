import tkinter as tk
from tkinter import ttk, messagebox 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import OrderedDict
import numpy as np 
from mock_data_loader import MockDataLoader
from ai_optimizer import AIOptimizer
from api_key_manager import APIKeyManager

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
        # Calculate block address
        block_address = address // self.block_size
        
        # Handle different associativity types
        if self.associativity == 'Direct':
            # Direct mapping: one fixed location for each block
            cache_line = block_address % self.cache_size
            if cache_line in self.cache and self.cache[cache_line]['block'] == block_address:
                self.hits += 1
                if self.replacement_policy == 'LRU':
                    self.cache.move_to_end(cache_line)
            else:
                self.misses += 1
                if len(self.cache) >= self.cache_size:
                    self.cache.popitem(last=False)
                self.cache[cache_line] = {'block': block_address, 'data': True}
                
        elif self.associativity == 'Set-Associative':
            # Set-associative: multiple blocks per set
            set_size = 2  # 2-way set associative
            set_index = block_address % (self.cache_size // set_size)
            set_found = False
            
            # Check if block exists in the set
            for cache_line in list(self.cache.keys()):
                if cache_line // (self.cache_size // set_size) == set_index:
                    if self.cache[cache_line]['block'] == block_address:
                        self.hits += 1
                        if self.replacement_policy == 'LRU':
                            self.cache.move_to_end(cache_line)
                        set_found = True
                        break
            
            if not set_found:
                self.misses += 1
                # Find or create space in the set
                set_lines = [line for line in self.cache.keys() 
                           if line // (self.cache_size // set_size) == set_index]
                if len(set_lines) >= set_size:
                    self.cache.pop(set_lines[0])
                new_line = set_index * set_size + (len(set_lines) % set_size)
                self.cache[new_line] = {'block': block_address, 'data': True}
                
        else:  # Fully-Associative
            # Can place block anywhere in cache
            block_found = False
            for cache_line, entry in self.cache.items():
                if entry['block'] == block_address:
                    self.hits += 1
                    if self.replacement_policy == 'LRU':
                        self.cache.move_to_end(cache_line)
                    block_found = True
                    break
                    
            if not block_found:
                self.misses += 1
                if len(self.cache) >= self.cache_size:
                    self.cache.popitem(last=False)
                # Use the block address as the cache line for simplicity
                self.cache[len(self.cache)] = {'block': block_address, 'data': True}

    def get_hit_rate(self):
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0

class CacheSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Cache Simulator')
        self.root.geometry('1000x700')  # Increased window size for better layout
        self.root.minsize(800, 600)     # Set minimum window size
        self.simulator = CacheSimulator()
        
        # Initialize AI components
        self.ai_optimizer = AIOptimizer()
        self.api_key_manager = APIKeyManager(root)
        self.ai_optimizer.set_api_key(self.api_key_manager.get_api_key())
        
        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Apply a theme for better appearance
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'))
        style.configure('TNotebook.Tab', font=('Arial', 10))
        
        self.setup_gui()

    def setup_gui(self):
        # Main container with notebook for tabbed interface
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=3)  # Configuration tab gets more space
        main_container.rowconfigure(1, weight=2)  # Results tab gets less space
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=0, column=0, sticky='nsew')
        
        # Configuration Tab
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(config_tab, text='Configuration')
        config_tab.columnconfigure(0, weight=1)
        config_tab.columnconfigure(1, weight=1)
        
        # Cache Configuration Frame (left side of config tab)
        config_frame = ttk.LabelFrame(config_tab, text='Cache Configuration', padding='10')
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # Cache Size with spinbox instead of entry for better UX
        ttk.Label(config_frame, text='Cache Size:').grid(row=0, column=0, padx=5, pady=8, sticky='w')
        self.cache_size_var = tk.StringVar(value='4')
        cache_size_spinbox = ttk.Spinbox(config_frame, from_=1, to=100, textvariable=self.cache_size_var, width=10)
        cache_size_spinbox.grid(row=0, column=1, padx=5, pady=8, sticky='w')
        
        # Block Size with spinbox
        ttk.Label(config_frame, text='Block Size:').grid(row=1, column=0, padx=5, pady=8, sticky='w')
        self.block_size_var = tk.StringVar(value='16')
        block_size_spinbox = ttk.Spinbox(config_frame, from_=1, to=1024, textvariable=self.block_size_var, width=10)
        block_size_spinbox.grid(row=1, column=1, padx=5, pady=8, sticky='w')
        
        # Associativity with improved dropdown
        ttk.Label(config_frame, text='Associativity:').grid(row=2, column=0, padx=5, pady=8, sticky='w')
        self.associativity_var = tk.StringVar(value='Direct')
        associativity_combo = ttk.Combobox(config_frame, textvariable=self.associativity_var, width=15, state='readonly')
        associativity_combo['values'] = ('Direct', 'Set-Associative', 'Fully-Associative')
        associativity_combo.grid(row=2, column=1, padx=5, pady=8, sticky='w')
        
        # Replacement Policy with improved dropdown
        ttk.Label(config_frame, text='Replacement Policy:').grid(row=3, column=0, padx=5, pady=8, sticky='w')
        self.policy_var = tk.StringVar(value='LRU')
        policy_combo = ttk.Combobox(config_frame, textvariable=self.policy_var, width=15, state='readonly')
        policy_combo['values'] = ('LRU', 'FIFO')
        policy_combo.grid(row=3, column=1, padx=5, pady=8, sticky='w')
        
        # Memory Access Pattern Frame (right side of config tab)
        pattern_frame = ttk.LabelFrame(config_tab, text='Memory Access Pattern', padding='10')
        pattern_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        # Access Pattern with better layout
        ttk.Label(pattern_frame, text='Access Pattern:').grid(row=0, column=0, padx=5, pady=8, sticky='w')
        self.access_pattern_var = tk.StringVar()
        access_pattern_entry = ttk.Entry(pattern_frame, textvariable=self.access_pattern_var, width=30)
        access_pattern_entry.grid(row=0, column=0, columnspan=2, padx=5, pady=8, sticky='ew')
        
        # Help text for access pattern
        help_text = ttk.Label(pattern_frame, text='Enter space-separated memory addresses (e.g., "0 1 2 3")', 
                             font=('Arial', 9, 'italic'), foreground='gray')
        help_text.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky='w')
        
        # Create and add the mock data loader with better layout
        self.mock_loader = MockDataLoader(self.root, self.access_pattern_var)
        mock_frame = ttk.LabelFrame(pattern_frame, text='Predefined Patterns', padding='5')
        mock_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky='ew')
        
        # Custom implementation of mock data loader UI for better layout
        patterns = self.mock_loader.patterns
        for i, (pattern_name, pattern) in enumerate(patterns.items()):
            row, col = i // 2, i % 2
            ttk.Button(
                mock_frame,
                text=pattern_name,
                command=lambda p=pattern: self.mock_loader.load_pattern(p),
                width=12
            ).grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Control buttons with better styling
        control_frame = ttk.Frame(main_container)
        control_frame.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        control_frame.columnconfigure(0, weight=1)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, pady=10)
        
        start_button = ttk.Button(button_frame, text='Start Simulation', command=self.start_simulation, width=20)
        start_button.pack(side=tk.LEFT, padx=10)
        
        reset_button = ttk.Button(button_frame, text='Reset', command=self.reset_simulation, width=15)
        reset_button.pack(side=tk.LEFT, padx=10)
        
        # AI Optimization button
        ai_button = ttk.Button(button_frame, text='Auto Customize Cache with AI', command=self.optimize_with_ai, width=25)
        ai_button.pack(side=tk.LEFT, padx=10)
        
        # API Key configuration button
        api_key_button = ttk.Button(button_frame, text='Set API Key', command=self.configure_api_key, width=15)
        api_key_button.pack(side=tk.LEFT, padx=10)
        
        # Results Tab
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text='Results')
        results_tab.columnconfigure(0, weight=1)
        results_tab.columnconfigure(1, weight=1)
        results_tab.rowconfigure(0, weight=1)
        
        # Cache State Frame with improved visualization
        cache_frame = ttk.LabelFrame(results_tab, text='Cache State', padding='10')
        cache_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # Scrollable cache display with better formatting
        cache_scroll = ttk.Scrollbar(cache_frame)
        cache_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cache_text = tk.Text(cache_frame, width=30, height=15, yscrollcommand=cache_scroll.set)
        self.cache_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        cache_scroll.config(command=self.cache_text.yview)
        
        # Statistics Frame with improved visualization
        stats_frame = ttk.LabelFrame(results_tab, text='Cache Performance', padding='10')
        stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        # Create figure for statistics with better styling
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=stats_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize statistics display
        self.update_statistics()

    def update_cache_display(self):
        self.cache_text.delete('1.0', tk.END)
        self.cache_text.tag_configure('header', font=('Arial', 10, 'bold'))
        self.cache_text.tag_configure('address', foreground='blue')
        
        if not self.simulator.cache:
            self.cache_text.insert(tk.END, "Cache is empty. Run a simulation to see results.\n", 'header')
            return
            
        self.cache_text.insert(tk.END, f"Cache contains {len(self.simulator.cache)} blocks\n\n", 'header')
        
        for i, addr in enumerate(self.simulator.cache):
            self.cache_text.insert(tk.END, f"Block {i}: ", 'header')
            self.cache_text.insert(tk.END, f"Address {addr}\n", 'address')

    def update_statistics(self):
        self.ax.clear()
        
        # Get statistics
        hits = self.simulator.hits
        misses = self.simulator.misses
        total = hits + misses
        hit_rate = self.simulator.get_hit_rate() * 100 if total > 0 else 0
        
        # Create bar chart with better styling
        stats = [hits, misses]
        labels = ['Hits', 'Misses']
        colors = ['#4CAF50', '#F44336']  # Green for hits, red for misses
        
        bars = self.ax.bar(labels, stats, color=colors)
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height}', ha='center', va='bottom')
        
        # Add hit rate as text
        if total > 0:
            self.ax.text(0.5, 0.9, f'Hit Rate: {hit_rate:.1f}%', 
                        horizontalalignment='center',
                        transform=self.ax.transAxes,
                        bbox=dict(facecolor='#E0E0E0', alpha=0.5))
        
        # Improve chart appearance
        self.ax.set_title('Cache Performance')
        self.ax.set_ylabel('Count')
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Update canvas
        self.fig.tight_layout()
        self.canvas.draw()

    def start_simulation(self):
        try:
            # Validate inputs
            cache_size = int(self.cache_size_var.get())
            block_size = int(self.block_size_var.get())
            
            if cache_size <= 0 or block_size <= 0:
                raise ValueError("Cache size and block size must be positive integers")
                
            # Get access pattern
            access_pattern = self.access_pattern_var.get().strip()
            if not access_pattern:
                tk.messagebox.showwarning('Warning', 'Please enter a memory access pattern or select a predefined pattern')
                return
                
            # Reset simulator
            self.simulator.reset()
            
            # Configure simulator
            self.simulator.cache_size = cache_size
            self.simulator.block_size = block_size
            self.simulator.associativity = self.associativity_var.get()
            self.simulator.replacement_policy = self.policy_var.get()

            # Run simulation
            addresses = access_pattern.split()
            for addr in addresses:
                self.simulator.access_memory(int(addr))
            
            # Update UI
            self.update_cache_display()
            self.update_statistics()
            
            # Switch to results tab
            self.notebook.select(1)  # Select the Results tab

        except ValueError as e:
            tk.messagebox.showerror('Error', 'Please enter valid numeric values for cache size, block size, and memory addresses')

    def reset_simulation(self):
        # Reset simulator
        self.simulator.reset()
        
        # Clear access pattern
        self.access_pattern_var.set('')
        
        # Update UI
        self.update_cache_display()
        self.update_statistics()
        
        # Show a confirmation message
        tk.messagebox.showinfo('Reset', 'Simulation has been reset successfully')
    
    def configure_api_key(self):
        """Open the API key configuration dialog"""
        api_key = self.api_key_manager.show_api_key_dialog()
        if api_key:
            self.ai_optimizer.set_api_key(api_key)
    
    def optimize_with_ai(self):
        """Use AI to optimize cache configuration based on access pattern"""
        # Check if API key is set
        if not self.ai_optimizer.api_key:
            response = messagebox.askyesno(
                'API Key Required', 
                'You need to set your Google AI Studio API key to use this feature. Would you like to set it now?'
            )
            if response:
                self.configure_api_key()
            return
        
        # Get current access pattern
        access_pattern = self.access_pattern_var.get().strip()
        if not access_pattern:
            messagebox.showwarning('Warning', 'Please enter a memory access pattern or select a predefined pattern')
            return
        
        # Get current configuration
        current_config = {
            'cache_size': self.cache_size_var.get(),
            'block_size': self.block_size_var.get(),
            'associativity': self.associativity_var.get(),
            'replacement_policy': self.policy_var.get()
        }
        
        # Show loading message
        loading_window = tk.Toplevel(self.root)
        loading_window.title('Processing')
        loading_window.geometry('300x100')
        loading_window.transient(self.root)
        loading_window.grab_set()
        
        # Center the loading window
        loading_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - loading_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - loading_window.winfo_height()) // 2
        loading_window.geometry(f"+{x}+{y}")
        
        loading_label = ttk.Label(loading_window, text='Analyzing access pattern with AI...\nThis may take a few seconds.', justify='center')
        loading_label.pack(pady=20)
        
        # Update UI to show we're processing
        self.root.update()
        
        # Get recommendation from AI
        recommendation = self.ai_optimizer.get_cache_recommendation(access_pattern, current_config)
        
        # Close loading window
        loading_window.destroy()
        
        # Handle error
        if 'error' in recommendation:
            messagebox.showerror('Error', recommendation['error'])
            return
        
        # Handle raw response (couldn't parse JSON)
        if 'raw_response' in recommendation:
            messagebox.showinfo('AI Response', recommendation['raw_response'])
            return
        
        # Apply recommendation
        try:
            # Update UI with recommendation
            self.cache_size_var.set(str(recommendation['cache_size']))
            self.block_size_var.set(str(recommendation['block_size']))
            self.associativity_var.set(recommendation['associativity'])
            self.policy_var.set(recommendation['replacement_policy'])
            
            # Show success message with details and explanations
            message = f"AI Recommendation Applied:\n\n"
            
            # Add each parameter with its explanation
            if 'explanations' in recommendation:
                message += f"Cache Size: {recommendation['cache_size']}\n"
                message += f"→ Why? {recommendation['explanations'].get('cache_size', '')}\n\n"
                
                message += f"Block Size: {recommendation['block_size']}\n"
                message += f"→ Why? {recommendation['explanations'].get('block_size', '')}\n\n"
                
                message += f"Associativity: {recommendation['associativity']}\n"
                message += f"→ Why? {recommendation['explanations'].get('associativity', '')}\n\n"
                
                message += f"Replacement Policy: {recommendation['replacement_policy']}\n"
                message += f"→ Why? {recommendation['explanations'].get('replacement_policy', '')}\n\n"
            else:
                # Fallback to original format if no explanations
                message += f"Cache Size: {recommendation['cache_size']}\n" \
                          f"Block Size: {recommendation['block_size']}\n" \
                          f"Associativity: {recommendation['associativity']}\n" \
                          f"Replacement Policy: {recommendation['replacement_policy']}\n\n"
            
            message += "Would you like to run the simulation with these settings?"
            
            if messagebox.askyesno('AI Recommendation', message):
                self.start_simulation()
                
        except Exception as e:
            messagebox.showerror('Error', f"Failed to apply recommendation: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CacheSimulatorGUI(root)
    root.mainloop()