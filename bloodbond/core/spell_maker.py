"""
SpellMaker module - Core functionality for creating spells in the Blood Bond system.

This module provides the SpellMaker class which handles all aspects of spell creation
by processing input parameters and generating appropriate spell incantations and descriptions.
It integrates with DataLoader and ElementMapper to create a comprehensive spell creation system.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import json
import os
from pathlib import Path

from bloodbond.core.data_loader import DataLoader
from bloodbond.core.element_mapper import ElementMapper
from bloodbond.core.exceptions import (
    SpellError, InvalidParameterError, IncompatibleElementsError,
    SpellValidationError, SpellLimitError, DataError
)


class SpellMaker:
    """
    Core class for creating and handling Blood Bond spells.
    
    This class provides functionality to create spells with different effects,
    elements, durations, and ranges. It utilizes the DataLoader to access
    spell data and the ElementMapper to ensure proper element compatibility.
    
    Attributes:
        data_loader (DataLoader): Instance for loading and accessing spell data
        element_mapper (ElementMapper): Instance for mapping between element systems
        spoken_spell_table (Dict): Reference to the spoken spell table data
        cached_spells (Dict): Cache of previously created spells for performance
    """
    
    def __init__(self, data_loader: Optional[DataLoader] = None, 
                 element_mapper: Optional[ElementMapper] = None):
        """
        Initialize the SpellMaker with necessary components.
        
        Args:
            data_loader: Optional custom DataLoader instance
            element_mapper: Optional custom ElementMapper instance
        """
        self.data_loader = data_loader or DataLoader()
        
        # Initialize ElementMapper with appropriate parameters instead of the DataLoader instance
        if element_mapper:
            self.element_mapper = element_mapper
        else:
            # Use default ElementMapper initialization with no parameters
            self.element_mapper = ElementMapper()
            
        self.spoken_spell_table = self.data_loader.get_spoken_spell_table()
        self.cached_spells = {}
        
    def create_spell(self, effect: str, element: str, 
                     duration: str = "instant", 
                     range_value: str = "self", 
                     level: int = 1) -> Dict[str, Any]:
        """
        Create a new spell with the specified parameters.
        
        Args:
            effect: The effect of the spell (e.g., "damage", "creation")
            element: The element of the spell (e.g., "fire", "water")
            duration: The duration of the spell (default: "instant")
            range_value: The range of the spell (default: "self")
            level: The power level of the spell (default: 1)
            
        Returns:
            A dictionary containing the complete spell details including
            incantation and description
            
        Raises:
            InvalidParameterError: If effect, element, duration, or range values are invalid
            SpellValidationError: If the spell parameters fail validation
            IncompatibleElementsError: If the element combination is not allowed
            SpellLimitError: If the level is outside the allowed range
            DataError: If required data cannot be loaded or is malformed
        """
        # Generate cache key for this spell combination
        cache_key = f"{effect}|{element}|{duration}|{range_value}|{level}"
        
        # Return cached spell if available
        if cache_key in self.cached_spells:
            return self.cached_spells[cache_key]
        
        # Validate inputs
        self._validate_spell_parameters(effect, element, duration, range_value, level)
        
        # Map the element if needed
        mapped_element = self.element_mapper.map_element(element)
        
        # Debug the spell structure to understand the JSON structure
        self.debug_spell_structure(effect, mapped_element)
        
        # Generate spell components
        incantation = self._generate_incantation(effect, mapped_element, duration, range_value, level)
        description = self._generate_description(effect, mapped_element, duration, range_value, level)
        
        # Create spell object
        spell = {
            "effect": effect,
            "element": element,
            "mapped_element": mapped_element,
            "duration": duration,
            "range": range_value,
            "level": level,
            "incantation": incantation,
            "description": description
        }
        
        # Cache the spell
        self.cached_spells[cache_key] = spell
        
        return spell
    
    def create_custom_spell(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a spell using a parameters dictionary for more flexibility.
        
        Args:
            parameters: Dictionary containing spell parameters:
                - effect: The effect of the spell
                - element: The element of the spell
                - duration: The duration of the spell (optional)
                - range: The range of the spell (optional)
                - level: The power level of the spell (optional)
                - custom_modifiers: Additional custom modifiers (optional)
                
        Returns:
            A dictionary containing the complete spell details
            
        Raises:
            InvalidParameterError: If required parameters are missing or invalid
            SpellValidationError: If the spell parameters fail validation
            IncompatibleElementsError: If the element combination is not allowed
            SpellLimitError: If the level is outside the allowed range
            DataError: If required data cannot be loaded or is malformed
        """
        effect = parameters.get("effect")
        element = parameters.get("element")
        duration = parameters.get("duration", "instant")
        range_value = parameters.get("range", "self")
        level = parameters.get("level", 1)
        custom_modifiers = parameters.get("custom_modifiers", {})
        
        if not effect and not element:
            raise InvalidParameterError(
                "Effect and element are required for spell creation. Please specify both parameters."
            )
        elif not effect:
            raise InvalidParameterError(
                "Effect is required for spell creation. Please specify an effect like 'damage', 'healing', etc."
            )
        elif not element:
            raise InvalidParameterError(
                "Element is required for spell creation. Please specify an element like 'fire', 'water', etc."
            )
        
        # Create the base spell
        spell = self.create_spell(effect, element, duration, range_value, level)
        
        # Apply any custom modifiers
        if custom_modifiers:
            spell = self._apply_custom_modifiers(spell, custom_modifiers)
            
        return spell
    
    def get_available_effects(self) -> List[str]:
        """
        Get a list of all available spell effects.
        
        Returns:
            List of effect names available for spell creation
        """
        return list(self.spoken_spell_table.get("effect_prefix", {}).keys())
    
    def get_available_elements(self) -> List[str]:
        """
        Get a list of all available spell elements.
        
        Returns:
            List of element names available for spell creation
        """
        return list(self.spoken_spell_table.get("element_prefix", {}).keys())
    
    def get_available_durations(self) -> List[str]:
        """
        Get a list of all available spell durations.
        
        Returns:
            List of duration options available for spell creation
        """
        return list(self.spoken_spell_table.get("duration_modifier", {}).keys())
    
    def get_available_ranges(self) -> List[str]:
        """
        Get a list of all available spell ranges.
        
        Returns:
            List of range options available for spell creation
        """
        return list(self.spoken_spell_table.get("range_suffix", {}).keys())
    
    def get_element_affinity(self, primary_element: str, secondary_element: str) -> float:
        """
        Get the affinity percentage between two elements.
        
        Args:
            primary_element: The primary element
            secondary_element: The secondary element to check affinity with
            
        Returns:
            The affinity percentage (0.0 to 1.0) between the elements
            
        Raises:
            InvalidParameterError: If either element is not found in the bloodline affinities
            DataError: If the bloodline affinities data cannot be loaded
        """
        bloodline_affinities = self.data_loader.get_bloodline_affinities()
        
        if primary_element not in bloodline_affinities:
            available_elements = list(bloodline_affinities.keys())
            raise InvalidParameterError(
                f"Primary element '{primary_element}' not found in bloodline affinities. "
                f"Available elements: {', '.join(available_elements)}"
            )
            
        if secondary_element not in bloodline_affinities.get(primary_element, {}):
            available_secondary = list(bloodline_affinities.get(primary_element, {}).keys())
            raise InvalidParameterError(
                f"Secondary element '{secondary_element}' not found for primary element '{primary_element}'. "
                f"Available secondary elements for {primary_element}: {', '.join(available_secondary)}"
            )
            
        return bloodline_affinities[primary_element][secondary_element]
    
    def batch_create_spells(self, spell_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple spells from a list of configurations.
        
        Args:
            spell_configs: List of dictionaries, each containing parameters for create_custom_spell
            
        Returns:
            List of spell dictionaries corresponding to each configuration
        """
        return [self.create_custom_spell(config) for config in spell_configs]
    
    def export_spell_to_json(self, spell: Dict[str, Any], file_path: str) -> None:
        """
        Export a spell to a JSON file.
        
        Args:
            spell: The spell dictionary to export
            file_path: The path where the JSON file should be saved
            
        Raises:
            DataError: If there's an error writing to the file or creating the directory
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(spell, file, indent=4)
        except IOError as e:
            raise DataError(f"Error writing spell to file {file_path}: {str(e)}. "
                           f"Check if the directory is writable and you have sufficient permissions.")
        except Exception as e:
            raise DataError(f"Unexpected error when writing spell to file {file_path}: {str(e)}")
    
    def _validate_spell_parameters(self, effect: str, element: str, 
                                  duration: str, range_value: str, level: int) -> None:
        """
        Validate that the provided spell parameters exist in the data.
        
        Args:
            effect: The effect of the spell
            element: The element of the spell
            duration: The duration of the spell
            range_value: The range of the spell
            level: The power level of the spell
            
        Raises:
            InvalidParameterError: If effect, element, duration, or range values are invalid
            SpellLimitError: If the level is outside the allowed range
            SpellValidationError: If any other parameter validation fails
        """
        # Validate effect
        if not effect:
            raise InvalidParameterError("Effect cannot be empty. Please specify a spell effect.")
            
        if effect not in self.spoken_spell_table.get("effect_prefix", {}):
            available_effects = list(self.spoken_spell_table.get("effect_prefix", {}).keys())
            suggestions = self._get_closest_matches(effect, available_effects)
            suggestion_msg = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            
            raise InvalidParameterError(
                f"Invalid effect: '{effect}'. Available effects: {', '.join(available_effects)}.{suggestion_msg}"
            )
        
        # Validate element (first with element_mapper, then our own check)
        if not element:
            raise InvalidParameterError("Element cannot be empty. Please specify a spell element.")
            
        try:
            # This will raise ValueError if element is invalid
            mapped_element = self.element_mapper.map_element(element)
        except ValueError as e:
            available_elements = self.get_available_elements()
            suggestions = self._get_closest_matches(element, available_elements)
            suggestion_msg = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            
            raise InvalidParameterError(
                f"Invalid element: '{element}'. {str(e)}{suggestion_msg}"
            )
        
        # Validate duration
        if not duration:
            raise InvalidParameterError("Duration cannot be empty. Using default 'instant' duration.")
            
        if duration not in self.spoken_spell_table.get("duration_modifier", {}):
            available_durations = list(self.spoken_spell_table.get("duration_modifier", {}).keys())
            suggestions = self._get_closest_matches(duration, available_durations)
            suggestion_msg = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            
            raise InvalidParameterError(
                f"Invalid duration: '{duration}'. Available durations: {', '.join(available_durations)}.{suggestion_msg}"
            )
        
        # Validate range
        if not range_value:
            raise InvalidParameterError("Range cannot be empty. Using default 'self' range.")
            
        if range_value not in self.spoken_spell_table.get("range_suffix", {}):
            available_ranges = list(self.spoken_spell_table.get("range_suffix", {}).keys())
            suggestions = self._get_closest_matches(range_value, available_ranges)
            suggestion_msg = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            
            raise InvalidParameterError(
                f"Invalid range: '{range_value}'. Available ranges: {', '.join(available_ranges)}.{suggestion_msg}"
            )
        
        # Validate level
        if not isinstance(level, int):
            raise SpellLimitError(
                f"Spell level must be an integer, got {type(level).__name__}. Please provide a number between 1 and 10."
            )
            
        if level < 1:
            raise SpellLimitError(
                f"Spell level {level} is too low. Minimum allowed level is 1."
            )
            
        if level > 10:
            raise SpellLimitError(
                f"Spell level {level} is too high. Maximum allowed level is 10."
            )
            
        # Check for element compatibility 
        # This could be enhanced further if there are specific element combinations that aren't allowed
    
    def _generate_incantation(self, effect: str, element: str, 
                             duration: str, range_value: str, level: int) -> str:
        """
        Generate a spell incantation from the components.
        
        Args:
            effect: The effect of the spell
            element: The element of the spell
            duration: The duration of the spell
            range_value: The range of the spell
            level: The power level of the spell
            
        Returns:
            The complete spell incantation string
        """
        effect_prefix = self.spoken_spell_table["effect_prefix"].get(effect, "")
        element_prefix = self.spoken_spell_table["element_prefix"].get(element, "")
        duration_modifier = self.spoken_spell_table["duration_modifier"].get(duration, "")
        level_modifier = self.spoken_spell_table["level_modifier"].get(str(level), "")
        range_suffix = self.spoken_spell_table["range_suffix"].get(range_value, "")
        
        # Construct the incantation
        incantation_parts = []
        if effect_prefix:
            incantation_parts.append(effect_prefix)
        if element_prefix:
            incantation_parts.append(element_prefix)
        if duration_modifier:
            incantation_parts.append(duration_modifier)
        if level_modifier:
            incantation_parts.append(level_modifier)
        if range_suffix:
            incantation_parts.append(range_suffix)
        
        return " ".join(incantation_parts)
    
    def _generate_description(self, effect: str, element: str, 
                             duration: str, range_value: str, level: int) -> str:
        """
        Generate a spell description based on its components.
        
        Args:
            effect: The effect of the spell
            element: The element of the spell
            duration: The duration of the spell
            range_value: The range of the spell
            level: The power level of the spell
            
        Returns:
            A string containing the spell description
        """
        descriptions = self.data_loader.get_spell_descriptions()
        
        # Try to find an exact match for the effect-element combination
        # The structure is: descriptions["effect_prefix"][effect]["element_prefix"][element]
        base_description = None
        
        # Step 1: Try to find direct match
        if "effect_prefix" in descriptions and effect in descriptions["effect_prefix"]:
            effect_data = descriptions["effect_prefix"][effect]
            if "element_prefix" in effect_data and element in effect_data["element_prefix"]:
                # Found the description in the nested structure
                base_description = effect_data["element_prefix"][element][0]  # Take the first description
        
        # Step 2: If direct match not found, check if effect might be a sub-effect in another effect
        if base_description is None and "effect_prefix" in descriptions:
            # Loop through all effects to find if our effect might be a sub-effect
            for parent_effect, parent_data in descriptions["effect_prefix"].items():
                # Skip if we're looking at the same effect we already checked
                if parent_effect == effect:
                    continue
                    
                # Check if our effect is a key inside any effect
                if effect in parent_data:
                    sub_effect_data = parent_data[effect]
                    print(f'Found {effect} as sub-effect in {parent_effect}, structure: {type(sub_effect_data)}')
                    
                    # Check if sub-effect has element_prefix structure
                    if isinstance(sub_effect_data, dict) and "element_prefix" in sub_effect_data:
                        element_data = sub_effect_data["element_prefix"]
                        if element in element_data:
                            element_description = element_data[element]
                            # Handle both string and list formats
                            if isinstance(element_description, list) and element_description:
                                base_description = element_description[0]
                            elif isinstance(element_description, str):
                                base_description = element_description
                            break
                    # Direct element mapping without element_prefix layer
                    elif isinstance(sub_effect_data, dict) and element in sub_effect_data:
                        element_description = sub_effect_data[element]
                        # Handle both string and list formats
                        if isinstance(element_description, list) and element_description:
                            base_description = element_description[0]
                        elif isinstance(element_description, str):
                            base_description = element_description
                        break

        # Step 3: Try to find a description with the element even if effect doesn't match
        if base_description is None and "effect_prefix" in descriptions:
            for other_effect, effect_data in descriptions["effect_prefix"].items():
                if "element_prefix" in effect_data and element in effect_data["element_prefix"]:
                    # Found a description for this element, adapt it for our effect
                    element_description = effect_data["element_prefix"][element][0]
                    base_description = f"A {effect} spell that works similar to {other_effect}. {element_description}"
                    break

        # Step 4: Fallback to a generic description if all else fails
        if base_description is None:
            base_description = f"A {effect} spell using the power of {element}."
        
        # Add duration information
        duration_text = self._format_duration_text(duration)
        
        # Add range information
        range_text = self._format_range_text(range_value)
        
        # Add level information
        level_text = f"Level {level}"
        
        # Compose the full description
        full_description = (
            f"{base_description} {duration_text}. {range_text}. {level_text}."
        )
        
        return full_description
    
    def _format_duration_text(self, duration: str) -> str:
        """
        Format the duration into a readable text description.
        
        Args:
            duration: The duration identifier
            
        Returns:
            A formatted string describing the duration
        """
        if duration == "instant":
            return "The effect is instantaneous"
        elif duration == "1_minute":
            return "The spell lasts for 1 minute"
        elif duration == "5_minute":
            return "The spell persists for 5 minutes"
        elif duration == "30_minute":
            return "The spell endures for 30 minutes"
        elif duration == "1_hour":
            return "The spell lasts for 1 hour"
        elif duration == "8_hour":
            return "The spell persists for 8 hours"
        elif duration == "24_hour":
            return "The spell lasts for a full day"
        elif duration == "permanent":
            return "The spell's effect is permanent until dispelled"
        else:
            return f"The spell lasts for {duration}"
    
    def _format_range_text(self, range_value: str) -> str:
        """
        Format the range into a readable text description.
        
        Args:
            range_value: The range identifier
            
        Returns:
            A formatted string describing the range
        """
        if range_value == "self":
            return "It affects only the caster"
        elif range_value == "touch":
            return "It requires touching the target"
        elif range_value == "5ft":
            return "It affects targets within 5 feet"
        elif range_value == "30ft":
            return "It reaches targets up to 30 feet away"
        elif range_value == "100ft":
            return "It extends to targets up to 100 feet distant"
        elif range_value == "sight":
            return "It affects any target the caster can see"
        else:
            return f"It has a range of {range_value}"
    
    def _apply_custom_modifiers(self, spell: Dict[str, Any], 
                               custom_modifiers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply custom modifiers to a spell to enhance or alter its properties.
        
        This method takes a base spell and applies custom modifications, which can include:
        - Additional effects (e.g., secondary damage, healing properties)
        - Power boosts (e.g., increased damage, extended range)
        - Special properties (e.g., silence effect, armor penetration)
        - Custom incantation additions
        - Description enhancements
        
        Args:
            spell: The base spell dictionary to modify
            custom_modifiers: Dictionary of custom modifiers to apply, which may include:
                - additional_effects: List of additional effects to add
                - power_boost: Percentage to increase the spell's power
                - special_properties: List of special properties to add
                - custom_incantation_suffix: String to append to the incantation
                - description_enhancement: Additional text for the description
                
        Returns:
            The modified spell dictionary with all custom modifiers applied
            
        Raises:
            InvalidParameterError: If an invalid modifier type is provided
            SpellValidationError: If the modified spell would be invalid
        """
        # Create a copy of the spell to avoid modifying the original
        modified_spell = spell.copy()
        
        # Apply additional effects
        if 'additional_effects' in custom_modifiers:
            additional_effects = custom_modifiers['additional_effects']
            if not isinstance(additional_effects, list):
                additional_effects = [additional_effects]
                
            # Add additional effects to the spell
            if 'additional_effects' not in modified_spell:
                modified_spell['additional_effects'] = []
            modified_spell['additional_effects'].extend(additional_effects)
            
            # Update the description to include additional effects
            effects_text = ", ".join(additional_effects)
            modified_spell['description'] += f" Additionally, it {effects_text}."
        
        # Apply power boost
        if 'power_boost' in custom_modifiers:
            power_boost = custom_modifiers['power_boost']
            if not isinstance(power_boost, (int, float)):
                raise InvalidParameterError(
                    f"Power boost must be a number, got {type(power_boost).__name__}. "
                    f"Please provide a percentage value (e.g., 25 for 25% boost)."
                )
                
            # Add power boost to the spell
            modified_spell['power_boost'] = power_boost
            
            # Optionally adjust the level based on power boost
            if power_boost > 0:
                # Don't exceed maximum level (10)
                modified_spell['level'] = min(10, modified_spell['level'] + int(power_boost / 25))
                
            # Update the description
            modified_spell['description'] += f" The spell's power is boosted by {power_boost}%."
        
        # Apply special properties
        if 'special_properties' in custom_modifiers:
            special_properties = custom_modifiers['special_properties']
            if not isinstance(special_properties, list):
                special_properties = [special_properties]
                
            # Add special properties to the spell
            if 'special_properties' not in modified_spell:
                modified_spell['special_properties'] = []
            modified_spell['special_properties'].extend(special_properties)
            
            # Update the description
            properties_text = ", ".join(special_properties)
            modified_spell['description'] += f" Special properties: {properties_text}."
        
        # Apply custom incantation suffix
        if 'custom_incantation_suffix' in custom_modifiers:
            suffix = custom_modifiers['custom_incantation_suffix']
            modified_spell['incantation'] += f" {suffix}"
        
        # Apply description enhancement
        if 'description_enhancement' in custom_modifiers:
            enhancement = custom_modifiers['description_enhancement']
            modified_spell['description'] += f" {enhancement}"
        
        # Apply any other custom modifiers that aren't handled specifically
        for key, value in custom_modifiers.items():
            if key not in ['additional_effects', 'power_boost', 'special_properties', 
                          'custom_incantation_suffix', 'description_enhancement']:
                modified_spell[key] = value
        
        return modified_spell

    def debug_spell_structure(self, effect, element):
        """
        Debug function to print the structure of spell descriptions.
        
        Args:
            effect: The effect of the spell
            element: The element of the spell
        """
        descriptions = self.data_loader.get_spell_descriptions()
        print(f'Effect: {effect}, Element: {element}')
        print(f'Descriptions structure: {type(descriptions)}')
        print(f'Descriptions keys: {list(descriptions.keys()) if descriptions else []}')
        
        if "effect_prefix" in descriptions:
            print(f'effect_prefix found in descriptions')
            effect_prefix = descriptions["effect_prefix"]
            print(f'Available effects: {list(effect_prefix.keys())}')
            
            # Check for the effect directly in effect_prefix
            if effect in effect_prefix:
                effect_data = effect_prefix[effect]
                print(f'Effect {effect} found in effect_prefix')
                print(f'Effect structure: {type(effect_data)}')
                print(f'Effect keys: {list(effect_data.keys()) if isinstance(effect_data, dict) else "Not a dictionary"}')
                
                if isinstance(effect_data, dict) and "element_prefix" in effect_data:
                    element_prefix = effect_data["element_prefix"]
                    print(f'Element prefix keys: {list(element_prefix.keys())}')
                    
                    if element in element_prefix:
                        print(f'Element {element} found in element_prefix')
                        element_value = element_prefix[element]
                        print(f'Element value type: {type(element_value)}')
                        print(f'Element value: {element_value}')
                    else:
                        print(f'Element {element} NOT found in element_prefix')
                else:
                    print(f'element_prefix not found in effect data')
            else:
                print(f'Effect {effect} NOT found in effect_prefix')
                
                # Look for effect as a sub-effect in other effects
                print(f'Checking for {effect} as a sub-effect:')
                for parent_effect, parent_data in effect_prefix.items():
                    if isinstance(parent_data, dict) and effect in parent_data:
                        print(f'  Found {effect} in {parent_effect}')
                        sub_effect_data = parent_data[effect]
                        print(f'  Sub-effect structure: {type(sub_effect_data)}')
                        
                        if isinstance(sub_effect_data, dict):
                            print(f'  Sub-effect keys: {list(sub_effect_data.keys())}')
                            
                            # Check if the sub-effect has element_prefix
                            if "element_prefix" in sub_effect_data:
                                sub_element_prefix = sub_effect_data["element_prefix"]
                                print(f'  Sub-effect element_prefix keys: {list(sub_element_prefix.keys())}')
                                
                                if element in sub_element_prefix:
                                    print(f'  Element {element} found in sub-effect element_prefix')
                                    sub_element_value = sub_element_prefix[element]
                                    print(f'  Sub-element value type: {type(sub_element_value)}')
                                    print(f'  Sub-element value: {sub_element_value}')
                                else:
                                    print(f'  Element {element} NOT found in sub-effect element_prefix')
                            # Check if element is directly in the sub-effect
                            elif element in sub_effect_data:
                                print(f'  Element {element} found directly in sub-effect')
                                sub_element_value = sub_effect_data[element]
                                print(f'  Sub-element value type: {type(sub_element_value)}')
                                print(f'  Sub-element value: {sub_element_value}')
                            else:
                                print(f'  Element {element} NOT found in sub-effect')
        else:
            print(f'effect_prefix not found in descriptions')

    def _get_closest_matches(self, input_value: str, valid_options: List[str], limit: int = 3) -> List[str]:
        """
        Find closest matches to the input value from valid options for better error suggestions.
        
        Args:
            input_value: The invalid input value
            valid_options: List of valid options to compare against
            limit: Maximum number of suggestions to return
            
        Returns:
            List of closest matching valid options, up to the specified limit
        """
        if not input_value or not valid_options:
            return []
            
        # Simple distance-based matching
        input_lower = input_value.lower()
        matches = []
        
        # First look for options that start with the input
        prefix_matches = [opt for opt in valid_options if opt.lower().startswith(input_lower)]
        matches.extend(prefix_matches)
        
        # Then look for options that contain the input
        if len(matches) < limit:
            contains_matches = [
                opt for opt in valid_options 
                if opt.lower().find(input_lower) != -1 and opt not in matches
            ]
            matches.extend(contains_matches)
        
        # Return up to the limit number of matches
        return matches[:limit]
