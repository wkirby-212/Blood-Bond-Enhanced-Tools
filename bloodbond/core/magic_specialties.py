"""
Magic Specialties for the Blood Bond TTRPG system.

This module defines various magic specialties and their unique characteristics,
abilities, and modifiers as defined in the Blood Bond TTRPG magic system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Set, Tuple, Optional, Union


class MagicSpecialty(ABC):
    """
    Base abstract class for all magic specialties in the Blood Bond system.
    
    All specialized magic users derive from this base class, which defines
    common properties and methods for spell calculations and modifications.
    """
    
    def __init__(self, name: str = None, level: int = 1, magical_affinity: int = 0, bloodline: str = None):
        """
        Initialize a new magic specialty.
        
        Args:
            name: The name of the magic user (optional)
            level: The specialty level, affects bonus calculations (1-10)
            magical_affinity: The magical affinity score, affects magic potency
            bloodline: The character's magical bloodline heritage
        """
        self.name = name or self.__class__.__name__
        self.level = max(1, min(10, level))  # Ensure level is between 1 and 10
        self.magical_affinity = magical_affinity
        self.bloodline = bloodline
        
    @property
    @abstractmethod
    def preferred_elements(self) -> Set[str]:
        """Return the set of elements this specialty prefers and gets bonuses with."""
        pass
    
    @property
    @abstractmethod
    def restricted_elements(self) -> Set[str]:
        """Return the set of elements this specialty has difficulty using."""
        pass
    
    @property
    @abstractmethod
    def special_abilities(self) -> Dict[str, str]:
        """Return a dictionary of special abilities with descriptions."""
        pass
    
    def calculate_spell_bonus(self, element: str, spell_level: int) -> int:
        """
        Calculate any bonus to spell effects based on specialty.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        if element.lower() in self.preferred_elements:
            return self.level + spell_level // 2
        elif element.lower() in self.restricted_elements:
            return -self.level // 2
        return 0
    
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        Modify the duration of a spell based on specialty.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        # Default implementation - no modification
        return base_duration
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        Modify the range of a spell based on specialty.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Modified range value
        """
        # Default implementation - no modification
        return base_range
    
    def can_cast_spell(self, element: str) -> bool:
        """
        Determine if this specialty can cast a spell of the given element.
        
        Args:
            element: The element of the spell
            
        Returns:
            True if the spell can be cast, False if restricted
        """
        # By default, all specialties can cast any spell, but with 
        # possible penalties for restricted elements
        return True
    
    def get_spell_difficulty_modifier(self, element: str) -> float:
        """
        Get a modifier to spell difficulty checks.
        
        Args:
            element: The element of the spell
            
        Returns:
            A modifier to difficulty checks (positive means easier)
        """
        if element.lower() in self.preferred_elements:
            return self.level * 0.5
        elif element.lower() in self.restricted_elements:
            return -self.level * 0.7
        return 0

class Chronomage(MagicSpecialty):
    """
    Chronomage specialty - masters of time magic.
    
    Chronomages specialize in manipulating the flow of time, allowing them
    to speed up allies, slow down enemies, and even catch glimpses of 
    possible futures or echoes of the past.
    """
    
    @property
    def class_die(self) -> int:
        """Return the class die size for Chronomage."""
        return 8
    
    def __init__(self, level: int = 1, magical_affinity: int = 0, bloodline: str = None, name: str = None):
        """Initialize a Chronomage with the given level and affinity."""
        super().__init__(name=name, level=level, magical_affinity=magical_affinity, bloodline=bloodline)
    
    @property
    def preferred_elements(self) -> Set[str]:
        """Elements that Chronomages excel with."""
        return {"moon", "wind", "song"}
    
    @property
    def restricted_elements(self) -> Set[str]:
        """Elements that Chronomages struggle with."""
        return {"earth", "death"}
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to Chronomages."""
        return {
            "Temporal Acceleration": "Can extend spell durations by 50% for preferred elements.",
            "Time Glimpse": "Can cast divination spells to glimpse the near future.",
            "Delayed Casting": "Can delay spell effects to trigger at a specific time."
        }
    
    def get_special_ability(self) -> str:
        """
        Return a string representation of the special abilities.
        
        Returns:
            A formatted string describing all special abilities
        """
        abilities = self.special_abilities
        result = f"Chronomage Special Abilities:\n"
        for name, description in abilities.items():
            result += f"- {name}: {description}\n"
        return result
    
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        Chronomages can extend spell durations for preferred elements.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        if element.lower() in self.preferred_elements:
            return int(base_duration * (1.5 + (self.level * 0.1)))
        return base_duration
    
    def calculate_spell_bonus(self, element: str, spell_level: int) -> int:
        """
        Calculate chronomage's bonus to spell effects.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        # Chronomages get extra bonus with time-affecting spells
        base_bonus = super().calculate_spell_bonus(element, spell_level)
        
        # Additional bonus for time magic
        if element.lower() in self.preferred_elements and "time" in element.lower():
            return base_bonus + self.level
        
        return base_bonus

class Graveturgy(MagicSpecialty):
    """
    Graveturgy specialty - masters of death magic.
    
    Graveturgists specialize in manipulating the forces of death and decay,
    allowing them to speak with the dead, animate corpses, and siphon the
    life energy from living beings.
    """
    
    @property
    def class_die(self) -> int:
        """Return the class die size for Graveturgy."""
        return 10
    
    def __init__(self, level: int = 1, magical_affinity: int = 0, bloodline: str = None, name: str = None):
        """Initialize a Graveturgy with the given level and affinity."""
        super().__init__(name=name, level=level, magical_affinity=magical_affinity, bloodline=bloodline)
    
    @property
    def preferred_elements(self) -> Set[str]:
        """Elements that Graveturgists excel with."""
        return {"death", "earth", "moon"}
    
    @property
    def restricted_elements(self) -> Set[str]:
        """Elements that Graveturgists struggle with."""
        return {"love", "protection", "sun"}
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to Graveturgists."""
        return {
            "Death Whispers": "Can communicate with recently deceased spirits.",
            "Life Siphon": "Can drain life force to power spells.",
            "Corpse Animation": "Can temporarily animate dead bodies as servants."
        }
    
    def get_special_ability(self) -> str:
        """
        Return a string representation of the special abilities.
        
        Returns:
            A formatted string describing all special abilities
        """
        abilities = self.special_abilities
        result = f"Graveturgy Special Abilities:\n"
        for name, description in abilities.items():
            result += f"- {name}: {description}\n"
        return result
    
    def calculate_spell_bonus(self, element: str, spell_level: int) -> int:
        """
        Calculate graveturgist's bonus to spell effects.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        # Enhanced death magic
        if element.lower() == "death":
            return self.level + spell_level
        
        # Standard specialty calculations for other elements
        return super().calculate_spell_bonus(element, spell_level)
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        Graveturgists have extended range with death magic.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Modified range value
        """
        if element.lower() == "death":
            return int(base_range * (1.3 + (self.level * 0.05)))
        return base_range

class Illusionist(MagicSpecialty):
    """
    Illusionist specialty - masters of deception and sensory manipulation.
    
    Illusionists specialize in creating false sensory experiences, from simple
    visual tricks to complete sensory immersion that can fool all five senses.
    """
    
    @property
    def class_die(self) -> int:
        """Return the class die size for Illusionist."""
        return 6
    
    def __init__(self, level: int = 1, magical_affinity: int = 0, bloodline: str = None, name: str = None):
        """Initialize an Illusionist with the given level and affinity."""
        super().__init__(name=name, level=level, magical_affinity=magical_affinity, bloodline=bloodline)
    
    @property
    def preferred_elements(self) -> Set[str]:
        """Elements that Illusionists excel with."""
        return {"moon", "wind", "song"}
    
    @property
    def restricted_elements(self) -> Set[str]:
        """Elements that Illusionists struggle with."""
        return {"earth", "fire", "sun"}
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to Illusionists."""
        return {
            "Minor Illusion": "Can create small sensory illusions without formal spellcasting.",
            "Sensory Layering": "Can affect multiple senses with a single casting.",
            "Phantom Reinforcement": "Can make illusions partially real."
        }
    
    def get_special_ability(self) -> str:
        """
        Return a string representation of the special abilities.
        
        Returns:
            A formatted string describing all special abilities
        """
        abilities = self.special_abilities
        result = f"Illusionist Special Abilities:\n"
        for name, description in abilities.items():
            result += f"- {name}: {description}\n"
        return result
    
    def calculate_spell_bonus(self, element: str, spell_level: int) -> int:
        """
        Calculate illusionist's bonus to spell effects.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        base_bonus = super().calculate_spell_bonus(element, spell_level)
        
        # Additional bonus for illusion magic
        if "illusion" in element.lower() or "phantom" in element.lower():
            return base_bonus + self.level
            
        return base_bonus
    
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        Illusionists can maintain illusions longer.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        if element.lower() in self.preferred_elements:
            # Extend duration for preferred elements
            return int(base_duration * (1.4 + (self.level * 0.1)))
        return base_duration

class Siren(MagicSpecialty):
    """
    Siren specialty - masters of sound and emotion magic.
    
    Sirens specialize in manipulating emotions and using sound as a magical
    medium, allowing them to charm, inspire, terrify, or manipulate others
    through the power of their voice and music.
    """
    
    @property
    def class_die(self) -> int:
        """Return the class die size for Siren."""
        return 8
    
    def __init__(self, level: int = 1, magical_affinity: int = 0, bloodline: str = None, name: str = None):
        """Initialize a Siren with the given level and affinity."""
        super().__init__(name=name, level=level, magical_affinity=magical_affinity, bloodline=bloodline)
    
    @property
    def preferred_elements(self) -> Set[str]:
        """Elements that Sirens excel with."""
        return {"song", "love", "wind"}
    
    @property
    def restricted_elements(self) -> Set[str]:
        """Elements that Sirens struggle with."""
        return {"earth", "death"}
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to Sirens."""
        return {
            "Enchanting Voice": "Can cast minor charm effects through singing.",
            "Emotional Resonance": "Can sense and amplify emotions in an area.",
            "Sonic Disruption": "Can use sound to disrupt enemy spellcasting."
        }
    
    def get_special_ability(self) -> str:
        """
        Return a string representation of the special abilities.
        
        Returns:
            A formatted string describing all special abilities
        """
        abilities = self.special_abilities
        result = f"Siren Special Abilities:\n"
        for name, description in abilities.items():
            result += f"- {name}: {description}\n"
        return result
    
    def calculate_spell_bonus(self, element: str, spell_level: int) -> int:
        """
        Calculate siren's bonus to spell effects.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        base_bonus = super().calculate_spell_bonus(element, spell_level)
        
        # Additional bonus for emotion/sound-based magic
        if element.lower() == "song" or "emotion" in element.lower() or "charm" in element.lower():
            return base_bonus + (self.level // 2) + 2
            
        return base_bonus
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        Sirens have extended range with sound-based magic.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Modified range value
        """
        if element.lower() == "song" or "sound" in element.lower():
            return int(base_range * (1.5 + (self.level * 0.1)))
        return base_range

class WarMage(MagicSpecialty):
    """
    WarMage specialty - masters of combat and destructive magic.
    
    WarMages specialize in combat applications of magic, focusing on destructive
    spells, defensive barriers, and tactical enhancements that give them an
    edge on the battlefield.
    """
    
    @property
    def class_die(self) -> int:
        """Return the class die size for WarMage."""
        return 12
    
    def __init__(self, level: int = 1, magical_affinity: int = 0, bloodline: str = None, name: str = None):
        """Initialize a WarMage with the given level and affinity."""
        super().__init__(name=name, level=level, magical_affinity=magical_affinity, bloodline=bloodline)
    
    @property
    def preferred_elements(self) -> Set[str]:
        """Elements that WarMages excel with."""
        return {"fire", "earth", "protection"}
    
    @property
    def restricted_elements(self) -> Set[str]:
        """Elements that WarMages struggle with."""
        return {"love", "song"}
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to WarMages."""
        return {
            "Battle Instinct": "Gain advantage on initiative when using magic in combat.",
            "Spell Shield": "Can convert offensive magic into defensive barriers.",
            "Focused Destruction": "Can concentrate destructive magic into precise strikes."
        }
    
    def get_special_ability(self) -> str:
        """
        Return a string representation of the special abilities.
        
        Returns:
            A formatted string describing all special abilities
        """
        abilities = self.special_abilities
        result = f"WarMage Special Abilities:\n"
        for name, description in abilities.items():
            result += f"- {name}: {description}\n"
        return result
    
    def calculate_spell_bonus(self, element: str, spell_level: int) -> int:
        """
        Calculate war mage's bonus to spell effects.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        base_bonus = super().calculate_spell_bonus(element, spell_level)
        
        # Additional damage bonus for offensive spells
        if element.lower() in self.preferred_elements and any(x in element.lower() for x in ["attack", "strike", "bolt", "blast"]):
            return base_bonus + self.level + (spell_level // 2)
            
        return base_bonus
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        WarMages have extended range with offensive magic.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Modified range value
        """
        # Increase range for offensive magic
        if element.lower() == "fire" or any(x in element.lower() for x in ["attack", "strike", "bolt", "blast"]):
            return int(base_range * (1.2 + (self.level * 0.05)))
        return base_range

class Alchemist(MagicSpecialty):
    """
    Alchemist specialty - masters of transformation and material magic.
    
    Alchemists specialize in manipulating physical matter, brewing potions,
    and transforming substances from one form to another through a combination
    of magical knowledge and scientific principles.
    """
    
    @property
    def class_die(self) -> int:
        """Return the class die size for Alchemist."""
        return 8
    
    def __init__(self, level: int = 1, magical_affinity: int = 0, bloodline: str = None, name: str = None):
        """Initialize an Alchemist with the given level and affinity."""
        super().__init__(name=name, level=level, magical_affinity=magical_affinity, bloodline=bloodline)
    
    @property
    def preferred_elements(self) -> Set[str]:
        """Elements that Alchemists excel with."""
        return {"earth", "water", "fire"}
    
    @property
    def restricted_elements(self) -> Set[str]:
        """Elements that Alchemists struggle with."""
        return {"song", "moon"}
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to Alchemists."""
        return {
            "Transmute": "Can transform one material into another temporarily.",
            "Quickbrew": "Can create potions with immediate but temporary effects.",
            "Elemental Infusion": "Can infuse objects with elemental properties."
        }
        
    def get_special_ability(self) -> str:
        """Returns a string description of the Alchemist's special abilities."""
        abilities = []
        for name, desc in self.special_abilities.items():
            abilities.append(f"{name}: {desc}")
        return "\n".join(abilities)
        
class NatureShaman(MagicSpecialty):
    """
    Nature Shaman specialty - masters of environmental and natural magic.
    
    Nature Shamans specialize in communing with nature, manipulating plants and animals,
    controlling weather, and drawing power from natural surroundings.
    """
    
    @property
    def class_die(self) -> int:
        """Return the class die size for NatureShaman."""
        return 10
    
    def __init__(self, level: int = 1, magical_affinity: int = 0, bloodline: str = None, name: str = None):
        """Initialize a NatureShaman with the given level and affinity."""
        super().__init__(name=name, level=level, magical_affinity=magical_affinity, bloodline=bloodline)
    
    @property
    def preferred_elements(self) -> Set[str]:
        """Elements that Nature Shamans excel with."""
        return {"earth", "water", "wind"}
    
    @property
    def restricted_elements(self) -> Set[str]:
        """Elements that Nature Shamans struggle with."""
        return {"death", "fire"}
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to Nature Shamans."""
        return {
            "Wild Growth": "Can rapidly grow plants for battlefield control.",
            "Animal Companion": "Can summon a temporary animal ally.",
            "Weather Shift": "Can temporarily alter local weather conditions.",
            "Natural Healing": "Can channel nature's energy to heal wounds."
        }
    
    def get_special_ability(self) -> str:
        """
        Return a string representation of the special abilities.
        
        Returns:
            A formatted string describing all special abilities
        """
        abilities = self.special_abilities
        result = f"Nature Shaman Special Abilities:\n"
        for name, description in abilities.items():
            result += f"- {name}: {description}\n"
        return result
    
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        Nature Shamans can extend the duration of nature-based effects.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        if element.lower() in self.preferred_elements:
            # Extend duration for preferred elements
            return int(base_duration * (1.4 + (self.level * 0.05)))
