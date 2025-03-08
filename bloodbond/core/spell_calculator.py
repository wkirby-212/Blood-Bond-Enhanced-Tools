"""
Spell Calculator for Blood Bond TTRPG Magic System.

This module provides functionality for calculating spell damage, effectiveness,
and handling special casting methods according to the Blood Bond TTRPG rules.
"""

import random
import json
import os
from typing import Dict, List, Tuple, Union

class SpellCalculator:
    """
    A calculator for Blood Bond TTRPG spell mechanics.
    
    This class handles the core spell calculations including damage, 
    effectiveness based on bloodline compatibility, and special casting methods.
    """
    
    # Standard class dice values
    CLASS_DICE = {
        "novice": 4,
        "apprentice": 6, 
        "adept": 8,
        "expert": 10,
        "master": 12
    }
    # Mapping between compatibility categories and percentage values
    COMPATIBILITY_CATEGORIES = {
        "Perfect 100%": 100,
        "Best 80%": 80,
        "Good 60%": 60,
        "Moderate 40%": 40,
        "Weak 20%": 20,
        "Neutral 50%": 50
    }
    
    def __init__(self):
        """Initialize the SpellCalculator and load compatibility data from JSON file."""
        self.compatibility_data = self._load_compatibility_data()

    def _load_compatibility_data(self) -> Dict:
        """
        Load and parse the compatibility data from the Standardized_Compatibility.json file.
        
        Returns:
            Dictionary containing bloodline compatibility data in the format:
            {bloodline: {element: percentage}}
        """
        compatibility_map = {}
        try:
            # Construct path to the Standardized_Compatibility.json file
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    "data", "Standardized_Compatibility.json")
            
            # Load the JSON data
            with open(file_path, 'r') as file:
                json_data = json.load(file)
            
            # Extract data from the "Blood line" section of the JSON
            bloodlines_data = json_data.get("Blood line", {})
            
            # Process each bloodline
            for bloodline, categories in bloodlines_data.items():
                bloodline_lower = bloodline.lower()
                compatibility_map[bloodline_lower] = {}
                
                # For each category (Perfect 100%, Best 80%, etc.)
                for category, elements in categories.items():
                    percentage = self.COMPATIBILITY_CATEGORIES.get(category, 50)
                    
                    # Handle the special case of "All" elements for the Sun bloodline
                    if 'All' in elements:
                        for element in ["moon", "wind", "water", "fire", "earth", 
                                        "death", "protection", "love", "song"]:
                            compatibility_map[bloodline_lower][element] = percentage
                    else:
                        # Add each element with its percentage value
                        for element in elements:
                            compatibility_map[bloodline_lower][element.lower()] = percentage
                
                # Make sure the bloodline is compatible with itself at 100%
                compatibility_map[bloodline_lower][bloodline_lower] = 100
            
            return compatibility_map
        except Exception as e:
            print(f"Error loading compatibility data: {str(e)}")
            # Return an empty dictionary to avoid errors
            return {}
    
    def calculate_damage(self, caster, spell_level: int, element: str, godly_blessing_percent: int) -> int:
        """
        Calculate spell damage using the Blood Bond formula.
        
        Damage = (Class Die × Spell Level) + Magical Affinity + Godly Blessing Percentage
        
        Args:
            caster: Object representing the spell caster with attributes class_die, magical_affinity, etc.
            spell_level: Level of the spell being cast (1-10)
            element: The elemental type of the spell
            godly_blessing_percent: Percentage bonus from godly blessing
            
        Returns:
            The calculated damage value
        """
        # Get the die value from the caster
        class_die = getattr(caster, 'class_die', 6)  # Default to d6 if not found
        
        # Get magical affinity from the caster
        magical_affinity = getattr(caster, 'magical_affinity', 0)  # Default to 0 if not found
        
        # Roll the class die for each spell level
        base_damage = 0
        for _ in range(spell_level):
            base_damage += random.randint(1, class_die)
        
        # Add magical affinity
        total_damage = base_damage + magical_affinity
        
        # Check elemental compatibility if caster has a bloodline attribute AND the bloodline is not None
        if hasattr(caster, 'bloodline') and caster.bloodline is not None:
            effectiveness = self.calculate_effectiveness(caster.bloodline, element)
            total_damage = int(total_damage * effectiveness)
        
        # Apply godly blessing as a percentage
        blessing_bonus = int(base_damage * godly_blessing_percent / 100)
        total_damage += blessing_bonus
        
        return max(1, total_damage)  # Minimum damage of 1
    
    def calculate_effectiveness(self, caster_element: str, spell_element: str) -> float:
        """
        Calculate the effectiveness of a spell based on bloodline compatibility.
        
        Args:
            caster_element: The elemental bloodline of the caster
            spell_element: The elemental type of the spell
            
        Returns:
            Effectiveness as a float between 0.0 and 1.0
        """
        # Define standardized elements list
        standardized_elements = ["moon", "water", "wind", "earth", "death", "fire", "protection", "love", "song", "sun"]
        
        # Return default compatibility value if either element is None
        if caster_element is None or spell_element is None:
            print(f"DEBUG: One or both elements are None. caster_element={caster_element}, spell_element={spell_element}")
            return 0.5
            
        # Normalize inputs to lowercase
        caster_element = caster_element.lower()
        spell_element = spell_element.lower()
        
        # Validate elements against standardized list
        if caster_element not in standardized_elements:
            print(f"WARNING: Caster element '{caster_element}' is not in the standardized elements list. Returning 0% compatibility.")
            return 0.0
            
        if spell_element not in standardized_elements:
            print(f"WARNING: Spell element '{spell_element}' is not in the standardized elements list. Returning 0% compatibility.")
            return 0.0
        
        # DEBUG: Print the elements being used
        print(f"DEBUG: Calculating effectiveness for bloodline={caster_element}, element={spell_element}")
        
        # Get compatibility value or default to 50% if not found
        compatibility = self.compatibility_data.get(caster_element, {}).get(spell_element, 50)
        
        # DEBUG: Print the compatibility value found
        print(f"DEBUG: Found compatibility value: {compatibility}%")
        
        # Check if this bloodline exists in the compatibility data
        if caster_element not in self.compatibility_data:
            print(f"DEBUG: WARNING! Bloodline '{caster_element}' not found in compatibility data!")
        # Check if we're using the default value (50) because the element wasn't found
        elif spell_element not in self.compatibility_data.get(caster_element, {}):
            print(f"DEBUG: WARNING! Element '{spell_element}' not found for bloodline '{caster_element}'! Using default value 50%")
        
        # Find the expected compatibility category for debugging
        expected_category = None
        for category, elements in self.COMPATIBILITY_CATEGORIES.items():
            if compatibility == elements:
                expected_category = category
                break
        
        # DEBUG: Print the category information
        if expected_category:
            print(f"DEBUG: This is a '{expected_category}' compatibility")
        else:
            print(f"DEBUG: WARNING! Compatibility value {compatibility}% does not match any standard category!")
            print(f"DEBUG: Standard categories: {self.COMPATIBILITY_CATEGORIES}")
        
        # Return as a float between 0.0 and 1.0
        return compatibility / 100.0
    
    def particast(self, caster, element: str, difficulty: int) -> Dict[str, Union[bool, int, float]]:
        """
        Calculate the results of a particast (ambient magic).
        
        Args:
            caster: Object representing the spell caster with attributes bloodline, magical_affinity
            element: The elemental type of the spell
            difficulty: The difficulty level of the particast
            
        Returns:
            Dictionary containing 'success', 'effect_strength', 'duration', 'difficulty', and 'compatibility' values
        """
        # Extract caster element from caster's bloodline
        caster_element = getattr(caster, 'bloodline', 'wind')  # Default to wind if no bloodline
        # If bloodline attribute exists but is None, use 'wind' as default
        if caster_element is None:
            caster_element = 'wind'
        # Extract magical affinity from caster
        magical_affinity = getattr(caster, 'magical_affinity', 0)  # Default to 0 if not found
        
        # Get effectiveness based on compatibility
        effectiveness = self.calculate_effectiveness(caster_element, element)
        
        # Calculate success chance (higher effectiveness = higher chance)
        success_chance = 0.4 + (effectiveness * 0.4) + (magical_affinity * 0.02)
        success_chance = min(0.9, success_chance)  # Cap at 90%
        
        # Determine success
        success = random.random() < success_chance
        
        if success:
            # Calculate reduced effect value for particast
            effect_strength = random.randint(1, 4) + (magical_affinity // 2)
            effect_strength = int(effect_strength * effectiveness)
            # Calculate duration based on difficulty
            duration = difficulty // 2 + 1
        else:
            effect_strength = 0
            duration = 0
        
        return {
            'success': success,
            'effect_strength': effect_strength,
            'duration': duration,
            'difficulty': difficulty,
            'compatibility': effectiveness
        }
    
    def elemental_fusion(self, caster, primary_element: str, secondary_element: str,
                        spell_level: int) -> Dict[str, Union[int, float, bool]]:
        """
        Calculate the results of a fusion between two elements.
        
        Args:
            caster: Object representing the spell caster with attributes class_die, magical_affinity, etc.
            primary_element: The primary element being used
            secondary_element: The secondary element being fused
            spell_level: Level of the spell being cast
            
        Returns:
            Dictionary containing 'base_damage', 'fusion_bonus', 'total_damage', and 'compatibility' values
        """
        # Extract magical affinity from caster
        magical_affinity = getattr(caster, 'magical_affinity', 0)  # Default to 0 if not found
        
        # Check compatibility between elements
        compatibility = self.calculate_effectiveness(primary_element, secondary_element)
        
        # Fusion requires decent compatibility
        if compatibility < 0.3:
            return {
                'base_damage': 0,
                'fusion_bonus': 0,
                'total_damage': 0,
                'compatibility': compatibility
            }
        
        # Calculate success chance
        success_chance = 0.3 + (compatibility * 0.5) + (magical_affinity * 0.02)
        success_chance = min(0.9, success_chance)  # Cap at 90%
        
        # Determine success
        success = random.random() < success_chance
        
        if success:
            # Calculate base effect
            primary_effect = random.randint(1, 6) * spell_level
            secondary_effect = random.randint(1, 4) * spell_level
            
            # Base damage is from primary element
            base_damage = primary_effect
            
            # Fusion bonus comes from secondary element and magical affinity
            fusion_bonus = secondary_effect + magical_affinity
            
            # Calculate total damage before compatibility modifier
            combined_effect = base_damage + fusion_bonus
            
            # Apply compatibility modifier
            total_damage = int(combined_effect * compatibility)
            
            return {
                'base_damage': base_damage,
                'fusion_bonus': fusion_bonus,
                'total_damage': total_damage,
                'compatibility': compatibility
            }
        else:
            # Fusion failed
            return {
                'base_damage': 0,
                'fusion_bonus': 0,
                'total_damage': 0,
                'compatibility': compatibility
            }

    def get_bloodline_compatibility(self, bloodline: str, element: str) -> int:
        """
        Calculate the compatibility between a bloodline and an element.
        
        Args:
            bloodline: The bloodline to check
            element: The elemental type
            
        Returns:
            Compatibility as a percentage (0-100)
        """
        # Use calculate_effectiveness method to get compatibility as a float (0.0-1.0)
        effectiveness = self.calculate_effectiveness(bloodline, element)
        
        # Convert to percentage (0-100) and round to nearest integer
        compatibility_percentage = round(effectiveness * 100)
        
        return compatibility_percentage
    
    def get_effective_spell_level(self, caster, element: str, base_level: int) -> int:
        """
        Calculate the effective spell level based on bloodline compatibility.
        
        The effective level is adjusted based on:
        - Element preferences and restrictions
        - Bloodline compatibility with the element
        
        Args:
            caster: Object representing the spell caster
            element: The elemental type of the spell
            base_level: The base level of the spell
            
        Returns:
            The effective spell level (1-10)
        """
        # Start with the base level
        effective_level = base_level
        
        # Check if caster has preferred_elements attribute
        if hasattr(caster, 'preferred_elements'):
            preferred = getattr(caster, 'preferred_elements', [])
            # If element is in preferred elements, increase level by 1
            if element.lower() in {e.lower() for e in preferred}:
                effective_level += 1
        # Check if caster has restricted_elements attribute
        if hasattr(caster, 'restricted_elements'):
            restricted = getattr(caster, 'restricted_elements', [])
            # If element is in restricted elements, decrease level by 1
            if element.lower() in {e.lower() for e in restricted}:
                effective_level -= 1
                
        # Check bloodline compatibility
        if hasattr(caster, 'bloodline') and caster.bloodline is not None:
            compatibility = self.calculate_effectiveness(caster.bloodline, element)
            
            # Boost for high compatibility
            if compatibility > 0.8:
                effective_level += 1
                
            # Penalty for low compatibility
            if compatibility < 0.3:
                effective_level -= 1
                
        # Ensure level stays within valid range (1-10)
        effective_level = max(1, min(effective_level, 10))
        
        return effective_level

    def ritual_casting(self, leader, participants: List, target_element: str, 
                     spell_level: int, ritual_difficulty: int) -> Dict[str, Union[bool, int, float]]:
        """
        Simulate a group ritual casting.
        
        Args:
            leader: The ritual leader (a caster object)
            participants: List of participant casters
            target_element: The elemental type of the ritual
            spell_level: The base level of the spell (1-10)
            ritual_difficulty: The difficulty of the ritual (1-10)
            
        Returns:
            Dictionary containing success, base_power, participant_bonus, total_power, duration, and range values
        """
        # Get leader's level and magical affinity
        leader_level = getattr(leader, 'level', 1)  # Default to level 1 if not found
        magical_affinity = getattr(leader, 'magical_affinity', 0)  # Default to 0 if not found
        
        # Calculate base power
        base_power = (leader_level * spell_level) + magical_affinity
        
        # Check if leader has the target element in preferred elements
        if hasattr(leader, 'preferred_elements'):
            preferred = getattr(leader, 'preferred_elements', set())
            if target_element.lower() in {e.lower() for e in preferred}:
                base_power += 10
        
        # Calculate participant bonus
        participant_bonus = 0
        for participant in participants:
            # Get participant's level
            participant_level = getattr(participant, 'level', 1)  # Default to level 1
            participant_bonus += participant_level / 2
            
            # Check if participant has the target element in preferred elements
            if hasattr(participant, 'preferred_elements'):
                preferred = getattr(participant, 'preferred_elements', set())
                if target_element.lower() in {e.lower() for e in preferred}:
                    participant_bonus += 2
        
        # Calculate total power
        total_power = base_power + participant_bonus
        
        # Determine success
        success = total_power > (ritual_difficulty * 10)
        
        # Calculate duration and range
        if success:
            duration = int(total_power / 10)  # Hours, rounded down
            range_value = total_power * 2     # Units
        else:
            duration = 0
            range_value = 0
        
        # Return the result dictionary
        return {
            'success': success,
            'base_power': base_power,
            'participant_bonus': participant_bonus,
            'total_power': total_power,
            'duration': duration,
            'range': range_value
        }

