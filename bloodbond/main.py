#!/usr/bin/env python3
"""
BloodBond Enhanced Tools - Main Entry Point

This module serves as the main entry point for the BloodBond Enhanced Tools application.
It provides functions to start both the GUI and CLI versions of the application.
"""

import argparse
import logging
import os
import sys
import traceback
from pathlib import Path

# Import core functionality
from bloodbond.core.data_loader import DataLoader
from bloodbond.core.element_mapper import ElementMapper
from bloodbond.core.spell_maker import SpellMaker

# Import UI components
from bloodbond.ui.gui import SpellCreatorApp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'bloodbond.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def setup_application():
    """
    Initialize application resources and data loaders.
    
    Returns:
        tuple: Containing DataLoader, ElementMapper, and SpellMaker instances
    """
    try:
        logger.info("Initializing BloodBond Enhanced Tools")
        
        # Get the path to the data directory
        data_dir = Path(__file__).parent / 'data'
        
        # Initialize the data loader
        data_loader = DataLoader(data_dir)
        
        # Initialize element mapper
        element_mapper = ElementMapper()
        
        # Initialize spell maker
        spell_maker = SpellMaker(data_loader, element_mapper)
        
        logger.info("Application setup complete")
        return data_loader, element_mapper, spell_maker
    
    except Exception as e:
        logger.error(f"Error during application setup: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"Error initializing application: {str(e)}")
        sys.exit(1)


def start_gui(use_ctk=False):
    """
    Start the graphical user interface version of the application.
    
    Args:
        use_ctk (bool): Whether to use customtkinter if available (True) or force standard tkinter (False)
    """
    try:
        logger.info("Starting GUI application")
        
        # Initialize the application components
        data_loader, element_mapper, spell_maker = setup_application()
        
        # Create the tkinter root window
        import tkinter as tk
        if use_ctk:
            try:
                # Try to use customtkinter if available
                import customtkinter as ctk
                root = ctk.CTk()
                logger.info("Using customtkinter for enhanced UI")
            except ImportError:
                # Fall back to standard tkinter
                root = tk.Tk()
                logger.info("customtkinter not found, falling back to standard tkinter")
        else:
            # Force use of standard tkinter
            root = tk.Tk()
            logger.info("Using standard tkinter as requested")
        
        # Create the GUI application with the root window
        app = SpellCreatorApp(root, use_ctk=use_ctk)
        
        # Start the tkinter main loop
        logger.info("Starting tkinter main loop")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Error in GUI mode: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"Error running GUI: {str(e)}")
        sys.exit(1)


def start_cli():
    """
    Start the command-line interface version of the application.
    """
    try:
        logger.info("Starting CLI application")
        data_loader, element_mapper, spell_maker = setup_application()
        
        print("BloodBond Enhanced Tools CLI")
        print("==========================")
        
        while True:
            print("\nSpell Creation Menu:")
            print("1. Create new spell")
            print("2. Show element affinities")
            print("3. List available effects")
            print("4. List available elements")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == '1':
                effect = input("Enter effect (e.g., damage, heal, shield): ")
                element = input("Enter element (e.g., fire, water, air): ")
                duration = input("Enter duration (e.g., instant, 1 minute, 1 hour): ")
                range_val = input("Enter range (e.g., self, touch, 30ft): ")
                
                try:
                    spell = spell_maker.create_spell(effect, element, duration, range_val)
                    
                    print("\n=== Spell Created ===")
                    print(f"Incantation: {spell['incantation']}")
                    print(f"Description: {spell['description']}")
                    print(f"Duration: {spell['duration_text']}")
                    print(f"Range: {spell['range_text']}")
                except Exception as e:
                    print(f"Error creating spell: {str(e)}")
                    
            elif choice == '2':
                affinities = data_loader.get_bloodline_affinities()
                print("\n=== Bloodline Affinities ===")
                for bloodline, affinities in affinities.items():
                    print(f"\n{bloodline}:")
                    for element, value in affinities.items():
                        print(f"  {element}: {value}%")
                        
            elif choice == '3':
                effects = data_loader.get_spell_effects()
                print("\n=== Available Effects ===")
                for effect in effects:
                    print(f"- {effect}")
                    
            elif choice == '4':
                elements = data_loader.get_spell_elements()
                print("\n=== Available Elements ===")
                for element in elements:
                    print(f"- {element}")
                    
            elif choice == '5':
                print("Exiting BloodBond Enhanced Tools CLI. Goodbye!")
                break
                
            else:
                print("Invalid choice. Please select a number between 1 and 5.")
                
    except Exception as e:
        logger.error(f"Error in CLI mode: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"Error running CLI: {str(e)}")
        sys.exit(1)


def main():
    """
    Main entry point function that parses command-line arguments
    and starts the application in the appropriate mode.
    """
    parser = argparse.ArgumentParser(
        description='BloodBond Enhanced Tools - A spell creation system for the Blood Bond TTRPG'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Start the application in command-line interface mode'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Start the application in graphical user interface mode (default)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--use-customtkinter',
        action='store_true',
        help='Use customtkinter instead of standard tkinter for the GUI'
    )
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Start in the appropriate mode
    if args.cli:
        start_cli()
    else:
        # Default to GUI mode
        start_gui(use_ctk=args.use_customtkinter)


if __name__ == '__main__':
    main()

