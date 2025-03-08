"""
Blood Bond Enhanced Tools - A Python package for creating and managing spells for the Blood Bond TTRPG.
"""

__version__ = '0.3.0'
__author__ = 'Blood Bond Enhanced Tools Team'

# Import main classes for direct access
from bloodbond.core.data_loader import DataLoader
from bloodbond.core.element_mapper import ElementMapper
from bloodbond.core.spell_maker import SpellMaker
from bloodbond.ui.gui import SpellCreatorApp

# Provide a convenience function to launch the application
def launch_gui():
    """Launch the Blood Bond spell creator GUI application."""
    from bloodbond.main import start_gui
    start_gui()

def launch_cli():
    """Launch the Blood Bond spell creator CLI application."""
    from bloodbond.main import start_cli
    start_cli()

