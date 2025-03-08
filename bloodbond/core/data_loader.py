import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, TypedDict, cast, Set
import logging
from functools import lru_cache
import jsonschema
from bloodbond.core.element_mapper import ElementMapper

from bloodbond.core.exceptions import (
    DataError, 
    FileNotFoundError as BBFileNotFoundError, 
    MalformedDataError, 
    InvalidDataError
)


class SpellDataDict(TypedDict):
    bloodline_affinities: Dict[str, Dict[str, float]]
    spoken_spell_table: Dict[str, Any]


class SpellDescriptionsDict(TypedDict):
    spoken_spell_table: Dict[str, Dict[str, str]]


class SynonymsDict(TypedDict):
    effects: Dict[str, List[str]]
    elements: Dict[str, List[str]]
    duration: Dict[str, List[str]]
    range: Dict[str, List[str]]


class TimingPatternsDict(TypedDict):
    instant: Dict[str, Union[List[str], str]]
    one_minute: Dict[str, Union[List[str], str]]
    five_minutes: Dict[str, Union[List[str], str]]
    ten_minutes: Dict[str, Union[List[str], str]]
    thirty_minutes: Dict[str, Union[List[str], str]]
    one_hour: Dict[str, Union[List[str], str]]
    eight_hours: Dict[str, Union[List[str], str]]
    one_day: Dict[str, Union[List[str], str]]
    seven_days: Dict[str, Union[List[str], str]]
    until_dismissed: Dict[str, Union[List[str], str]]
    permanent: Dict[str, Union[List[str], str]]


class DataLoader:
    """
    A class for loading and providing access to JSON data files used in the Blood Bond system.
    
    This class handles loading spell data, spell descriptions, synonyms, and timing patterns
    from JSON files. It includes error handling and caching for better performance.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the DataLoader with a specific data directory.
        
        Args:
            data_dir: Path to the directory containing JSON data files.
                     If None, defaults to the 'data' directory in the package.
        """
        self.logger = logging.getLogger(__name__)
        
        if data_dir is None:
            # Default to the 'data' directory in the package
            self.data_dir = Path(__file__).parent.parent / 'data'
        else:
            self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        self.spell_data_path = self.data_dir / 'spell_data.json'
        self.spell_descriptions_path = self.data_dir / 'spell_descriptions.json'
        self.synonyms_path = self.data_dir / 'synonyms.json'
        self.timing_patterns_path = self.data_dir / 'timing_patterns.json'
        self.compatibility_path = self.data_dir / 'Standardized_Compatibility.json'
        
        # Validate that all required files exist
        self._validate_file_paths()
        
        # Cache for loaded data
        self._cache: Dict[str, Any] = {}

    def _validate_file_paths(self) -> None:
        """Validate that all required data files exist."""
        required_files = [
            (self.spell_data_path, "Spell data"),
            (self.spell_descriptions_path, "Spell descriptions"),
            (self.synonyms_path, "Synonyms"),
            (self.timing_patterns_path, "Timing patterns"),
            (self.compatibility_path, "Standardized Compatibility")
        ]
        
        for file_path, file_desc in required_files:
            if not file_path.exists():
                self.logger.error(f"{file_desc} file not found: {file_path}")
                raise FileNotFoundError(f"{file_desc} file not found: {file_path}")

    def _load_json_file(self, file_path: Path) -> Any:
        """
        Load and parse a JSON file with error handling.
        
        Args:
            file_path: Path to the JSON file.
            
        Returns:
            Parsed JSON data.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            raise

    @lru_cache(maxsize=1)
    def load_spell_data(self) -> SpellDataDict:
        """
        Load spell data from the spell_data.json file.
        
        Returns:
            Dictionary containing bloodline affinities and spoken spell table.
        """
        if 'spell_data' not in self._cache:
            self.logger.info(f"Loading spell data from {self.spell_data_path}")
            self._cache['spell_data'] = self._load_json_file(self.spell_data_path)
        
        return cast(SpellDataDict, self._cache['spell_data'])

    @lru_cache(maxsize=1)
    def load_spell_descriptions(self) -> SpellDescriptionsDict:
        """
        Load spell descriptions from the spell_descriptions.json file.
        
        Returns:
            Dictionary containing spoken spell descriptions.
        """
        if 'spell_descriptions' not in self._cache:
            self.logger.info(f"Loading spell descriptions from {self.spell_descriptions_path}")
            self._cache['spell_descriptions'] = self._load_json_file(self.spell_descriptions_path)
        
        return cast(SpellDescriptionsDict, self._cache['spell_descriptions'])

    @lru_cache(maxsize=1)
    def load_synonyms(self) -> SynonymsDict:
        """
        Load synonyms from the synonyms.json file.
        
        Returns:
            Dictionary containing synonyms for effects, elements, duration, and range.
        """
        if 'synonyms' not in self._cache:
            self.logger.info(f"Loading synonyms from {self.synonyms_path}")
            self._cache['synonyms'] = self._load_json_file(self.synonyms_path)
        
        return cast(SynonymsDict, self._cache['synonyms'])

    @lru_cache(maxsize=1)
    def load_timing_patterns(self) -> TimingPatternsDict:
        """
        Load timing patterns from the timing_patterns.json file.
        
        Returns:
            Dictionary containing regex patterns for different durations.
        """
        if 'timing_patterns' not in self._cache:
            self.logger.info(f"Loading timing patterns from {self.timing_patterns_path}")
            self._cache['timing_patterns'] = self._load_json_file(self.timing_patterns_path)
        
        return cast(TimingPatternsDict, self._cache['timing_patterns'])

    @lru_cache(maxsize=1)
    def load_compatibility_data(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        """
        Load bloodline compatibility data from the Standardized_Compatibility.json file.
        
        Returns:
            Dictionary containing bloodline compatibility data.
        """
        if 'compatibility_data' not in self._cache:
            self.logger.info(f"Loading compatibility data from {self.compatibility_path}")
            self._cache['compatibility_data'] = self._load_json_file(self.compatibility_path)
        
        return self._cache['compatibility_data']

    def get_bloodline_affinities(self) -> Dict[str, Dict[str, float]]:
        """
        Get bloodline affinities from the spell data.
        
        Returns:
            Dictionary mapping bloodlines to their element affinities.
        """
        # For backward compatibility, still return from spell_data.json
        spell_data = self.load_spell_data()
        return spell_data['bloodline_affinities']
        
    def get_bloodline_element_compatibility(self, bloodline: str, element: str) -> float:
        """
        Calculate the compatibility percentage between a bloodline and an element.
        
        Uses the Standardized_Compatibility.json file as the source of truth for compatibility values.
        
        Args:
            bloodline: The name of the bloodline (e.g., 'Moon', 'Water')
            element: The name of the element (e.g., 'Fire', 'Love')
            
        Returns:
            Compatibility percentage as a float between 0 and 100.
            Returns 0 if the bloodline or element doesn't exist, or if they have no affinity.
        """
        try:
            # Load the standardized compatibility data
            compatibility_data = self.load_compatibility_data()
            
            # Check if the "Blood line" key exists
            if "Blood line" not in compatibility_data:
                self.logger.warning(f"'Blood line' key not found in compatibility data")
                return 0.0
            
            bloodlines = compatibility_data["Blood line"]
            
            # Check if the bloodline exists
            if bloodline not in bloodlines:
                self.logger.warning(f"Bloodline '{bloodline}' not found in compatibility data")
                return 0.0
            
            # Get the categories for this bloodline
            bloodline_data = bloodlines[bloodline]
            
            # Special case for Sun bloodline with "All" elements
            if bloodline == "Sun" and element != "Sun":
                for category, elements in bloodline_data.items():
                    if "All" in elements:
                        import re
                        percentage_match = re.search(r'(\d+)%', category)
                        if percentage_match:
                            return float(percentage_match.group(1))
            
            # Iterate through each category to find the element
            for category, elements in bloodline_data.items():
                try:
                    # Find the percentage in the category string
                    import re
                    percentage_match = re.search(r'(\d+)%', category)
                    if percentage_match:
                        percentage = float(percentage_match.group(1))
                        
                        # Check if the element is in this category
                        if element in elements:
                            return percentage
                except Exception as e:
                    self.logger.error(f"Error parsing category '{category}': {e}")
            
            # If we get here, the element wasn't found in any category
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating compatibility for {bloodline}/{element}: {e}")
            return 0.0

    def get_spoken_spell_components(self) -> Dict[str, Any]:
        """
        Get the spoken spell components from the spell data.
        
        Returns:
            Dictionary containing effect prefixes, element prefixes, etc.
        """
        spell_data = self.load_spell_data()
        return spell_data['spoken_spell_table']

    def get_spoken_spell_table(self) -> Dict[str, Any]:
        """
        Get the spoken spell table from the spell data.
        This is a wrapper around get_spoken_spell_components for backward compatibility.
        
        Returns:
            Dictionary containing effect prefixes, element prefixes, etc.
        """
        return self.get_spoken_spell_components()

    def get_spell_data(self) -> SpellDataDict:
        """
        Get the full spell data dictionary.
        
        Returns:
            Dictionary containing all spell data including bloodline affinities and spoken spell components.
        """
        return self.load_spell_data()

    def get_spell_description(self, effect: str, element: str) -> Optional[str]:
        """
        Get a spell description for a specific effect and element combination.
        
        Args:
            effect: The spell effect (e.g., 'Creation', 'Damage')
            element: The spell element (e.g., 'Fire', 'Water')
            
        Returns:
            Description string if found, None otherwise.
        """
        try:
            descriptions = self.load_spell_descriptions()
            return descriptions['spoken_spell_table'].get(effect, {}).get(element)
        except Exception as e:
            self.logger.error(f"Error getting spell description for {effect}/{element}: {e}")
            return None

    def get_synonyms_for_category(self, category: str) -> Dict[str, List[str]]:
        """
        Get synonyms for a specific category.
        
        Args:
            category: One of 'effects', 'elements', 'duration', or 'range'.
            
        Returns:
            Dictionary mapping terms to their synonyms.
            
        Raises:
            ValueError: If the category is invalid.
        """
        valid_categories = ['effects', 'elements', 'duration', 'range']
        if category not in valid_categories:
            raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")
        
        synonyms = self.load_synonyms()
        return synonyms.get(category, {})

    def get_timing_pattern(self, duration_type: str) -> Optional[Dict[str, Union[List[str], str]]]:
        """
        Get timing pattern information for a specific duration type.
        
        Args:
            duration_type: One of the supported duration types 
                          (e.g., 'instant', 'one_minute', 'one_hour')
            
        Returns:
            Dictionary with pattern and examples if found, None otherwise.
        """
        timing_patterns = self.load_timing_patterns()
        
        # Use get() to avoid KeyError for missing keys
        return timing_patterns.get(duration_type)

    def clear_cache(self) -> None:
        """Clear the data cache, forcing fresh loads on next access."""
        self.logger.info("Clearing data cache")
        self._cache.clear()
        
        # Also clear the lru_cache for the loading methods
        self.load_spell_data.cache_clear()
        self.load_spell_descriptions.cache_clear()
        self.load_synonyms.cache_clear()
        self.load_timing_patterns.cache_clear()
        self.load_compatibility_data.cache_clear()

    def reload_all_data(self) -> None:
        """Force reload of all data files."""
        self.clear_cache()
        self.load_spell_data()
        self.load_spell_descriptions()
        self.load_synonyms()
        self.load_timing_patterns()
        self.load_compatibility_data()
        self.logger.info("All data reloaded successfully")

    def get_spell_effects(self) -> List[str]:
        """
        Get a list of available spell effects from the spoken spell table.
        
        Returns:
            List of effect names (keys from the effect_prefixes dictionary).
        """
        spell_components = self.get_spoken_spell_components()
        return list(spell_components.get('effect_prefix', {}).keys())

    def get_spell_elements(self) -> List[str]:
        """
        Get a list of available spell elements from the spoken spell table.
        
        Returns:
            List of element names (keys from the element_prefixes dictionary)
            that are standardized according to Standardized_Compatibility.json.
        """
        # Get all elements from the spell components
        spell_components = self.get_spoken_spell_components()
        all_elements = list(spell_components.get('element_prefix', {}).keys())
        
        # Get the standardized elements from the compatibility data
        standardized_elements: Set[str] = set()
        try:
            compatibility_data = self.load_compatibility_data()
            if "Blood line" in compatibility_data:
                bloodlines = compatibility_data["Blood line"]
                
                # Collect all standardized elements from the compatibility data
                for bloodline, categories in bloodlines.items():
                    for category, elements in categories.items():
                        standardized_elements.update(elements)
                
                # Remove "All" if it exists since it's a special marker, not an actual element
                if "All" in standardized_elements:
                    standardized_elements.remove("All")
                
                self.logger.debug(f"Standardized elements: {standardized_elements}")
        except Exception as e:
            self.logger.error(f"Error loading standardized elements: {e}")
        
        # Filter elements to only include those in the standardized list
        filtered_elements = [elem for elem in all_elements if elem in standardized_elements]
        
        if len(filtered_elements) < len(all_elements):
            self.logger.info(f"Filtered out {len(all_elements) - len(filtered_elements)} non-standardized elements")
        
        return filtered_elements

    def get_spell_descriptions(self) -> Dict[str, Dict[str, str]]:
        """
        Get the spoken spell descriptions from the spell_descriptions.json file.
        
        Returns:
            Dictionary containing the spoken spell descriptions organized by effect and element.
        """
        descriptions = self.load_spell_descriptions()
        return descriptions['spoken_spell_table']

