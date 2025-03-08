#!/usr/bin/env python3
"""
Script to generate the bloodline_affinities JSON from the BLOODLINE_COMPATIBILITY constant.

This script:
1. Imports the SpellCalculator class to access the BLOODLINE_COMPATIBILITY constant
2. Converts the compatibility dictionary to the JSON structure expected in spell_data.json
3. Prints the formatted JSON that can replace the current bloodline_affinities section
"""

import json
import sys
from bloodbond.core.spell_calculator import SpellCalculator

def generate_bloodline_affinities():
    """
    Generate the bloodline_affinities JSON from the BLOODLINE_COMPATIBILITY constant.
    
    Returns:
        dict: The generated bloodline_affinities dictionary in the format expected by spell_data.json
    """
    # Access the BLOODLINE_COMPATIBILITY constant from SpellCalculator
    compat_dict = SpellCalculator.BLOODLINE_COMPATIBILITY
    
    # Initialize the result dictionary
    bloodline_affinities = {}
    
    # Iterate through each bloodline in the compatibility dictionary
    for bloodline, compatibilities in compat_dict.items():
        # Initialize categories for this bloodline
        bloodline_data = {
            "Best 100%": [],
            "Best 80%": [],
            "Good 60%": [],
            "Moderate 40%": [],
            "Weak 20%": [],
            "Neutral 50%": []
        }
        
        # Categorize elements based on compatibility percentage
        for element, compatibility in compatibilities.items():
            if compatibility == 100:
                bloodline_data["Best 100%"].append(element.capitalize())
            elif compatibility == 80:
                bloodline_data["Best 80%"].append(element.capitalize())
            elif compatibility == 60:
                bloodline_data["Good 60%"].append(element.capitalize())
            elif compatibility == 40:
                bloodline_data["Moderate 40%"].append(element.capitalize())
            elif compatibility == 20:
                bloodline_data["Weak 20%"].append(element.capitalize())
            elif compatibility == 50:
                bloodline_data["Neutral 50%"].append(element.capitalize())
        
        # Add this bloodline's data to the result
        bloodline_affinities[bloodline.capitalize()] = bloodline_data
    
    return bloodline_affinities

def print_bloodline_affinities_json():
    """
    Print the bloodline_affinities JSON that can be used to replace the current section in spell_data.json.
    """
    bloodline_affinities = generate_bloodline_affinities()
    
    # Convert to JSON with proper formatting
    json_str = json.dumps({"bloodline_affinities": bloodline_affinities}, indent=4)
    
    # Print the result
    print("\nGenerated bloodline_affinities JSON:\n")
    print(json_str)
    print("\n\nYou can replace the bloodline_affinities section in spell_data.json with this JSON.")

def verify_compatibility_values():
    """
    Verify that all compatibility values in BLOODLINE_COMPATIBILITY are standardized to 20%, 40%, 60%, 80%, 100%, or 50% for Sun.
    """
    compat_dict = SpellCalculator.BLOODLINE_COMPATIBILITY
    
    valid_values = {20, 40, 50, 60, 80, 100}
    issues_found = False
    
    print("Verifying standardized compatibility values...")
    
    for bloodline, compatibilities in compat_dict.items():
        for element, compatibility in compatibilities.items():
            if compatibility not in valid_values:
                print(f"ERROR: Non-standard value found: {bloodline} + {element} = {compatibility}%")
                issues_found = True
    
    if not issues_found:
        print("All compatibility values are standardized correctly.")
    else:
        print("Issues were found with the standardized values. Please fix them in SpellCalculator.BLOODLINE_COMPATIBILITY.")

if __name__ == "__main__":
    print("Bloodline Affinities Generator")
    print("==============================")
    
    # First verify the compatibility values
    verify_compatibility_values()
    
    # Then generate and print the JSON
    print_bloodline_affinities_json()

