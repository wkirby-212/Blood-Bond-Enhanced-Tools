#!/usr/bin/env python3
"""
Element Mapper Module

This module provides functionality for mapping elements between different naming systems,
such as converting "Wind" to "Air" or finding the closest match based on string similarity.
It is part of the Blood Bond Enhanced Tools suite, a Python port of the original PowerShell
project.

Classes:
    ElementMapper: Maps elements between different naming systems with direct mapping and
                  string similarity matching.
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Optional, Union, Any, Set
import difflib

# Optional import for better performance
try:
    import rapidfuzz
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


class ElementMapper:
    """
    Maps elements between different naming systems with direct mapping and string similarity.
    
    This class provides functionality to convert elements between different naming conventions,
    such as mapping "Wind" to "Air" or "Moon" to "Light". For elements without a direct mapping,
    it uses string similarity algorithms to find the best match.
    
    Attributes:
        direct_mappings (Dict[str, str]): Dictionary of known direct element mappings.
        source_elements (List[str]): List of valid source elements.
        target_elements (List[str]): List of valid target elements.
        similarity_threshold (float): Minimum similarity score required for a match (0.0-1.0).
        use_rapidfuzz (bool): Whether to use the rapidfuzz library for similarity matching.
        
    Examples:
        >>> mapper = ElementMapper()
        >>> mapper.map_element("Water")
        'Water'
        >>> mapper.map_element("Moon")
        'Moon'
        >>> mapper.find_closest_match("Firey", ["Fire", "Water", "Earth"])
        ('Fire', 0.8)
    """
    
    def __init__(self, 
                 direct_mappings: Optional[Dict[str, str]] = None,
                 source_elements: Optional[List[str]] = None,
                 target_elements: Optional[List[str]] = None,
                 similarity_threshold: float = 0.7,
                 use_rapidfuzz: bool = RAPIDFUZZ_AVAILABLE,
                 compatibility_file_path: Optional[str] = None):
        """
        Initialize the ElementMapper with direct mappings and element lists.
        
        Args:
            direct_mappings: Dictionary mapping source elements to target elements.
                             If None, only standardized elements will be used.
            source_elements: List of valid source elements. If None, standardized elements will be used.
            target_elements: List of valid target elements. If None, standardized elements will be used.
            similarity_threshold: Minimum similarity score (0.0-1.0) for a match.
            use_rapidfuzz: Whether to use the rapidfuzz library for similarity matching.
                           Defaults to True if the library is available.
            compatibility_file_path: Path to the Standardized_Compatibility.json file.
                                     If None, a default path will be used.
        """
        self.logger = logging.getLogger(__name__)
        
        # Load standardized elements from compatibility file
        self.standardized_elements = self._load_standardized_elements(compatibility_file_path)
        self.logger.debug(f"Loaded {len(self.standardized_elements)} standardized elements")
        
        # Use only standardized elements for mappings
        self.direct_mappings = {}
        
        # Initialize source and target elements with standardized elements
        self.source_elements = source_elements or list(self.standardized_elements)
        self.target_elements = target_elements or list(self.standardized_elements)
        
        # Ensure both source and target elements contain only standardized elements
        self.source_elements = [element for element in self.source_elements if element in self.standardized_elements]
        self.target_elements = [element for element in self.target_elements if element in self.standardized_elements]
        
        self.similarity_threshold = similarity_threshold
        self.use_rapidfuzz = use_rapidfuzz and RAPIDFUZZ_AVAILABLE
        
        self.logger.debug(f"ElementMapper initialized with standardized elements: {', '.join(self.standardized_elements)}")
        self.logger.debug(f"Using RapidFuzz: {self.use_rapidfuzz}")
    
    def map_element(self, element: str) -> str:
        """
        Map an element to its equivalent in the target system.
        
        First tries direct mapping, then falls back to string similarity matching
        if no direct mapping is found.
        
        Args:
            element: The source element to map.
            
        Returns:
            The mapped element in the target system.
            
        Examples:
            >>> mapper = ElementMapper()
            >>> mapper.map_element("Water")
            'Water'
        """
        # Try direct mapping first
        if element in self.direct_mappings:
            mapped = self.direct_mappings[element]
            self.logger.debug(f"Direct mapping: {element} -> {mapped}")
            return mapped
        
        # Try reverse mapping
        reverse_mappings = {v: k for k, v in self.direct_mappings.items()}
        if element in reverse_mappings:
            mapped = reverse_mappings[element]
            self.logger.debug(f"Reverse mapping: {element} -> {mapped}")
            return mapped
        
        # If no direct mapping, use string similarity to find closest match
        closest_match, similarity = self.find_closest_match(element, self.target_elements)
        
        if similarity >= self.similarity_threshold:
            self.logger.debug(f"Similarity mapping: {element} -> {closest_match} (score: {similarity:.2f})")
            return closest_match
        
        # If no good match is found, return the original element
        # If no good match is found, log a warning and return a default element if it's not in standardized elements
        if element not in self.standardized_elements:
            default_element = next(iter(self.standardized_elements), element)
            self.logger.warning(f"No suitable mapping found for '{element}'. It's not a standardized element. Using '{default_element}' instead.")
            return default_element
        
        # If it's already a standardized element, return it as-is
        return element
    
    def find_closest_match(self, query: str, candidates: List[str]) -> Tuple[str, float]:
        """
        Find the closest matching element from a list of candidates using string similarity.
        
        Args:
            query: The element name to find a match for.
            candidates: List of possible matching elements.
            
        Returns:
            A tuple containing (best_match, similarity_score).
            
        Examples:
            >>> mapper = ElementMapper()
            >>> mapper.find_closest_match("Firey", ["Fire", "Water", "Earth"])
            ('Fire', 0.8)
        """
        if not candidates:
            self.logger.warning("No candidates provided for matching")
            return query, 0.0
        
        if query in candidates:
            return query, 1.0
        
        # Use rapidfuzz if available and enabled, otherwise use difflib
        if self.use_rapidfuzz:
            # Process Extraction returns list of tuples (match, score, index)
            matches = rapidfuzz.process.extract(
                query, 
                candidates, 
                scorer=fuzz.ratio,
                limit=1
            )
            best_match, score = matches[0][0], matches[0][1] / 100.0
        else:
            # Get similarity ratios using difflib
            similarities = [(candidate, difflib.SequenceMatcher(None, query.lower(), candidate.lower()).ratio()) 
                           for candidate in candidates]
            best_match, score = max(similarities, key=lambda x: x[1])
        
        self.logger.debug(f"Closest match for '{query}': '{best_match}' (score: {score:.2f})")
        return best_match, score
    def add_mapping(self, source: str, target: str) -> None:
        """
        Add a new direct mapping between elements.
        Only adds mapping if both elements are standardized elements.
        
        Args:
            source: The source element name.
            target: The target element name.
        """
        # Only add mapping if both elements are standardized
        if source in self.standardized_elements and target in self.standardized_elements:
            self.direct_mappings[source] = target
            
            # Ensure both elements are in the source and target lists
            if source not in self.source_elements:
                self.source_elements.append(source)
            if target not in self.target_elements:
                self.target_elements.append(target)
                
            self.logger.debug(f"Added mapping: {source} -> {target}")
        else:
            non_standard = []
            if source not in self.standardized_elements:
                non_standard.append(source)
            if target not in self.standardized_elements:
                non_standard.append(target)
            self.logger.warning(f"Cannot add mapping with non-standardized elements: {', '.join(non_standard)}")
        self.logger.debug(f"Added mapping: {source} -> {target}")
    
    def remove_mapping(self, source: str) -> bool:
        """
        Remove a direct mapping for the given source element.
        
        Args:
            source: The source element to remove mapping for.
            
        Returns:
            True if mapping was removed, False if not found.
        """
        if source in self.direct_mappings:
            del self.direct_mappings[source]
            self.logger.debug(f"Removed mapping for: {source}")
            return True
        
        self.logger.debug(f"No mapping found to remove for: {source}")
        return False
    
    def get_all_mappings(self) -> Dict[str, str]:
        """
        Get all direct mappings as a dictionary.
        
        Returns:
            Dictionary of all source->target element mappings.
        """
        return self.direct_mappings.copy()
    
    def load_mappings_from_file(self, filepath: str) -> bool:
        """
        Load element mappings from a JSON file.
        
        Args:
            filepath: Path to the JSON file containing mappings.
            
        Returns:
            True if loaded successfully, False otherwise.
            
        The JSON file should have a format like:
        {
            "element_mappings": {
                "Moon": "Sun",
                "Water": "Earth",
                ...
            }
        }
        """
        try:
            if not os.path.exists(filepath):
                self.logger.error(f"Mapping file not found: {filepath}")
                return False
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "element_mappings" not in data:
                self.logger.error(f"Invalid mapping file format: {filepath}")
                return False
            
            # Filter out any non-standardized elements from mappings
            filtered_mappings = {}
            for source, target in data["element_mappings"].items():
                if source in self.standardized_elements and target in self.standardized_elements:
                    filtered_mappings[source] = target
                else:
                    self.logger.warning(f"Skipping non-standard element mapping: {source} -> {target}")
            
            self.direct_mappings = filtered_mappings
            
            # Update source and target elements (ensuring they remain standardized)
            self.source_elements = [elem for elem in list(self.direct_mappings.keys()) if elem in self.standardized_elements]
            self.target_elements = [elem for elem in list(self.direct_mappings.values()) if elem in self.standardized_elements]
            
            self.logger.info(f"Loaded {len(self.direct_mappings)} mappings from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading mappings from {filepath}: {str(e)}")
            return False
    
    def save_mappings_to_file(self, filepath: str) -> bool:
        """
        Save current element mappings to a JSON file.
        
        Args:
            filepath: Path to save the JSON file.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({"element_mappings": self.direct_mappings}, f, indent=4)
            
            self.logger.info(f"Saved {len(self.direct_mappings)} mappings to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving mappings to {filepath}: {str(e)}")
            return False
    
    def batch_map_elements(self, elements: List[str]) -> Dict[str, str]:
        """
        Map multiple elements at once.
        
        Args:
            elements: List of source elements to map.
            
        Returns:
            Dictionary mapping each source element to its target element.
        """
        return {element: self.map_element(element) for element in elements}

    def _load_standardized_elements(self, filepath: Optional[str] = None) -> Set[str]:
        """
        Load standardized elements from the compatibility file.
        
        Args:
            filepath: Path to the Standardized_Compatibility.json file.
                      If None, will try to find the file in default locations.
                      
        Returns:
            Set of standardized element names.
        """
        standard_elements = set()
        
        # Default paths to check if filepath is not provided
        default_paths = [
            os.path.join("data", "Standardized_Compatibility.json"),
            os.path.join("..", "data", "Standardized_Compatibility.json"),
            os.path.join(os.path.dirname(__file__), "..", "data", "Standardized_Compatibility.json")
        ]
        
        paths_to_try = [filepath] if filepath else default_paths
        
        for path in paths_to_try:
            if path and os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract elements from the "Blood line" section
                    if "Blood line" in data:
                        # Add each bloodline (key in the "Blood line" section) as a standardized element
                        standard_elements.update(data["Blood line"].keys())
                        
                        # Also add any elements that appear in compatibility lists
                        for bloodline_data in data["Blood line"].values():
                            for compatibility_list in bloodline_data.values():
                                if isinstance(compatibility_list, list):
                                    # Add all elements except "All" which is a special keyword
                                    standard_elements.update([e for e in compatibility_list if e != "All"])
                    
                    self.logger.info(f"Loaded standardized elements from: {path}")
                    break  # Stop after finding the first valid file
                    
                except Exception as e:
                    self.logger.error(f"Error loading standardized elements from {path}: {str(e)}")
                    continue
        
        # If no elements were loaded, use a hardcoded list of standard elements
        if not standard_elements:
            self.logger.warning("Using hardcoded standardized elements as fallback")
            standard_elements = {"Moon", "Water", "Wind", "Earth", "Death", "Fire", "Protection", "Love", "Song", "Sun"}
        
        return standard_elements


# Example usage of ElementMapper
if __name__ == "__main__":
    # Set up logging to see the debug messages
    logging.basicConfig(level=logging.DEBUG, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create an instance of ElementMapper
    mapper = ElementMapper()
    
    print("ElementMapper Example:")
    print("-" * 30)
    
    # Standard elements that should be recognized
    standard_elements = ["Moon", "Water", "Wind", "Earth", "Death", "Fire", "Protection", "Love", "Song", "Sun"]
    
    # Map each standard element
    print("Mapping standard elements:")
    for element in standard_elements:
        mapped = mapper.map_element(element)
        print(f"  {element} -> {mapped}")
    
    # Create custom mappings between standard elements
    print("\nAdding custom mappings between standard elements:")
    mapper.add_mapping("Water", "Moon")
    mapper.add_mapping("Fire", "Sun")
    
    # Show the results of custom mappings
    print("Results after adding custom mappings:")
    print(f"  Water -> {mapper.map_element('Water')}")
    print(f"  Fire -> {mapper.map_element('Fire')}")
    
    # Show how batch mapping works
    print("\nBatch mapping multiple elements:")
    elements_to_map = ["Water", "Fire", "Earth", "Wind", "Sun"]
    mapped_results = mapper.batch_map_elements(elements_to_map)
    for source, target in mapped_results.items():
        print(f"  {source} -> {target}")
    
    # Get all current mappings
    print("\nAll current mappings:")
    all_mappings = mapper.get_all_mappings()
    for source, target in all_mappings.items():
        print(f"  {source} -> {target}")

