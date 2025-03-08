#!/usr/bin/env python3
"""
Run Application script for Blood Bond Enhanced Tools.
This script handles tkinter/customtkinter imports and provides error handling during application startup.

Standard tkinter is used by default. Use --use-customtkinter flag to enable customtkinter.
"""
import sys
import os
import traceback
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def setup_import_paths():
    """Add the project root to the import path if running as script."""
    script_dir = Path(__file__).resolve().parent
    if script_dir not in sys.path:
        sys.path.insert(0, str(script_dir))

def setup_tkinter(use_customtkinter=False, force_standard=False):
    """Setup tkinter environment with standard tkinter as default and customtkinter as opt-in.
    
    Args:
        use_customtkinter (bool): If True, try to use customtkinter instead of standard tkinter.
        force_standard (bool): If True, force the use of standard tkinter regardless of other settings.
    """
    # force_standard takes precedence over use_customtkinter
    if force_standard:
        try:
            import tkinter
            logger.info("Using standard tkinter as requested by --use-standard-tkinter flag")
            return False
        except ImportError:
            logger.error("Unable to import tkinter. Please ensure tkinter is installed.")
            return None
    
    # Use customtkinter only if explicitly requested
    if use_customtkinter:
        try:
            import customtkinter
            logger.info("Using customtkinter for enhanced UI as requested by --use-customtkinter flag")
            return True
        except ImportError:
            logger.info("customtkinter requested but not found, falling back to standard tkinter")
            try:
                import tkinter
                logger.info("Standard tkinter imported successfully")
                return False
            except ImportError:
                logger.error("Unable to import tkinter. Please ensure tkinter is installed.")
                return None
    
    # Default to standard tkinter
    try:
        import tkinter
        logger.info("Using standard tkinter (default behavior)")
        return False
    except ImportError:
        logger.error("Unable to import tkinter. Please ensure tkinter is installed.")
        return None

def main():
    """Main entry point for the application."""
    
    # Create argument parser
    parser = argparse.ArgumentParser(description='Blood Bond Enhanced Tools')
    parser.add_argument('--use-standard-tkinter', action='store_true', 
                        help='Force the use of standard tkinter (default behavior, provided for backward compatibility)')
    parser.add_argument('--use-customtkinter', action='store_true',
                        help='Use customtkinter instead of standard tkinter for enhanced UI')
    args = parser.parse_args()
    
    logger.info("Starting Blood Bond Enhanced Tools")
    
    # Setup imports
    setup_import_paths()
    
    # Check tkinter environment
    use_ctk = setup_tkinter(use_customtkinter=args.use_customtkinter, force_standard=args.use_standard_tkinter)
    if use_ctk is None:
        logger.error("Exiting due to missing tkinter. Please install tkinter and try again.")
        return 1
    
    try:
        # Import main module
        from bloodbond.main import setup_application, start_gui
        logger.info("Successfully imported application modules")
        
        # Run the application
        if args.use_standard_tkinter:
            logger.info("Using standard tkinter interface as requested (--use-standard-tkinter)")
        elif args.use_customtkinter:
            logger.info("Using customtkinter interface as requested (--use-customtkinter)")
        else:
            logger.info("Using standard tkinter interface (default behavior)")
        start_gui(use_ctk=use_ctk)
        logger.info("Application exit successfully")
        return 0
    except Exception as e:
        logger.error(f"Error running application: {e}")
        logger.error("Detailed traceback:")
        traceback.print_exc()
        
        # Show error in GUI if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Application Error",
                f"An error occurred while starting the application:\n\n{str(e)}\n\n"
                "Please check the console output for more details."
            )
            root.destroy()
        except Exception:
            # If we can't show a GUI error, just print to console
            logger.error("Could not display error dialog")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

