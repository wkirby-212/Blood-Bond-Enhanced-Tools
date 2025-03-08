import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path
import logging
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
import datetime
import uuid

# For more modern and visually appealing UI
try:
    import customtkinter as ctk
    USE_CTK = True
except ImportError:
    USE_CTK = False
    print("customtkinter not found, falling back to standard tkinter")

class SpellTomeWindow:
    
    def __init__(self, parent, data_loader=None, use_ctk=None):
        """
        Initialize the SpellTomeWindow.
        
        Args:
            parent: The parent widget (window or frame)
            data_loader: The DataLoader instance for accessing spell data
            use_ctk: Override the global USE_CTK setting. If None, uses the global setting.
        """
        # Override USE_CTK if specified
        global USE_CTK
        if use_ctk is not None:
            USE_CTK = use_ctk
            
        self.parent = parent
        self.data_loader = data_loader
        self.logger = logging.getLogger(__name__)
        
        # Set up the spell history file path
        self.history_dir = Path.home() / ".bloodbond"
        self.history_file = self.history_dir / "spell_history.json"
        
        # Ensure the directory exists
        self.history_dir.mkdir(exist_ok=True)
        
        # Initialize the UI variables
        self.setup_variables()
        
        # Set up the UI elements
        self.setup_ui()
        
        # Load existing spells
        self.load_spells()
        
        # After widgets are created, update layout to ensure proper sizing
        # Execute update_layout once to set initial layout
        self.parent.after(100, self.update_layout)
        
        # Bind to Configure events to handle window resizing, but only trigger when resizing ends
        self.parent.bind("<Configure>", self.on_configure)
        
        self.setup_filters()
        
        # Update the display with loaded spells
        self.update_display()
    def setup_variables(self):
        """Set up the variables used in the UI."""
        # Variables for storing spell data
        self.spells = []
        self.filtered_spells = []
        
        # Selected spell
        self.selected_spell = None
        
        # Filter variables
        var_class = ctk.StringVar if USE_CTK else tk.StringVar
        
        self.filter_effect_var = var_class(value="All")
        self.filter_element_var = var_class(value="All")
        self.filter_level_var = var_class(value="All")
        self.search_var = var_class(value="")
        
        # Get effect and element lists from data_loader if available
        self.effects = ["All"]
        self.elements = ["All"]
        self.levels = ["All", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        
        if self.data_loader:
            try:
                self.effects.extend(self.data_loader.get_spell_effects())
                self.elements.extend(self.data_loader.get_spell_elements())
            except Exception as e:
                self.logger.error(f"Error loading spell effects and elements: {e}")
    
    def setup_ui(self):
        """Set up the UI elements for the spell history tab."""
        # Determine the appropriate widget classes based on USE_CTK
        frame_class = ctk.CTkFrame if USE_CTK else ttk.Frame
        label_class = ctk.CTkLabel if USE_CTK else ttk.Label
        button_class = ctk.CTkButton if USE_CTK else ttk.Button
        entry_class = ctk.CTkEntry if USE_CTK else ttk.Entry
        combobox_class = ctk.CTkComboBox if USE_CTK else ttk.Combobox
        
        # Main container frame
        self.main_frame = frame_class(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a two-panel layout with equal width (50/50 split)
        self.panels_frame = frame_class(self.main_frame)
        self.panels_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure panels_frame to use grid for better control
        self.panels_frame.grid_columnconfigure(0, weight=1)
        self.panels_frame.grid_columnconfigure(1, weight=1)
        self.panels_frame.grid_rowconfigure(0, weight=1)
        
        # Set up panels using grid to maintain exact 50/50 split
        self.left_panel = frame_class(self.panels_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.left_panel.grid_propagate(False)  # Prevent auto-resize
        
        self.right_panel = frame_class(self.panels_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.right_panel.grid_propagate(False)  # Prevent auto-resize
        
        # Set up the left panel with search, filters, and tree view
        self.setup_left_panel(label_class, entry_class, combobox_class, button_class)
        
        # Set up the right panel with spell details and action buttons
        self.setup_right_panel(label_class, button_class)
    
    def setup_left_panel(self, label_class, entry_class, combobox_class, button_class):
        """Set up the left panel with search, filters, and tree view."""
        # Create a master frame to hold everything in the left panel with proper order
        master_frame = ttk.Frame(self.left_panel)
        master_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for search and filters at the top
        top_controls_frame = ttk.Frame(master_frame)
        top_controls_frame.pack(fill=tk.X, pady=(0, 10), side=tk.TOP)
        
        # Search frame first for better UI flow
        search_frame = ttk.Frame(top_controls_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5), side=tk.TOP)
        
        # Filter frame below search
        filter_frame = ttk.Frame(top_controls_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5), side=tk.TOP)
        
        # Configure search components
        search_label = label_class(search_frame, text="")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        search_entry = entry_class(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_button = button_class(search_frame, text="Search", command=self.apply_filters)
        search_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Bind the Enter key to the search function
        search_entry.bind("<Return>", lambda event: self.apply_filters())
        
        # Configure filter components
        filter_label_frame = ttk.LabelFrame(filter_frame, text="")
        filter_label_frame.pack(fill=tk.X, expand=True)
        
        filter_inner_frame = ttk.Frame(filter_label_frame)
        filter_inner_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Effect filter
        effect_label = label_class(filter_inner_frame, text="Effect:")
        effect_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        
        # Set up the variable based on the widget type
        if USE_CTK:
            effect_combo = combobox_class(filter_inner_frame, values=self.effects, 
                                    variable=self.filter_effect_var)
        else:
            effect_combo = combobox_class(filter_inner_frame, values=self.effects, 
                                    textvariable=self.filter_effect_var)
        effect_combo.grid(row=0, column=1, sticky="ew", pady=2)
        
        # Element filter
        element_label = label_class(filter_inner_frame, text="Element:")
        element_label.grid(row=0, column=2, sticky="w", padx=(10, 5), pady=2)
        
        # Set up the variable based on the widget type
        if USE_CTK:
            element_combo = combobox_class(filter_inner_frame, values=self.elements, 
                                     variable=self.filter_element_var)
        else:
            element_combo = combobox_class(filter_inner_frame, values=self.elements, 
                                     textvariable=self.filter_element_var)
        element_combo.grid(row=0, column=3, sticky="ew", pady=2)
        
        # Level filter
        level_label = label_class(filter_inner_frame, text="Level:")
        level_label.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
        
        # Set up the variable based on the widget type
        if USE_CTK:
            level_combo = combobox_class(filter_inner_frame, values=self.levels, 
                                   variable=self.filter_level_var)
        else:
            level_combo = combobox_class(filter_inner_frame, values=self.levels, 
                                   textvariable=self.filter_level_var)
        level_combo.grid(row=1, column=1, sticky="ew", pady=2)
        
        # Apply filter button
        apply_button = button_class(filter_inner_frame, text="Apply Filters", 
                                  command=self.apply_filters)
        apply_button.grid(row=1, column=2, columnspan=2, sticky="ew", pady=2, padx=(10, 0))
        
        # Configure grid weights
        filter_inner_frame.columnconfigure(1, weight=1)
        filter_inner_frame.columnconfigure(3, weight=1)
        
        # Add Treeview for displaying spells
        self.setup_treeview()
    def setup_treeview(self):
        """Set up the ttk.Treeview widget for displaying spells."""
        # Create a frame for the treeview with a scrollbar - make it fill the available space
        tree_frame = ttk.Frame(self.left_panel)
        tree_frame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
        tree_frame.pack_propagate(False)  # Prevent the frame from shrinking to fit contents
        
        # Set a minimum height for the treeview frame to ensure visibility
        self.left_panel.update_idletasks()
        panel_height = self.left_panel.winfo_height()
        if panel_height <= 1:  # If height is not yet determined, use a reasonable default
            panel_height = 400
        # Reserve space for search and filters (approximately 100-120 pixels)
        tree_frame.config(height=panel_height - 120)
        
        columns = ("name", "effect", "element", "level", "date")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Define column headings
        
        # Define column headings
        self.tree.heading("name", text="Name", command=lambda: self.sort_treeview("name"))
        self.tree.heading("effect", text="Effect", command=lambda: self.sort_treeview("effect"))
        self.tree.heading("element", text="Element", command=lambda: self.sort_treeview("element"))
        self.tree.heading("level", text="Level", command=lambda: self.sort_treeview("level", numeric=True))
        self.tree.heading("date", text="Date Added", command=lambda: self.sort_treeview("date"))
        
        # Define column widths
        self.tree.column("name", width=150, minwidth=100)
        self.tree.column("effect", width=100, minwidth=80)
        self.tree.column("element", width=100, minwidth=80)
        self.tree.column("level", width=50, minwidth=40)
        self.tree.column("date", width=150, minwidth=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and treeview
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_spell_select)
    def setup_top_buttons(self, button_class):
        """Set up the top buttons for refreshing and clearing the spell list."""
        # Refresh spell list button - make it smaller and more compact
        self.refresh_button = button_class(self.top_buttons_frame, text="Refresh", 
                                      command=self.apply_filters)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Unlock checkbox for clear button
        checkbox_class = ctk.CTkCheckBox if USE_CTK else ttk.Checkbutton
        self.unlock_var = ctk.StringVar() if USE_CTK else tk.BooleanVar()
        self.unlock_var.set(False)
        
        # Put checkbox directly next to Refresh button
        if USE_CTK:
            self.unlock_checkbox = checkbox_class(self.top_buttons_frame, text="Unlock", 
                                            variable=self.unlock_var, onvalue="on", offvalue="off",
                                            command=self.toggle_clear_button)
        else:
            self.unlock_checkbox = checkbox_class(self.top_buttons_frame, text="Unlock", 
                                            variable=self.unlock_var,
                                            command=self.toggle_clear_button)
        self.unlock_checkbox.pack(side=tk.LEFT, padx=(5, 5))
        
        # Clear button - directly next to checkbox
        self.clear_button = button_class(self.top_buttons_frame, text="Clear", 
                                    command=self.clear_all_spells, state="disabled")
        self.clear_button.pack(side=tk.LEFT)
    def setup_right_panel(self, label_class, button_class):
        """Set up the right panel with spell details and action buttons."""
        # Spell details frame
        details_frame = ttk.LabelFrame(self.right_panel, text="")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), padx=5)
        details_frame.pack_propagate(False)  # Prevent the frame from shrinking to fit contents
        
        # Set a minimum height for the details frame
        self.right_panel.update_idletasks()
        panel_height = self.right_panel.winfo_height()
        if panel_height <= 1:  # If height is not yet determined, use a reasonable default
            panel_height = 400
        # Reserve space for buttons at the bottom (approximately 80 pixels)
        details_frame.config(height=panel_height - 80)
        
        # Add text widget for displaying spell details - make it fill the available space
        self.details_text = tk.Text(details_frame, wrap=tk.WORD, height=20)  # Set a reasonable height
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.details_text.config(state=tk.DISABLED)
        
        # Action buttons frame
        button_frame = ttk.Frame(self.right_panel)
        button_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Add buttons
        self.add_button = button_class(button_frame, text="Add New Spell", 
                                     command=self.add_new_spell)
        self.add_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.remove_button = button_class(button_frame, text="Remove Spell", 
                                       command=self.remove_selected_spell)
        self.remove_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        # No special styling for the Remove Spell button - use standard button appearance
        
        # Export/Import frame
        export_frame = ttk.Frame(self.right_panel)
        export_frame.pack(fill=tk.X, padx=5)
        
        self.export_button = button_class(export_frame, text="Export Spells", 
                                       command=self.export_spells)
        self.export_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.import_button = button_class(export_frame, text="Import Spells", 
                                       command=self.import_spells)
        self.import_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
    def setup_filters(self):
        """Set up the filter and search functionality."""
        # Set up callbacks for filter changes
        if USE_CTK:
            # For CustomTkinter, bind to the variable trace
            self.filter_effect_var.trace_add("write", lambda *args: self.apply_filters())
            self.filter_element_var.trace_add("write", lambda *args: self.apply_filters())
            self.filter_level_var.trace_add("write", lambda *args: self.apply_filters())
        else:
            # For standard tkinter/ttk
            self.filter_effect_var.trace("w", lambda *args: self.apply_filters())
            self.filter_element_var.trace("w", lambda *args: self.apply_filters())
            self.filter_level_var.trace("w", lambda *args: self.apply_filters())
    
    def load_spells(self):
        """Load spells from the history file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.spells = json.load(f)
                self.logger.info(f"Loaded {len(self.spells)} spells from {self.history_file}")
            else:
                self.spells = []
                self.logger.info("No spell history file found, starting with empty list")
        except Exception as e:
            self.logger.error(f"Error loading spells from {self.history_file}: {e}")
            messagebox.showerror("Error", f"Could not load spell history: {str(e)}")
            self.spells = []
    
    def save_spells(self):
        """Save spells to the history file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.spells, f, indent=2)
            self.logger.info(f"Saved {len(self.spells)} spells to {self.history_file}")
        except Exception as e:
            self.logger.error(f"Error saving spells to {self.history_file}: {e}")
            messagebox.showerror("Error", f"Could not save spell history: {str(e)}")
    
    def update_display(self):
        """Update the treeview display with the filtered spells."""
        # Clear the current display
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered spells to the treeview
        for spell in self.filtered_spells:
            # Format the date for display
            date_str = spell.get("date_added", "Unknown")
            if date_str and date_str != "Unknown":
                try:
                    # Convert ISO format date to more readable format
                    date_obj = datetime.datetime.fromisoformat(date_str)
                    date_str = date_obj.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    pass
            
            # Insert the spell into the treeview
            self.tree.insert("", tk.END, 
                             values=(spell.get("name", "Unknown"),
                                    spell.get("effect", "Unknown"),
                                    spell.get("element", "Unknown"),
                                    spell.get("level", "0"),
                                    date_str),
                             tags=(spell.get("id", "")))
        
        # Clear selection and details display
        self.selected_spell = None
        self.update_detail_display()
    
    def apply_filters(self):
        """Apply filters to the spell list based on current settings."""
        # Get filter values
        effect_filter = self.filter_effect_var.get()
        element_filter = self.filter_element_var.get()
        level_filter = self.filter_level_var.get()
        search_text = self.search_var.get().lower()
        
        # Apply filters
        self.filtered_spells = []
        for spell in self.spells:
            # Check if spell matches filters
            effect_match = effect_filter == "All" or spell.get("effect") == effect_filter
            element_match = element_filter == "All" or spell.get("element") == element_filter
            level_match = level_filter == "All" or str(spell.get("level")) == level_filter
            
            # Check if spell matches search text
            text_match = not search_text or any(
                search_text in str(value).lower() 
                for key, value in spell.items() 
                if key in ["name", "effect", "element", "description"]
            )
            
            # If all filters match, add to filtered list
            if effect_match and element_match and level_match and text_match:
                self.filtered_spells.append(spell)
        
        # Update the display with filtered results
        self.update_display()
    
    def sort_treeview(self, column, numeric=False):
        """Sort the treeview by the specified column."""
        # Get all items and their values for the column
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        
        # Sort items
        reverse = False
        if hasattr(self, '_last_sort') and self._last_sort == (column, False):
            # If we sorted by this column already, reverse the order
            reverse = True
            self._last_sort = (column, True)
        else:
            self._last_sort = (column, False)
        
        # Perform the sorting
        if numeric:
            # Handle non-numeric values gracefully
            def get_numeric_value(item):
                try:
                    return float(item[0])
                except ValueError:
                    return 0
            items.sort(key=get_numeric_value, reverse=reverse)
        else:
            # Standard lexicographical sorting
            items.sort(reverse=reverse)
        
        # Rearrange items in the sorted positions
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
    
    def on_spell_select(self, event):
        """Handle spell selection in the treeview."""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get the selected item's values
        item = selection[0]
        
        # Find the corresponding spell in our filtered list
        values = self.tree.item(item)['values']
        spell_name = values[0]
        
        for spell in self.filtered_spells:
            if spell.get("name") == spell_name:
                self.selected_spell = spell
                self.update_detail_display()
                break
    
    def update_detail_display(self):
        """Update the detail display with the selected spell's information."""
        # Enable editing to update the text
        self.details_text.config(state=tk.NORMAL)
        
        # Clear current content
        self.details_text.delete(1.0, tk.END)
        
        if self.selected_spell:
            # Format the spell details
            details = [
                f"Name: {self.selected_spell.get('name', 'Unknown')}",
                f"Effect: {self.selected_spell.get('effect', 'Unknown')}",
                f"Element: {self.selected_spell.get('element', 'Unknown')}",
                f"Level: {self.selected_spell.get('level', '0')}",
                f"Damage: {self.selected_spell.get('damage', 'N/A')}",
                f"Range: {self.selected_spell.get('range', 'N/A')}",
                f"Duration: {self.selected_spell.get('duration', 'N/A')}",
                f"Mana Cost: {self.selected_spell.get('mana_cost', 'N/A')}",
                f"Date Added: {self.selected_spell.get('date_added', 'Unknown')}",
                "\nDescription:",
                f"{self.selected_spell.get('description', 'No description available.')}",
            ]
            
            # Insert the details
            self.details_text.insert(tk.END, "\n".join(details))
        else:
            self.details_text.insert(tk.END, "Select a spell from the list to view details.")
        
        # Disable editing again
        self.details_text.config(state=tk.DISABLED)
    
    def add_new_spell(self):
        """Add a new spell to the history."""
        try:
            # This would typically open a dialog to create a new spell
            # For simplicity, we'll create a placeholder spell
            new_spell = {
                "id": str(uuid.uuid4()),
                "name": "New Spell",
                "effect": "None",
                "element": "Neutral",
                "level": 1,
                "damage": "1d6",
                "range": "30 ft",
                "duration": "Instantaneous",
                "mana_cost": 5,
                "description": "This is a placeholder for a new spell. Edit it to create your custom spell.",
                "date_added": datetime.datetime.now().isoformat()
            }
            
            # In a real implementation, you would show a form to edit these values
            
            # Add the new spell to the list
            self.spells.append(new_spell)
            
            # Save the updated list
            self.save_spells()
            
            # Update filters and display
            self.apply_filters()
            
            messagebox.showinfo("Success", "New spell added successfully!")
        except Exception as e:
            self.logger.error(f"Error adding new spell: {e}")
            messagebox.showerror("Error", f"Could not add new spell: {str(e)}")
    
    def remove_selected_spell(self):
        """Remove the currently selected spell from the history."""
        if not self.selected_spell:
            messagebox.showinfo("No Selection", "Please select a spell to remove.")
            return
        
        try:
            # Confirm with the user
            if not messagebox.askyesno("Confirm", f"Are you sure you want to remove the spell '{self.selected_spell.get('name')}'?"):
                return
            
            # Get the spell ID to remove
            spell_id = self.selected_spell.get("id")
            
            # Find and remove the spell from the list
            self.spells = [spell for spell in self.spells if spell.get("id") != spell_id]
            
            # Save the updated list
            self.save_spells()
            
            # Update filters and display
            self.apply_filters()
            
            messagebox.showinfo("Success", "Spell removed successfully!")
        except Exception as e:
            self.logger.error(f"Error removing spell: {e}")
            messagebox.showerror("Error", f"Could not remove spell: {str(e)}")
    
    def export_spells(self):
        """Export spells to a JSON file."""
        try:
            from tkinter import filedialog
            
            # Ask for the save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Spells"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Write the spells to the file
            with open(file_path, 'w') as f:
                json.dump(self.spells, f, indent=2)
            
            self.logger.info(f"Exported {len(self.spells)} spells to {file_path}")
            messagebox.showinfo("Success", f"Successfully exported {len(self.spells)} spells!")
        
        except Exception as e:
            self.logger.error(f"Error exporting spells: {e}")
            messagebox.showerror("Error", f"Could not export spells: {str(e)}")
    
    def import_spells(self):
        """Import spells from a JSON file."""
        try:
            from tkinter import filedialog
            
            # Ask for the file to import
            file_path = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Import Spells"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Read the spells from the file
            with open(file_path, 'r') as f:
                imported_spells = json.load(f)
            
            # Validate the imported data
            if not isinstance(imported_spells, list):
                raise ValueError("Invalid format: Expected a list of spells")
            
            # Confirm with the user
            action = messagebox.askyesnocancel(
                "Import Options", 
                f"Found {len(imported_spells)} spells to import. Would you like to:\n\n"
                "Yes: Add to existing spells\n"
                "No: Replace existing spells\n"
                "Cancel: Abort import"
            )
            
            if action is None:  # User cancelled
                return
            
            if action:  # User chose to add
                # Add unique IDs to imported spells if missing
                for spell in imported_spells:
                    if "id" not in spell:
                        spell["id"] = str(uuid.uuid4())
                
                # Add imported spells to existing spells
                self.spells.extend(imported_spells)
            else:  # User chose to replace
                self.spells = imported_spells
            
            # Save the updated list
            self.save_spells()
            
            # Update filters and display
            self.apply_filters()
            
            self.logger.info(f"Imported {len(imported_spells)} spells from {file_path}")
            messagebox.showinfo("Success", f"Successfully imported {len(imported_spells)} spells!")
        
        except Exception as e:
            self.logger.error(f"Error importing spells: {e}")
            messagebox.showerror("Error", f"Could not import spells: {str(e)}")
    
    def clear_all_spells(self):
        """Clear all spells from the history."""
        try:
            # Confirm with the user
            if not messagebox.askyesno("Confirm", "Are you sure you want to remove ALL spells? This cannot be undone!"):
                return
            
            # Clear the spell list
            self.spells = []
            
            # Save the updated (empty) list
            self.save_spells()
            
            # Update filters and display
            self.apply_filters()
            
            messagebox.showinfo("Success", "All spells have been removed!")
        except Exception as e:
            self.logger.error(f"Error clearing spells: {e}")
            messagebox.showerror("Error", f"Could not clear spells: {str(e)}")
    
    def save_on_exit(self):
        """Save spells when the application closes."""
        try:
            self.save_spells()
        except Exception as e:
            self.logger.error(f"Error saving spells on exit: {e}")
    def add_spell(self, spell):
        """
        Add a spell to the history.
        
        Args:
            spell: A dictionary containing the spell data
        """
        try:
            # Ensure the spell has an ID
            if "id" not in spell:
                spell["id"] = str(uuid.uuid4())
            
            # Ensure the spell has a date_added field
            if "date_added" not in spell:
                spell["date_added"] = datetime.datetime.now().isoformat()
            
            # Add the spell to the list
            self.spells.append(spell)
            
            # Save the updated list
            self.save_spells()
            
            # Update filters and display
            self.apply_filters()
            
            self.logger.info(f"Spell '{spell.get('name', 'Unknown')}' added to history")
        except Exception as e:
            self.logger.error(f"Error adding spell to history: {e}")
            messagebox.showerror("Error", f"Could not add spell to history: {str(e)}")
    def toggle_clear_button(self):
        """Enable or disable the clear button based on the unlock checkbox."""
        if USE_CTK:
            if self.unlock_var.get() == "on":
                self.clear_button.config(state="normal")
            else:
                self.clear_button.config(state="disabled")
        else:
            if self.unlock_var.get() == 1:  # Standard Tkinter uses 1/0 instead of "on"/"off"
                self.clear_button.config(state="normal")
            else:
                self.clear_button.config(state="disabled")
    def update_layout(self):
        """Update the layout of the UI elements after they are created.
        This helps ensure proper sizing and positioning of all elements."""
        try:
            # Update the panel sizes
            self.panels_frame.update_idletasks()
            width = self.main_frame.winfo_width()
            height = self.main_frame.winfo_height()
            
            if width > 1 and height > 1:  # Only if we have valid dimensions
                # Set sizes for left and right panels
                panel_width = width // 2
                self.left_panel.config(width=panel_width, height=height)
                self.right_panel.config(width=panel_width, height=height)
                
                # Update the treeview and details frame sizes
                tree_frame = self.tree.master
                if tree_frame:
                    tree_frame.config(height=height - 120)
                
                # Force panels to maintain their 50/50 split
                self.panels_frame.grid_columnconfigure(0, minsize=panel_width)
                self.panels_frame.grid_columnconfigure(1, minsize=panel_width)
                
                # No longer scheduling continuous updates
        except Exception as e:
            self.logger.error(f"Error updating layout: {e}")

    def on_configure(self, event):
        """Handle window resize events with a delay to avoid continuous updates."""
        # Cancel any existing scheduled update
        if hasattr(self, '_resize_timer') and self._resize_timer:
            self.parent.after_cancel(self._resize_timer)
        
        # Schedule a single update after resize is complete (300ms delay)
        self._resize_timer = self.parent.after(300, self.update_layout)
