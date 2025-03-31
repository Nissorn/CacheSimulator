import tkinter as tk
from tkinter import ttk, messagebox
import os
import json

class APIKeyManager:
    def __init__(self, root):
        self.root = root
        self.api_key = ""
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.load_api_key()
        
    def load_api_key(self):
        """Load API key from config file if it exists"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get("api_key", "")
        except Exception as e:
            print(f"Error loading API key: {e}")
    
    def save_api_key(self, api_key):
        """Save API key to config file"""
        try:
            config = {"api_key": api_key}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            self.api_key = api_key
            return True
        except Exception as e:
            print(f"Error saving API key: {e}")
            return False
    
    def show_api_key_dialog(self):
        """Show dialog to enter API key"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Google AI Studio API Key")
        dialog.geometry("500x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Make dialog modal
        dialog.grab_set()
        
        # Center the dialog on the parent window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Create a frame with padding
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add instructions
        instructions = ttk.Label(frame, text="Enter your Google AI Studio API Key", 
                               font=("Arial", 12, "bold"))
        instructions.pack(pady=(0, 10))
        
        info_text = "You need a Google AI Studio API key to use the AI optimization feature.\n" \
                    "Get your API key from https://aistudio.google.com/"
        info = ttk.Label(frame, text=info_text, wraplength=400)
        info.pack(pady=(0, 10))
        
        # API key entry
        api_key_var = tk.StringVar(value=self.api_key)
        api_key_entry = ttk.Entry(frame, textvariable=api_key_var, width=50)
        api_key_entry.pack(pady=(0, 20), fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        save_button = ttk.Button(
            button_frame, 
            text="Save", 
            command=lambda: self._on_save_api_key(api_key_var.get(), dialog)
        )
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to entry
        api_key_entry.focus_set()
        
        # Wait for the dialog to be closed
        self.root.wait_window(dialog)
        return self.api_key
    
    def _on_save_api_key(self, api_key, dialog):
        """Handle save button click"""
        if not api_key.strip():
            messagebox.showwarning("Warning", "API key cannot be empty")
            return
            
        if self.save_api_key(api_key):
            messagebox.showinfo("Success", "API key saved successfully")
            dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save API key")
    
    def get_api_key(self):
        """Get the current API key"""
        return self.api_key