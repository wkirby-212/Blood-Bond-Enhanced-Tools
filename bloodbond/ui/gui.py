import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import sys
from pathlib import Path

# For more modern and visually appealing UI
try:
    import customtkinter as ctk
    USE_CTK = True
except ImportError:
    USE_CTK = False
    print("customtkinter not found, falling back to standard tkinter")

# Add parent directory to path to enable importing from sibling packages
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from bloodbond.core.data_loader import DataLoader
from bloodbond.core.spell_maker import SpellMaker
from bloodbond.core.element_mapper import ElementMapper
from bloodbond.utils.nl_processor import NLProcessor
from bloodbond.ui.spell_history import SpellTomeWindow
from bloodbond.utils.string_utils import format_spell_name
from bloodbond.core.magic_specialties import (
    NoSpecialty, Chronomage, Graveturgy, Illusionist, Siren, WarMage, Alchemist, NatureShaman
)
from bloodbond.core.exceptions import (
    BloodBondError, DataError, FileNotFoundError, MalformedDataError, InvalidDataError,
    SpellError, InvalidParameterError, IncompatibleElementsError, SpellLimitError, SpellValidationError,
    UIError, InputValidationError, ResourceLoadError, UIConfigurationError
)

class SpellCreatorApp:
    """
    A GUI application for creating and managing spells in the Blood Bond TTRPG system.
    
    This application provides a user-friendly interface for specifying spell parameters
    and viewing the resulting spell incantations and descriptions.
    """
    
    @staticmethod
    def format_duration(duration_key):
        """
        Format a duration key into a user-friendly string.
        
        Args:
            duration_key (str): The original duration key (e.g., "1_minute", "30_minute")
            
        Returns:
            str: A formatted duration string (e.g., "1 Minute", "30 Minutes")
        """
        if not duration_key:
            return ""
            
        # Split the key by underscore
        parts = duration_key.split('_')
        
        if len(parts) < 2:
            return duration_key.capitalize()
            
        # Extract the value and unit
        value_str = parts[0]
        unit = ' '.join(parts[1:])  # Join remaining parts with spaces
        
        try:
            # Try to convert the value to a number
            value = int(value_str)
            
            # Capitalize the unit
            unit = unit.capitalize()
            
            # Add 's' for plural if value > 1
            if value > 1:
                unit += "s"
                
            return f"{value} {unit}"
        except ValueError:
            # If conversion fails, just return with underscores replaced by spaces
            return duration_key.replace('_', ' ').capitalize()
    
    def __init__(self, root=None, use_ctk=None):
        """
        Initialize the SpellCreatorApp.
        
        Args:
            root: The root Tk/CTk window. If None, a new one will be created.
            use_ctk: Override the global USE_CTK setting. If None, uses the global setting.
        """
        # Override USE_CTK if specified
        global USE_CTK
        if use_ctk is not None:
            USE_CTK = use_ctk
            if USE_CTK:
                print("Using customtkinter for enhanced UI")
            else:
                print("Using standard tkinter as requested")
                
        # Initialize data handling components
        self.data_loader = DataLoader()
        self.element_mapper = ElementMapper()
        self.spell_maker = SpellMaker(self.data_loader, self.element_mapper)
        
        # Initialize NLProcessor with path to synonyms.json
        synonyms_path = Path(self.data_loader.data_dir) / "synonyms.json"
        self.nl_processor = NLProcessor(synonyms_path)
        
        # Initialize status variable early to avoid reference errors
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to create spells")
        
        # Load bloodline affinities
        self.bloodline_affinities = self.data_loader.get_bloodline_affinities()
        
        # Store original text from Text-to-Spell tab
        self.original_spell_text = None
        self.use_original_text = True
        
        self.effects = self._get_effect_options()
        self.elements = self._get_element_options()
        self.durations = self._get_duration_options()
        self.ranges = self._get_range_options()
        # Sort bloodlines alphabetically
        self.bloodlines = sorted(self.bloodline_affinities.keys())
        
        # Define magic specialties
        # Define magic specialties
        self.magic_specialties = ["No Specialty", "Chronomage", "Graveturgy", "Illusionist", "Siren", "War Mage", "Alchemist", "Nature Shaman"]
        
        # Map specialty names to their classes
        self.specialty_classes = {
            "No Specialty": NoSpecialty,
            "Chronomage": Chronomage,
            "Graveturgy": Graveturgy,
            "Illusionist": Illusionist,
            "Siren": Siren,
            "War Mage": WarMage,
            "Alchemist": Alchemist,
            "Nature Shaman": NatureShaman
        }
        # Set up CustomTkinter theme
        if USE_CTK:
            ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
            ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Create root window if one wasn't provided
        if root is None:
            if USE_CTK:
                self.root = ctk.CTk()
            else:
                self.root = tk.Tk()
        else:
            self.root = root
            
        # Initialize UI variables
        var_class = ctk.StringVar if USE_CTK else tk.StringVar
        int_var_class = ctk.IntVar if USE_CTK else tk.IntVar
        bool_var_class = ctk.BooleanVar if USE_CTK else tk.BooleanVar
        
        self.tk_vars = {
            "effect": var_class(),
            "element": var_class(),
            "duration": var_class(),
            "range": var_class(),
            "power_level": int_var_class(value=1),
            # Lock variables for random generator
            "lock_effect": bool_var_class(value=False),
            "lock_element": bool_var_class(value=False),
            "lock_duration": bool_var_class(value=False),
            "lock_range": bool_var_class(value=False),
            "lock_range": bool_var_class(value=False),
            "bloodline": var_class(),
            "magic_specialty": var_class(),
        }
        self.root.title("Blood Bond Spell Creator")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        self._setup_ui()
        
        # Initialize the spell history panel
        self.open_spell_history()
    
    def _get_effect_options(self):
        """Get list of available spell effects."""
        try:
            effects = []
            spell_data = self.data_loader.get_spell_data()
            spoken_spell_table = spell_data["spoken_spell_table"]
            effect_prefixes = spoken_spell_table.get("effect_prefix", {})
            
            # Sort effects by name for easier navigation
            return sorted(effect_prefixes.keys())
        except Exception as e:
            print(f"Error loading effect options: {e}")
            return []
    
    def _get_element_options(self):
        """Get list of available spell elements."""
        try:
            elements = []
            spell_data = self.data_loader.get_spell_data()
            spoken_spell_table = spell_data["spoken_spell_table"]
            element_prefixes = spoken_spell_table.get("element_prefix", {})
            
            # Sort elements by name for easier navigation
            return sorted(element_prefixes.keys())
        except Exception as e:
            print(f"Error loading element options: {e}")
            return []
    
    def _get_duration_options(self):
        """Get list of available spell durations."""
        try:
            durations = []
            spell_data = self.data_loader.get_spell_data()
            spoken_spell_table = spell_data["spoken_spell_table"]
            duration_modifiers = spoken_spell_table.get("duration_modifier", {})
            
            # Sort durations for easier navigation (sort by numeric value if possible)
            sorted_durations = sorted(duration_modifiers.keys())
            
            # Create a mapping between internal keys and display formats
            self.duration_mapping = {
                key: self.format_duration(key) for key in sorted_durations
            }
            
            # Create the reverse mapping for looking up keys from display values
            self.duration_reverse_mapping = {
                display: key for key, display in self.duration_mapping.items()
            }
            
            # Return the formatted display values
            return [self.duration_mapping[key] for key in sorted_durations]
        except Exception as e:
            print(f"Error loading duration options: {e}")
            self.duration_mapping = {}
            self.duration_reverse_mapping = {}
            return []
    
    def _get_range_options(self):
        """Get list of available spell ranges."""
        try:
            ranges = []
            spell_data = self.data_loader.get_spell_data()
            spoken_spell_table = spell_data["spoken_spell_table"]
            range_suffixes = spoken_spell_table.get("range_suffix", {})
            
            # Sort ranges for easier navigation
            return sorted(range_suffixes.keys())
        except Exception as e:
            print(f"Error loading range options: {e}")
            return []
    
    def _setup_ui(self):
        """Setup the user interface components."""
        frame_class = ctk.CTkFrame if USE_CTK else ttk.Frame
        label_class = ctk.CTkLabel if USE_CTK else ttk.Label
        entry_class = ctk.CTkEntry if USE_CTK else ttk.Entry
        button_class = ctk.CTkButton if USE_CTK else ttk.Button
        combobox_class = ctk.CTkComboBox if USE_CTK else ttk.Combobox
        slider_class = ctk.CTkSlider if USE_CTK else ttk.Scale
        textbox_class = ctk.CTkTextbox if USE_CTK else tk.Text
        
        # Main container frame with padding
        if USE_CTK:
            main_frame = frame_class(self.root, corner_radius=10)
        else:
            main_frame = frame_class(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = label_class(main_frame, text="Blood Bond Spell Creator", 
                                  font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 20))
        title_label.pack(pady=(0, 20))
        main_content_frame = frame_class(main_frame)
        main_content_frame.pack(fill=tk.BOTH, expand=True)
        # Create left panel for spell creator and right panel for spell history
        # Create the main content frame
        main_content_frame = frame_class(main_frame)
        main_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the notebook (tabbed interface) that uses the full width
        notebook_class = ttk.Notebook  # Always use ttk.Notebook as ctk doesn't have a Notebook widget
        self.notebook = notebook_class(main_content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.spell_creator_tab = frame_class(self.notebook)
        self.random_generator_tab = frame_class(self.notebook)
        self.text_to_spell_tab = frame_class(self.notebook)
        self.bloodline_tab = frame_class(self.notebook)
        self.spell_history_tab = frame_class(self.notebook)
        
        # Add tabs to the notebook
        self.notebook.add(self.spell_creator_tab, text="Spell Creator")
        self.notebook.add(self.random_generator_tab, text="Random Generator")
        self.notebook.add(self.text_to_spell_tab, text="Text to Spell")
        self.notebook.add(self.bloodline_tab, text="Bloodline Compatibility")
        self.notebook.add(self.spell_history_tab, text="Spell History")
        # Setup each tab
        self._setup_spell_creator_tab()
        self._setup_random_generator_tab()
        self._setup_text_to_spell_tab()
        self._setup_bloodline_compatibility_tab()
        # Status bar at the bottom
        status_bar = label_class(main_frame, textvariable=self.status_var)
        status_bar.pack(fill=tk.X, pady=(10, 0), anchor=tk.W)
        status_bar = label_class(main_frame, textvariable=self.status_var)
        status_bar.pack(fill=tk.X, pady=(10, 0), anchor=tk.W)
    
    def _setup_spell_creator_tab(self):
        """Setup the Spell Creator tab with the original functionality."""
        frame_class = ctk.CTkFrame if USE_CTK else ttk.Frame
        label_class = ctk.CTkLabel if USE_CTK else ttk.Label
        entry_class = ctk.CTkEntry if USE_CTK else ttk.Entry
        button_class = ctk.CTkButton if USE_CTK else ttk.Button
        combobox_class = ctk.CTkComboBox if USE_CTK else ttk.Combobox
        slider_class = ctk.CTkSlider if USE_CTK else ttk.Scale
        textbox_class = ctk.CTkTextbox if USE_CTK else tk.Text
        
        # Input section frame
        input_frame = frame_class(self.spell_creator_tab)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Two-column layout
        left_column = frame_class(input_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = frame_class(input_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Left column (input parameters)
        # Effect
        effect_label = label_class(left_column, text="Effect:")
        effect_label.pack(anchor=tk.W, pady=(0, 5))
        
        if USE_CTK:
            effect_dropdown = combobox_class(left_column, values=self.effects,
                                         variable=self.tk_vars["effect"])
        else:
            effect_dropdown = combobox_class(left_column, values=self.effects,
                                         textvariable=self.tk_vars["effect"])
        effect_dropdown.pack(fill=tk.X, pady=(0, 10))
        if self.effects:
            self.tk_vars["effect"].set(self.effects[0])
        
        # Bloodline
        bloodline_label = label_class(left_column, text="Bloodline:")
        bloodline_label = label_class(left_column, text="Bloodline:")
        bloodline_label.pack(anchor=tk.W, pady=(0, 5))
        
        if USE_CTK:
            bloodline_dropdown = combobox_class(left_column, values=self.bloodlines,
                                           variable=self.tk_vars["bloodline"])
        else:
            bloodline_dropdown = combobox_class(left_column, values=self.bloodlines,
                                           textvariable=self.tk_vars["bloodline"])
        bloodline_dropdown.pack(fill=tk.X, pady=(0, 10))
        if self.bloodlines:
            self.tk_vars["bloodline"].set(self.bloodlines[0])
        
        # Magic Specialty
        specialty_label = label_class(left_column, text="Magic Specialty:")
        specialty_label.pack(anchor=tk.W, pady=(0, 5))
        
        if USE_CTK:
            specialty_dropdown = combobox_class(left_column, values=self.magic_specialties,
                                         variable=self.tk_vars["magic_specialty"])
        else:
            specialty_dropdown = combobox_class(left_column, values=self.magic_specialties,
                                         textvariable=self.tk_vars["magic_specialty"])
        specialty_dropdown.pack(fill=tk.X, pady=(0, 10))
        if self.magic_specialties:
            self.tk_vars["magic_specialty"].set(self.magic_specialties[0])
        
        # Display compatibility between bloodline and selected element
        self.compatibility_var = ctk.StringVar() if USE_CTK else tk.StringVar()
        # Element
        element_label = label_class(left_column, text="Element:")
        element_label.pack(anchor=tk.W, pady=(0, 5))
        if USE_CTK:
            element_dropdown = combobox_class(left_column, values=self.elements,
                                          variable=self.tk_vars["element"])
        else:
            element_dropdown = combobox_class(left_column, values=self.elements,
                                          textvariable=self.tk_vars["element"])
        element_dropdown.pack(fill=tk.X, pady=(0, 10))
        if self.elements:
            self.tk_vars["element"].set(self.elements[0])
        
        # Duration
        duration_label = label_class(left_column, text="Duration:")
        duration_label.pack(anchor=tk.W, pady=(0, 5))
        
        if USE_CTK:
            duration_dropdown = combobox_class(left_column, values=self.durations,
                                           variable=self.tk_vars["duration"])
        else:
            duration_dropdown = combobox_class(left_column, values=self.durations,
                                           textvariable=self.tk_vars["duration"])
        duration_dropdown.pack(fill=tk.X, pady=(0, 10))
        if self.durations:
            self.tk_vars["duration"].set(self.durations[0])
        
        # Range
        range_label = label_class(left_column, text="Range:")
        range_label.pack(anchor=tk.W, pady=(0, 5))
        
        if USE_CTK:
            range_dropdown = combobox_class(left_column, values=self.ranges,
                                        variable=self.tk_vars["range"])
        else:
            range_dropdown = combobox_class(left_column, values=self.ranges,
                                        textvariable=self.tk_vars["range"])
        range_dropdown.pack(fill=tk.X, pady=(0, 10))
        if self.ranges:
            self.tk_vars["range"].set(self.ranges[0])
        
        # Add command to update compatibility when element or bloodline changes
        if USE_CTK:
            element_dropdown.configure(command=self.update_element_compatibility)
            bloodline_dropdown.configure(command=self.update_element_compatibility)
        else:
            element_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_element_compatibility())
            bloodline_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_element_compatibility())
        
        # Power Level
        power_level_label = label_class(left_column, text="Power Level:")
        power_level_label.pack(anchor=tk.W, pady=(0, 5))
        
        if USE_CTK:
            power_level_slider = slider_class(left_column, from_=1, to=10,
                                            variable=self.tk_vars["power_level"])
            power_level_slider.pack(fill=tk.X, pady=(0, 10))
        else:
            power_level_slider = slider_class(left_column, from_=1, to=10, orient=tk.HORIZONTAL,
                                            variable=self.tk_vars["power_level"])
            power_level_slider.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = frame_class(left_column)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        create_spell_button = button_class(button_frame, text="Create Spell",
                                         command=self.create_spell)
        create_spell_button.pack(side=tk.LEFT, padx=(0, 5))
        
        write_spell_button = button_class(button_frame, text="Write Spell",
                                        command=self.save_spell_to_history)
        write_spell_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_button = button_class(button_frame, text="Clear",
                                  command=self.clear_fields)
        clear_button.pack(side=tk.LEFT)
        # Incantation
        incantation_label = label_class(right_column, text="Incantation:")
        incantation_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.incantation_text = textbox_class(right_column, height=4)
        self.incantation_text.pack(fill=tk.X, pady=(0, 10))
        
        # Description
        description_label = label_class(right_column, text="Description:")
        description_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.description_text = textbox_class(right_column, height=10)
        self.description_text.pack(fill=tk.BOTH, expand=True)

    def _setup_random_generator_tab(self):
        """Setup the Random Generator tab for creating random spells."""
        frame_class = ctk.CTkFrame if USE_CTK else ttk.Frame
        label_class = ctk.CTkLabel if USE_CTK else ttk.Label
        button_class = ctk.CTkButton if USE_CTK else ttk.Button
        textbox_class = ctk.CTkTextbox if USE_CTK else tk.Text
        checkbox_class = ctk.CTkCheckBox if USE_CTK else ttk.Checkbutton

        # Main content frame
        content_frame = frame_class(self.random_generator_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title and description
        title_label = label_class(content_frame, 
                                 text="Random Spell Generator", 
                                 font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10))

        description_text = (
            "This tab allows you to generate random spells with the click of a button. "
            "The system will randomly select effect, element, duration, range, and power level values."
        )
        description_label = label_class(content_frame, text=description_text, wraplength=700)
        description_label.pack(pady=(0, 20))

        # Create two columns for layout
        columns_frame = frame_class(content_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        left_column = frame_class(columns_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_column = frame_class(columns_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Generate button on the left
        generate_button = button_class(
            left_column, 
            text="Generate Random Spell",
            command=self.generate_random_spell
        )
        generate_button.pack(pady=(20, 10), padx=20, fill=tk.X)

        # Lock Current button
        lock_current_button = button_class(
            left_column, 
            text="Lock Current",
            command=self.lock_current_parameters
        )
        lock_current_button.pack(pady=(0, 10), padx=20, fill=tk.X)
        
        # Write Spell button for saving current spell to history
        write_spell_button = button_class(
            left_column, 
            text="Write Spell",
            command=self.save_spell_to_history
        )
        write_spell_button.pack(pady=(0, 20), padx=20, fill=tk.X)

        # Output on the right
        # Incantation
        incantation_label = label_class(right_column, text="Incantation:")
        incantation_label.pack(anchor=tk.W, pady=(0, 5))

        self.random_incantation_text = textbox_class(right_column, height=4)
        self.random_incantation_text.pack(fill=tk.X, pady=(0, 10))

        # Description
        description_label = label_class(right_column, text="Description:")
        description_label.pack(anchor=tk.W, pady=(0, 5))

        self.random_description_text = textbox_class(right_column, height=10)
        self.random_description_text.pack(fill=tk.BOTH, expand=True)

        # Details of the randomly generated spell parameters
        details_frame = frame_class(left_column)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        details_label = label_class(details_frame, text="Generated Spell Details:", font=("Helvetica", 12, "bold"))
        details_label.pack(anchor=tk.W, pady=(0, 10))

        # Parameter locking options
        locks_frame = frame_class(details_frame)
        locks_frame.pack(fill=tk.X, pady=(0, 10))

        lock_label = label_class(locks_frame, text="Lock Parameters:", font=("Helvetica", 10, "bold"))
        lock_label.pack(anchor=tk.W, pady=(0, 5))

        lock_description = label_class(locks_frame, text="Check boxes to keep these parameters fixed when generating random spells", 
                                  wraplength=300, font=("Helvetica", 9, "italic"))
        lock_description.pack(anchor=tk.W, pady=(0, 5))
        
        # Magic Specialty lock
        specialty_lock_frame = frame_class(locks_frame)
        specialty_lock_frame.pack(fill=tk.X, pady=2)
        
        # Add a lock_magic_specialty variable
        self.tk_vars["lock_magic_specialty"] = tk.BooleanVar(value=False)
        specialty_lock = checkbox_class(specialty_lock_frame, text="Magic Specialty", 
                                       variable=self.tk_vars["lock_magic_specialty"])
        specialty_lock.pack(side=tk.LEFT)
        # Effect lock
        effect_lock_frame = frame_class(locks_frame)
        effect_lock_frame.pack(fill=tk.X, pady=2)
        
        effect_lock = checkbox_class(effect_lock_frame, text="Effect", 
                                    variable=self.tk_vars["lock_effect"])
        effect_lock.pack(side=tk.LEFT)

        # Element lock
        element_lock_frame = frame_class(locks_frame)
        element_lock_frame.pack(fill=tk.X, pady=2)
        
        element_lock = checkbox_class(element_lock_frame, text="Element", 
                                     variable=self.tk_vars["lock_element"])
        element_lock.pack(side=tk.LEFT)

        # Duration lock
        duration_lock_frame = frame_class(locks_frame)
        duration_lock_frame.pack(fill=tk.X, pady=2)
        
        duration_lock = checkbox_class(duration_lock_frame, text="Duration", 
                                      variable=self.tk_vars["lock_duration"])
        duration_lock.pack(side=tk.LEFT)

        # Range lock
        range_lock_frame = frame_class(locks_frame)
        range_lock_frame.pack(fill=tk.X, pady=2)
        
        range_lock = checkbox_class(range_lock_frame, text="Range", 
                                   variable=self.tk_vars["lock_range"])
        range_lock.pack(side=tk.LEFT)

        self.spell_details_text = textbox_class(details_frame, height=10)
        self.spell_details_text.pack(fill=tk.BOTH, expand=True)

    def _setup_text_to_spell_tab(self):
        """Setup the Text to Spell tab for natural language processing."""
        frame_class = ctk.CTkFrame if USE_CTK else ttk.Frame
        label_class = ctk.CTkLabel if USE_CTK else ttk.Label
        button_class = ctk.CTkButton if USE_CTK else ttk.Button
        textbox_class = ctk.CTkTextbox if USE_CTK else tk.Text
        entry_class = ctk.CTkEntry if USE_CTK else ttk.Entry

        # Main content frame
        content_frame = frame_class(self.text_to_spell_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title and description
        title_label = label_class(content_frame, 
                                 text="Text to Spell Converter", 
                                 font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10))

        description_text = (
            "Enter a description of the spell you want to create, and the system will "
            "analyze it to extract effect, element, duration, and range parameters. "
            "This feature uses basic keyword matching to identify spell components."
        )
        description_label = label_class(content_frame, text=description_text, wraplength=700)
        description_label.pack(pady=(0, 20))

        # Create two columns for layout
        columns_frame = frame_class(content_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        left_column = frame_class(columns_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_column = frame_class(columns_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Text input area on the left
        input_label = label_class(left_column, text="Enter Spell Description:")
        input_label.pack(anchor=tk.W, pady=(0, 5))

        self.nlp_input_text = textbox_class(left_column, height=10)
        self.nlp_input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Add a hint about what to write
        hint_text = (
            "Example: 'Create a powerful fire spell that lasts for 1 minute "
            "and can be cast at a range of 30 feet.'"
        )
        hint_label = label_class(left_column, text=hint_text, wraplength=300, 
                               font=("Helvetica", 9, "italic"))
        hint_label.pack(anchor=tk.W, pady=(0, 10))

        # Convert button
        convert_button = button_class(
            left_column, 
            text="Convert to Spell",
            command=self.analyze_spell_text
        )
        convert_button.pack(pady=10, padx=20, fill=tk.X)

        # Output fields on the right
        output_label = label_class(right_column, text="Extracted Spell Components:", 
                                 font=("Helvetica", 12, "bold"))
        output_label.pack(anchor=tk.W, pady=(0, 10))

        # Extracted parameters
        params_frame = frame_class(right_column)
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Effect
        effect_label = label_class(params_frame, text="Effect:", width=10)
        effect_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.nlp_effect_var = ctk.StringVar() if USE_CTK else tk.StringVar()
        self.nlp_effect_entry = entry_class(params_frame, textvariable=self.nlp_effect_var, 
                                          state="readonly", width=200)
        self.nlp_effect_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(0, 10))

        # Element
        element_label = label_class(params_frame, text="Element:", width=10)
        element_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.nlp_element_var = ctk.StringVar() if USE_CTK else tk.StringVar()
        self.nlp_element_entry = entry_class(params_frame, textvariable=self.nlp_element_var, 
                                           state="readonly", width=200)
        self.nlp_element_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(0, 10))

        # Duration
        duration_label = label_class(params_frame, text="Duration:", width=10)
        duration_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.nlp_duration_var = ctk.StringVar() if USE_CTK else tk.StringVar()
        self.nlp_duration_entry = entry_class(params_frame, textvariable=self.nlp_duration_var, 
                                            state="readonly", width=200)
        self.nlp_duration_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(0, 10))

        # Range
        range_label = label_class(params_frame, text="Range:", width=10)
        range_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.nlp_range_var = ctk.StringVar() if USE_CTK else tk.StringVar()
        self.nlp_range_entry = entry_class(params_frame, textvariable=self.nlp_range_var, 
                                         state="readonly", width=200)
        self.nlp_range_entry.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=(0, 10))

        # Configure grid column weights
        params_frame.grid_columnconfigure(1, weight=1)

        # Add checkbox for using original text as description
        checkbox_class = ctk.CTkCheckBox if USE_CTK else ttk.Checkbutton
        self.use_original_text_var = ctk.BooleanVar(value=True) if USE_CTK else tk.BooleanVar(value=True)
        
        use_original_text_check = checkbox_class(
            right_column,
            text="Use original text as spell description",
            variable=self.use_original_text_var
        )
        use_original_text_check.pack(pady=(5, 10), anchor=tk.W)
        
        # Add a "Use These Parameters" button
        use_params_button = button_class(
            right_column, 
            text="Use These Parameters",
            command=self.use_nlp_parameters,
            state="disabled"  # Initially disabled until parameters are extracted
        )
        use_params_button.pack(pady=10, padx=20, fill=tk.X)
        self.use_params_button = use_params_button

        # Status label
        self.nlp_status_var = ctk.StringVar() if USE_CTK else tk.StringVar()
        self.nlp_status_var.set("Enter a spell description and click 'Convert to Spell'")
        nlp_status_label = label_class(right_column, textvariable=self.nlp_status_var)
        nlp_status_label.pack(fill=tk.X, pady=(10, 0), anchor=tk.W)

    def _setup_bloodline_compatibility_tab(self):
        """Setup the Bloodline Compatibility tab for viewing element affinities."""
        frame_class = ctk.CTkFrame if USE_CTK else ttk.Frame
        label_class = ctk.CTkLabel if USE_CTK else ttk.Label
        button_class = ctk.CTkButton if USE_CTK else ttk.Button
        combobox_class = ctk.CTkComboBox if USE_CTK else ttk.Combobox

        # Main content frame
        content_frame = frame_class(self.bloodline_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title and description
        title_label = label_class(content_frame, 
                                 text="Bloodline Compatibility Table", 
                                 font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10))

        description_text = (
            "This table shows the compatibility percentage between a bloodline and various elements. "
            "A higher percentage (100% = green) indicates stronger affinity, while "
            "a lower percentage (0% = red) indicates weaker affinity."
        )
        description_label = label_class(content_frame, text=description_text, wraplength=700)
        description_label.pack(pady=(0, 20))

        # Get element data (bloodline affinities already loaded in __init__)
        self.elements = self.data_loader.get_spell_elements()
        
        # Sort bloodlines alphabetically for easier navigation
        bloodlines = sorted(self.bloodline_affinities.keys())
        
        # Bloodline selection
        selection_frame = frame_class(content_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 20))
        
        bloodline_label = label_class(selection_frame, text="Select Bloodline:")
        bloodline_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.bloodline_var = ctk.StringVar() if USE_CTK else tk.StringVar()
        if bloodlines:
            self.bloodline_var.set(bloodlines[0])
        
        if USE_CTK:
            bloodline_dropdown = combobox_class(selection_frame, values=bloodlines,
                                           variable=self.bloodline_var,
                                           command=self.update_compatibility_table)
        else:
            bloodline_dropdown = combobox_class(selection_frame, values=bloodlines,
                                           textvariable=self.bloodline_var)
            # For standard ttk.Combobox, we need to use bind instead of command
            bloodline_dropdown.bind("<<ComboboxSelected>>", 
                                     lambda event: self.update_compatibility_table())
        bloodline_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a frame for the compatibility table
        table_frame = frame_class(content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Table headers (Element, Compatibility %)
        headers_frame = frame_class(table_frame)
        headers_frame.pack(fill=tk.X)
        
        # Create headers
        element_header = label_class(headers_frame, text="Element", width=15, 
                                    font=("Helvetica", 12, "bold"))
        element_header.pack(side=tk.LEFT, padx=5, pady=5)
        
        compatibility_header = label_class(headers_frame, text="Compatibility %", width=15,
                                         font=("Helvetica", 12, "bold"))
        compatibility_header.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create a frame to hold the scrollable table
        self.table_container = frame_class(table_frame)
        self.table_container.pack(fill=tk.BOTH, expand=True)
        
        # Initialize the table with the first bloodline
        if bloodlines:
            self.update_compatibility_table(bloodlines[0])

    def update_compatibility_table(self, bloodline=None):
        """
        Update the compatibility table with data for the selected bloodline.
        
        Args:
            bloodline: Name of the bloodline to display. If None, uses the currently selected one.
        """
        # If no bloodline provided, get the currently selected one
        if bloodline is None:
            bloodline = self.bloodline_var.get()
        
        # Clear the current table
        for widget in self.table_container.winfo_children():
            widget.destroy()
            
        frame_class = ctk.CTkFrame if USE_CTK else ttk.Frame
        label_class = ctk.CTkLabel if USE_CTK else ttk.Label
        
        # Get affinities for the selected bloodline
        affinities = self.bloodline_affinities.get(bloodline, {})
        
        # Canvas for scrollable content
        # Canvas for scrollable content
        canvas = tk.Canvas(self.table_container, highlightthickness=0)
        
        # Add scrollbar for the canvas
        scrollbar = ttk.Scrollbar(self.table_container, orient=tk.VERTICAL, command=canvas.yview)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a frame within the canvas for the table rows
        table_frame = frame_class(canvas)
        canvas.create_window((0, 0), window=table_frame, anchor="nw")
        
        # Sort elements by compatibility (descending)
        sorted_elements = sorted(
            [(element, self.data_loader.get_bloodline_element_compatibility(bloodline, element)) for element in self.elements],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Create rows for each element
        for element, percentage in sorted_elements:
            row_frame = frame_class(table_frame)
            row_frame.pack(fill=tk.X, pady=(0, 2))
            
            # Element name
            element_label = label_class(row_frame, text=element, width=15)
            element_label.pack(side=tk.LEFT, padx=5, pady=2)
            
            # Calculate color based on percentage (green = 100%, yellow = 50%, red = 0%)
            r = min(255, int(255 * (1 - percentage / 100)))
            g = min(255, int(255 * (percentage / 100)))
            b = 0
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            # Create a frame for the percentage display with color background
            percentage_frame = tk.Frame(row_frame, bg=color, width=200, height=20)
            percentage_frame.pack(side=tk.LEFT, padx=5, pady=2)
            
            # Add text with percentage
            percentage_label = tk.Label(percentage_frame, text=f"{percentage:.0f}%", 
                                        bg=color, fg="black" if percentage > 50 else "white")
            percentage_label.pack(padx=5)
        
        # Update canvas scrolling region
        table_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Update status bar
        self.status_var.set(f"Showing compatibility for {bloodline} bloodline")
    
    def update_element_compatibility(self, *args):
        """Update the compatibility display when element or bloodline changes."""
        try:
            element = self.tk_vars["element"].get()
            bloodline = self.tk_vars["bloodline"].get()
            
            if not (element and bloodline):
                self.compatibility_var.set("Compatibility: N/A")
                if not USE_CTK and hasattr(self, 'compatibility_label'):
                    self.compatibility_label.configure(text="Compatibility: N/A")
                return
            
            # Get detailed compatibility info using SpellCalculator
            # Create a simple caster object with bloodline for effective level calculation
            class SimpleCaster:
                def __init__(self, bloodline):
                    self.bloodline = bloodline
                    self.magical_affinity = 0
                    self.preferred_elements = []
                    self.restricted_elements = []
                    self.class_die = 10  # Default class die for display purposes
            
            caster = SimpleCaster(bloodline)
            power_level = self.tk_vars["power_level"].get()
            
            # Get the effective spell level (an integer)
            effective_level = self.spell_maker.spell_calculator.get_effective_spell_level(
                caster, element, power_level
            )
            # Get the compatibility percentage from SpellCalculator
            # This loads exact values from Standardized_Compatibility.json
            compatibility = self.spell_maker.spell_calculator.get_bloodline_compatibility(
                bloodline, element
            )
            
            # Calculate affinity bonus based on compatibility percentage
            affinity_bonus = compatibility // 10
            
            # Get descriptor based on compatibility percentage from Standardized_Compatibility.json
            if compatibility == 100:
                descriptor = "Perfect Harmony"
            elif compatibility == 80:
                descriptor = "Strong Affinity"
            elif compatibility == 60:
                descriptor = "Compatible"
            elif compatibility == 50:
                descriptor = "Sun's Balance"
            elif compatibility == 40:
                descriptor = "Moderate Resonance"
            elif compatibility == 20:
                descriptor = "Weak Connection"
            else:
                descriptor = "Elemental Rejection"
            
            # Calculate level adjustment (difference between effective and base levels)
            level_adjustment = effective_level - power_level
            
            # Calculate color (red to green gradient based on compatibility)
            r = min(255, int(255 * (1 - compatibility / 100)))
            g = min(255, int(255 * (compatibility / 100)))
            b = 0
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            # Update text and color based on widget type
            # Update text and color based on widget type
            # Create the dice notation formula: "level'd'class_die + affinity_bonus"
            dice_formula = f"{power_level}d{caster.class_die}+{affinity_bonus}"
            compatibility_text = f"Compatibility: {compatibility}% - {descriptor} (Formula: {dice_formula})"
            # Set the compatibility variable for CustomTkinter
            self.compatibility_var.set(compatibility_text)
            
            # For standard tkinter, we need to update the text property directly
            if not USE_CTK and hasattr(self, 'compatibility_label'):
                self.compatibility_label.configure(text=compatibility_text)
                try:
                    self.compatibility_label.configure(foreground=color)
                except Exception:
                    pass  # Some widgets might not support color changes
            elif USE_CTK and hasattr(self, 'compatibility_label'):
                try:
                    self.compatibility_label.configure(text_color=color)
                except Exception:
                    try:
                        self.compatibility_label.configure(foreground=color)
                    except Exception:
                        pass  # Handle any widget that doesn't support color changes
                        
        except Exception as e:
            error_text = f"Compatibility error: {str(e)}"
            self.compatibility_var.set(error_text)
            if not USE_CTK and hasattr(self, 'compatibility_label'):
                self.compatibility_label.configure(text=error_text)
    
    def create_spell(self):
        """Create a spell based on the current input values."""
        try:
            # Get values from UI
            effect = self.tk_vars["effect"].get()
            element = self.tk_vars["element"].get()
            bloodline = self.tk_vars["bloodline"].get()
            magic_specialty = self.tk_vars["magic_specialty"].get()
            
            # Get the display value and convert back to the internal key
            duration_display = self.tk_vars["duration"].get()
            duration = self.duration_reverse_mapping.get(duration_display, duration_display)
            
            range_val = self.tk_vars["range"].get()
            power_level = self.tk_vars["power_level"].get()
            
            # Validate inputs
            if not all([effect, element, duration, range_val]):
                self._show_error("All fields are required")
                return
            
            # Create specialty instance with appropriate level
            specialty_class = self.specialty_classes.get(magic_specialty)
            specialty_instance = None
            if specialty_class:
                specialty_instance = specialty_class(level=power_level)
            
            # Create the spell with bloodline and specialty information
            spell = self.spell_maker.create_spell(
                effect=effect,
                element=element,
                duration=duration,
                range_value=range_val,
                level=power_level,
                bloodline=bloodline,
                magical_affinity=0,  # Default value, can be enhanced with character progression
                specialty=specialty_instance
            )
            
            # Use original text as description if available and option is enabled
            if self.use_original_text and self.original_spell_text:
                description = self.original_spell_text
            else:
                description = spell.get("description", "")
            
            # Check if effectiveness data is available
            effectiveness_data = spell.get("effectiveness", None)
            
            if effectiveness_data:
                # Extract effectiveness information
                compatibility = effectiveness_data["compatibility"]
                effective_level = effectiveness_data["effective_level"]
                level_adjustment = effectiveness_data["level_adjustment"]
                descriptor = effectiveness_data["descriptor"]
                
                # Format level adjustment text
                if level_adjustment > 0:
                    level_text = f"increased by {level_adjustment} to {effective_level}"
                elif level_adjustment < 0:
                    level_text = f"decreased by {abs(level_adjustment)} to {effective_level}"
                else:
                    level_text = f"unchanged at {effective_level}"
                
                # The compatibility value is already standardized from Standardized_Compatibility.json
                # Use compatibility directly without recalculating
                compatibility_value = compatibility
                
                # Calculate the affinity bonus based on compatibility
                affinity_bonus = compatibility // 10
                
                # Create the dice notation formula
                # Assume a default class_die of 10 if not specified elsewhere
                class_die = 10
                if hasattr(self, "spell_maker") and hasattr(self.spell_maker, "spell_calculator"):
                    # If we have a caster with bloodline, try to get the appropriate class die
                    class SimpleCaster:
                        def __init__(self, bloodline, specialty=None):
                            self.bloodline = bloodline
                            self.specialty = specialty
                            # Use specialty class die if available
                            if specialty and hasattr(specialty, 'class_die'):
                                self.class_die = specialty.class_die
                            else:
                                self.class_die = 10
                            
                            # Set preferred and restricted elements if specialty has them
                            if specialty and hasattr(specialty, 'preferred_elements'):
                                self.preferred_elements = specialty.preferred_elements
                            else:
                                self.preferred_elements = []
                                
                            if specialty and hasattr(specialty, 'restricted_elements'):
                                self.restricted_elements = specialty.restricted_elements
                            else:
                                self.restricted_elements = []
                    caster = SimpleCaster(bloodline, specialty_instance)
                    # If there's a way to determine class_die based on bloodline, it would go here
                
                if effectiveness_data:
                    # Use formula from effectiveness_data if available, otherwise create a fallback
                    formula = effectiveness_data.get("formula", f"{power_level}d{class_die}+{affinity_bonus}")

                    # Get the final formula that uses the effective level
                    final_formula = effectiveness_data.get("final_formula", "")
                    
                    # Add detailed effectiveness info to description
                    effectiveness_info = (
                        f"\n\nBloodline Effectiveness:\n"
                        f"Your {bloodline} bloodline has {compatibility}% affinity with {element} magic.\n"
                        f"Spell effectiveness: {descriptor}\n"
                        f"Base spell formula: {formula}\n"
                        f"Final spell formula: {final_formula}\n"
                        f"Effective spell level: {level_text}"
                    )
                    description += effectiveness_info
                else:
                    # Fallback to basic compatibility info if effectiveness data is not available
                    compatibility = self.data_loader.get_bloodline_element_compatibility(bloodline, element)
                    description += f"\n\nBloodline Compatibility: Your {bloodline} bloodline has {compatibility:.0f}% affinity with {element} magic."
            # Add magic specialty information to the description if available
            if specialty_instance:
                specialty_info = (
                    f"\n\nMagic Specialty: {magic_specialty}\n"
                    f"Class Die: d{specialty_instance.class_die}\n"
                    f"Preferred Elements: {', '.join(specialty_instance.preferred_elements)}\n"
                    f"Restricted Elements: {', '.join(specialty_instance.restricted_elements)}\n"
                )
                description += specialty_info
            
            # Display the results
            self._set_output_text(spell.get("incantation", ""), description)
            
            # Update status bar
            if effectiveness_data:
                self.status_var.set(
                    f"Created spell: {effect} {element} ({compatibility}% compatibility, {effectiveness_data['descriptor']})"
                )
            else:
                self.status_var.set(f"Created spell: {effect} {element} ({compatibility:.0f}% compatibility with {bloodline})")
        except Exception as e:
            self.status_var.set(f"Error creating spell: {str(e)}")
            messagebox.showerror("Spell Creation Error", f"Could not create spell: {str(e)}")
            # Clear output or show placeholder text
            self._set_output_text("", "Error occurred while creating the spell.")

    def clear_fields(self):
        """Clear all input and output fields."""
        try:
            # Clear stored original text
            self.original_spell_text = None
            
            # Reset input fields to default values
            if self.effects:
                self.tk_vars["effect"].set(self.effects[0])
            else:
                self.tk_vars["effect"].set("")
                
            if self.elements:
                self.tk_vars["element"].set(self.elements[0])
            else:
                self.tk_vars["element"].set("")
                
            if self.durations:
                # Set to the formatted duration display value
                self.tk_vars["duration"].set(self.durations[0])
            else:
                self.tk_vars["duration"].set("")
                
            if self.ranges:
                self.tk_vars["range"].set(self.ranges[0])
            else:
                self.tk_vars["range"].set("")
                
            # Reset power level to 1
            self.tk_vars["power_level"].set(1)
            
            # Reset magic specialty to the first value
            if self.magic_specialties:
                self.tk_vars["magic_specialty"].set(self.magic_specialties[0])
            else:
                self.tk_vars["magic_specialty"].set("")
            
            # Clear output text fields
            self.incantation_text.delete("1.0", tk.END)
            self.description_text.delete("1.0", tk.END)
            
            # Update status
            self.status_var.set("Fields cleared")
        except Exception as e:
            self.status_var.set(f"Error clearing fields: {str(e)}")
            messagebox.showerror("Error", f"Could not clear fields: {str(e)}")

    def _set_output_text(self, incantation, description):
        """Set the output text fields with the given incantation and description."""
        # Clear existing text
        self.incantation_text.delete("1.0", tk.END)
        self.description_text.delete("1.0", tk.END)
        
        # Insert new text
        self.incantation_text.insert("1.0", incantation)
        self.description_text.insert("1.0", description)
        
    def _show_error(self, message):
        """Show an error message."""
        self.status_var.set(f"Error: {message}")
        messagebox.showerror("Error", message)

    def generate_random_spell(self):
        """Generate a random spell using random parameters."""
        import random

        try:
            # Check if parameters should be locked or randomized
            lock_effect = self.tk_vars["lock_effect"].get()
            lock_element = self.tk_vars["lock_element"].get()
            lock_duration = self.tk_vars["lock_duration"].get()
            lock_range = self.tk_vars["lock_range"].get()
            lock_magic_specialty = self.tk_vars["lock_magic_specialty"].get() if "lock_magic_specialty" in self.tk_vars else False
            
            # Get current parameter values for locked parameters
            current_effect = self.tk_vars["effect"].get()
            current_element = self.tk_vars["element"].get()
            current_duration_display = self.tk_vars["duration"].get() 
            current_duration = self.duration_reverse_mapping.get(current_duration_display, current_duration_display)
            current_range = self.tk_vars["range"].get()
            current_magic_specialty = self.tk_vars["magic_specialty"].get()
            
            # Randomly select parameters, respecting locked values
            random_effect = current_effect if lock_effect else (random.choice(self.effects) if self.effects else "")
            random_element = current_element if lock_element else (random.choice(self.elements) if self.elements else "")
            
            if lock_duration:
                random_duration_display = current_duration_display
                random_duration = current_duration
            else:
                random_duration_display = random.choice(self.durations) if self.durations else ""
                random_duration = self.duration_reverse_mapping.get(random_duration_display, random_duration_display)
                
            random_range = current_range if lock_range else (random.choice(self.ranges) if self.ranges else "")
            random_power_level = random.randint(1, 10)
            random_magic_specialty = random.choice(self.magic_specialties) if self.magic_specialties else ""

            # Validate random selections
            if not all([random_effect, random_element, random_duration, random_range, random_magic_specialty]):
                self._show_error("Unable to generate random spell: missing data options")
                return

            # Create specialty instance
            specialty_class = self.specialty_classes.get(random_magic_specialty)
            specialty_instance = None
            if specialty_class:
                specialty_instance = specialty_class(level=random_power_level)

            # Create the spell
            spell = self.spell_maker.create_spell(
                effect=random_effect,
                element=random_element,
                duration=random_duration,
                range_value=random_range,
                level=random_power_level,
                specialty=specialty_instance
            )

            # Display the results
            # Clear existing text
            self.random_incantation_text.delete("1.0", tk.END)
            self.random_description_text.delete("1.0", tk.END)
            self.spell_details_text.delete("1.0", tk.END)

            # Insert new text
            self.random_incantation_text.insert("1.0", spell.get("incantation", ""))
            self.random_description_text.insert("1.0", spell.get("description", ""))

            # Display the parameters that were randomly selected, with indicators for locked parameters
            details = f"Effect: {random_effect}{' (Locked)' if lock_effect else ''}\n"
            details += f"Element: {random_element}{' (Locked)' if lock_element else ''}\n"
            details += f"Duration: {random_duration_display}{' (Locked)' if lock_duration else ''}\n"
            details += f"Range: {random_range}{' (Locked)' if lock_range else ''}\n"
            details += f"Power Level: {random_power_level}\n"
            details += f"Magic Specialty: {random_magic_specialty}\n"
            
            # Update the main spell creation fields with the generated parameters
            self.tk_vars["effect"].set(random_effect)
            self.tk_vars["element"].set(random_element)
            self.tk_vars["duration"].set(random_duration_display)
            self.tk_vars["range"].set(random_range)
            self.tk_vars["power_level"].set(random_power_level)
            self.tk_vars["magic_specialty"].set(random_magic_specialty)
            self.spell_details_text.insert("1.0", details)

            self.status_var.set(f"Generated random spell: {random_effect} {random_element}")
        except Exception as e:
            self.status_var.set(f"Error generating random spell: {str(e)}")
            messagebox.showerror("Random Spell Error", f"Could not generate random spell: {str(e)}")
            # Clear output or show placeholder text
            self.random_incantation_text.delete("1.0", tk.END)
            self.random_description_text.delete("1.0", tk.END)
            self.spell_details_text.delete("1.0", tk.END)
            self.spell_details_text.insert("1.0", f"Error occurred: {str(e)}")

    def lock_current_parameters(self):
        """Lock all current parameter values in the random generator."""
        try:
            # Set all lock checkboxes to True
            self.tk_vars["lock_effect"].set(True)
            self.tk_vars["lock_element"].set(True)
            self.tk_vars["lock_duration"].set(True)
            self.tk_vars["lock_range"].set(True)
            
            # Update status
            self.status_var.set("All current parameters locked")
        except Exception as e:
            self.status_var.set(f"Error locking parameters: {str(e)}")
            messagebox.showerror("Error", f"Could not lock parameters: {str(e)}")

    def analyze_spell_text(self):
        """
        Analyze the text input to extract spell parameters using the NLProcessor.
        Uses natural language processing to identify effect, element, duration, and range.
        """
        try:
            # Get the text from the input area
            text = self.nlp_input_text.get("1.0", tk.END).strip()
            
            # Store the original text
            self.original_spell_text = text
            
            if not text:
                self.nlp_status_var.set("Please enter a spell description first.")
                return
                
            # Clear previous results
            self.nlp_effect_var.set("")
            self.nlp_element_var.set("")
            self.nlp_duration_var.set("")
            self.nlp_range_var.set("")
            
            # Update status while processing
            self.nlp_status_var.set("Analyzing text...")
            
            # Use the already initialized NLProcessor instance
            processor = self.nl_processor
            
            # Process the text to extract parameters
            extracted_params = processor.process_text(text)
            
            # Check if any parameters were found
            found_params = False
            
            # Set extracted values in the output fields
            if extracted_params.get("effect"):
                self.nlp_effect_var.set(extracted_params["effect"])
                found_params = True
            else:
                self.nlp_effect_var.set("Not found in text")
                
            if extracted_params.get("element"):
                self.nlp_element_var.set(extracted_params["element"])
                found_params = True
            else:
                self.nlp_element_var.set("Not found in text")
                
            if extracted_params.get("duration"):
                # Use formatted display value for duration
                duration_key = extracted_params["duration"]
                formatted_duration = self.format_duration(duration_key)
                self.nlp_duration_var.set(formatted_duration)
                found_params = True
            else:
                self.nlp_duration_var.set("Not found in text")
                
            if extracted_params.get("range"):
                self.nlp_range_var.set(extracted_params["range"])
                found_params = True
            else:
                self.nlp_range_var.set("Not found in text")
            
            # Enable/disable the "Use These Parameters" button based on whether parameters were found
            if found_params:
                self.use_params_button.configure(state="normal")
                self.nlp_status_var.set("Analysis complete. Parameters found.")
            else:
                self.use_params_button.configure(state="disabled")
                self.nlp_status_var.set("Analysis complete. No parameters found in text.")
            
            # Update main status
            self.status_var.set("Text analysis completed successfully.")
            
        except Exception as e:
            self.nlp_status_var.set(f"Error analyzing text: {str(e)}")
            messagebox.showerror("Text Analysis Error", f"Could not analyze text: {str(e)}")
    
    def use_nlp_parameters(self):
        """
        Use the parameters extracted from NLP in the main spell creator tab.
        If the 'use original text' checkbox is checked, use the original input text
        as the spell description instead of the generated one.
        """
        try:
            # Get values from NLP fields
            effect = self.nlp_effect_var.get()
            element = self.nlp_element_var.get()
            duration = self.nlp_duration_var.get()
            range_val = self.nlp_range_var.get()
            
            # Get the original text from the input area
            original_text = self.nlp_input_text.get("1.0", tk.END).strip()
            
            # Store the original text and preference for later use in create_spell method
            self.original_spell_text = original_text
            self.use_original_text = self.use_original_text_var.get()
            
            # Check if we have valid values
            if "Not found in text" in [effect, element, duration, range_val]:
                self.nlp_status_var.set("Cannot use parameters: some values were not found in the text.")
                return
                
            # Set the values in the main spell creator tab
            # Set the values in the main spell creator tab
            self.tk_vars["effect"].set(effect)
            self.tk_vars["element"].set(element)
            
            # Find the matching duration display value
            for display_val in self.durations:
                if duration in display_val:
                    self.tk_vars["duration"].set(display_val)
                    break
            
            self.tk_vars["range"].set(range_val)
            
            # Convert duration from display format back to internal format for spell creation
            duration_key = self.duration_reverse_mapping.get(self.tk_vars["duration"].get(), duration)
            
            # Get magic specialty and create a specialty instance
            magic_specialty = self.tk_vars["magic_specialty"].get()
            power_level = self.tk_vars["power_level"].get()
            
            # Create specialty instance with appropriate level
            specialty_class = self.specialty_classes.get(magic_specialty)
            specialty_instance = None
            if specialty_class:
                specialty_instance = specialty_class(level=power_level)
            
            # Check if we should use the original description text
            if self.use_original_text_var.get() and original_text:
                # Create the spell with the parameters but we'll override the description
                spell = self.spell_maker.create_spell(
                    effect=effect,
                    element=element,
                    duration=duration_key,
                    range_value=range_val,
                    level=self.tk_vars["power_level"].get(),
                    specialty=specialty_instance
                )
                
                # Override the generated description with the original text
                spell["description"] = original_text
                
                # Display the results directly
                self._set_output_text(spell.get("incantation", ""), original_text)
                self.status_var.set(f"Created spell using original description text")
            else:
                # Just switch to the spell creator tab and let the user click "Create Spell"
                self.notebook.select(0)  # First tab (index 0) is the spell creator
                self.status_var.set("Parameters transferred from NLP analysis. Click 'Create Spell' to generate.")
            
        except Exception as e:
            self.nlp_status_var.set(f"Error using parameters: {str(e)}")
            messagebox.showerror("Parameter Transfer Error", f"Could not use parameters: {str(e)}")

    def save_spell_to_history(self):
        """Save the current spell to the spell history."""
        try:
            # Get values from UI
            effect = self.tk_vars["effect"].get()
            element = self.tk_vars["element"].get()
            bloodline = self.tk_vars["bloodline"].get()
            
            # Get the display value and convert back to the internal key
            duration_display = self.tk_vars["duration"].get()
            duration = self.duration_reverse_mapping.get(duration_display, duration_display)
            
            range_val = self.tk_vars["range"].get()
            power_level = self.tk_vars["power_level"].get()
            
            # Validate inputs
            if not all([effect, element, duration, range_val]):
                self._show_error("All fields are required")
                return
            
            # Get spell information
            spell_name = format_spell_name(effect, element)
            
            # Check which tab is currently active
            current_tab = self.notebook.index("current")
            
            # Get the text from the appropriate fields based on the active tab
            if current_tab == 1:  # Random Generator tab (index 1)
                incantation = self.random_incantation_text.get("1.0", tk.END).strip()
                description = self.random_description_text.get("1.0", tk.END).strip()
            else:  # Main spell creator tab (index 0) or any other tab
                incantation = self.incantation_text.get("1.0", tk.END).strip()
                description = self.description_text.get("1.0", tk.END).strip()
            
            # Check if we have output text
            if not incantation or not description:
                self._show_error("Please create a spell first before saving to history")
                return
            
            # Create the spell data to save
            spell_data = {
                "name": spell_name.replace("-", " "),
                "incantation": incantation,
                "description": description,
                "effect": effect,
                "element": element,
                "duration": duration_display,  # Use formatted duration for display
                "range": range_val,
                "level": power_level
            }
            if hasattr(self, 'spell_history_panel'):
                self.spell_history_panel.add_spell(spell_data)
                # Update status message with tab info
                tab_source = "Random Generator" if current_tab == 1 else "Spell Creator"
                self.status_var.set(f"Spell '{spell_name}' from {tab_source} tab saved to history")
            else:
                self.status_var.set(f"Error: Spell history panel not initialized")
        except Exception as e:
            self.status_var.set(f"Error saving spell to history: {str(e)}")
            messagebox.showerror("Spell History Error", f"Could not save spell to history: {str(e)}")
    def open_spell_history(self):
        """Initialize the Spell History panel in the spell history tab."""
        try:
            # Clear any existing widgets in the spell history tab
            for widget in self.spell_history_tab.winfo_children():
                widget.destroy()
                
            # Initialize the SpellTomeWindow in the spell_history_tab
            self.spell_history_panel = SpellTomeWindow(self.spell_history_tab, data_loader=self.data_loader, use_ctk=USE_CTK)
            self.status_var.set("Spell History panel initialized")
        except Exception as e:
            self.status_var.set(f"Error initializing spell history panel: {str(e)}")
            messagebox.showerror("Spell History Error", f"Could not initialize spell history panel: {str(e)}")

