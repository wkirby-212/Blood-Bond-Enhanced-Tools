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
            magical_affinity: The caster's magical affinity score
            bloodline: The caster's magical bloodline (optional)
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
        # possible penalties for restricted elements
        # By default, all specialties can cast any spell, but with 
        # possible penalties for restricted elements
        return True
class NoSpecialty(MagicSpecialty):
    """
    NoSpecialty class - versatile magic without specialization.
    
    Mages without a specific specialty are adaptable and versatile,
    not receiving bonuses for particular elements but also not suffering
    restrictions or penalties when working with any kind of magic.
    """
    
    @property
    def class_die(self) -> int:
        """Return the class die size for NoSpecialty."""
        return 8
    
    def __init__(self, level: int = 1, magical_affinity: int = 0, bloodline: str = None, name: str = None):
        """Initialize a NoSpecialty mage with the given level and affinity."""
        super().__init__(name=name, level=level, magical_affinity=magical_affinity, bloodline=bloodline)
    
    @property
    def preferred_elements(self) -> Set[str]:
        """NoSpecialty mages don't have preferred elements."""
        return set()
    
    @property
    def restricted_elements(self) -> Set[str]:
        """NoSpecialty mages don't have restricted elements."""
        return set()
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to NoSpecialty mages."""
        return {
            "Versatility": "Can work with all elements without bonuses or penalties."
        }
    
    def get_special_ability(self) -> str:
        """
        Return a string representation of the special abilities.
        
        Returns:
            A formatted string describing all special abilities
        """
        abilities = self.special_abilities
        result = f"NoSpecialty Special Abilities:\n"
        for name, description in abilities.items():
            result += f"- {name}: {description}\n"
        return result
    
    def calculate_spell_bonus(self, element: str, spell_level: int) -> int:
        """
        Calculate spell bonus for NoSpecialty mages.
        
        NoSpecialty mages don't receive bonuses or penalties based on elements.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects (always 0)
        """
        return 0
    
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        NoSpecialty mages don't modify spell durations.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Unmodified base duration
        """
        return base_duration
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        NoSpecialty mages don't modify spell ranges.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Unmodified base range
        """
        return base_range

class Chronomage(MagicSpecialty):
    """
    Chronomage specialty - masters of time magic.
    
    Chronomages specialize in manipulating the flow of time, allowing them
    to speed up allies, slow down enemies, and even catch glimpses of 
    possible futures or echoes of the past.
    """
    
    def get_spell_difficulty_modifier(self, element: str) -> float:
        """
        Calculate difficulty modifier for casting spells of a given element.
        
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
        
        Temporal Acceleration allows Chronomages to extend the duration
        of their spells, particularly those related to time manipulation.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        # Base duration extension for preferred elements
        if element.lower() in self.preferred_elements:
            duration_modifier = 1.5 + (self.level * 0.1)
            
            # Additional duration for time-related spells (Temporal Acceleration)
            if "time" in element.lower() or "duration" in element.lower():
                duration_modifier += 0.2 + (self.level * 0.05)
                
            return int(base_duration * duration_modifier)
            
        return base_duration
    
    def calculate_spell_bonus(self, element: str, spell_level: int) -> int:
        """
        Calculate chronomage's bonus to spell effects.
        
        Time Glimpse ability enhances divination and time-related magic,
        allowing for improved predictions and temporal effects.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        # Chronomages get extra bonus with time-affecting spells
        base_bonus = super().calculate_spell_bonus(element, spell_level)
        
        # Additional bonus for time magic (Time Glimpse ability)
        if element.lower() in self.preferred_elements:
            if "time" in element.lower():
                return base_bonus + self.level + (spell_level // 2)
            elif "divination" in element.lower() or "future" in element.lower() or "past" in element.lower():
                # Time Glimpse enhances divination magic
                return base_bonus + (self.level // 2) + 2
        
        return base_bonus

class Graveturgy(MagicSpecialty):
    """
    Graveturgy specialty - masters of gravity magic.
    
    Graveturgists specialize in manipulating gravitational forces,
    allowing them to alter weight, create gravitational wells, and
    manipulate the pull of objects and beings in their vicinity.
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
        return {"earth", "wind", "moon"}
    
    @property
    def restricted_elements(self) -> Set[str]:
        """Elements that Graveturgists struggle with."""
        return {"fire", "song", "love"}
    
    @property
    def special_abilities(self) -> Dict[str, str]:
        """Special abilities unique to Graveturgists."""
        return {
            "Gravity Well": "Can create localized areas of intensified gravity to slow enemies.",
            "Weight Manipulation": "Can alter the weight of objects and creatures temporarily.",
            "Controlled Descent": "Can manipulate falling objects and create safe landing zones.",
            "Gravitational Binding": "Can create invisible bonds between objects using gravity."
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
        # Enhanced gravity-related magic
        if element.lower() == "earth" or "gravity" in element.lower() or "weight" in element.lower():
            return self.level + spell_level
        
        # Standard specialty calculations for other elements
        return super().calculate_spell_bonus(element, spell_level)
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        Graveturgists have extended range with gravity manipulation.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Modified range value
        """
        if element.lower() == "earth" or "gravity" in element.lower():
            return int(base_range * (1.3 + (self.level * 0.05)))
        return base_range
            
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        Graveturgists can maintain gravitational effects longer.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        if "gravity" in element.lower() or "weight" in element.lower():
            return int(base_duration * (1.2 + (self.level * 0.1)))
        return base_duration

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
        
        Phantom Reinforcement allows Illusionists to make their illusions
        partially real, enhancing their effectiveness.
        
        Sensory Layering allows affecting multiple senses with a single casting.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        base_bonus = super().calculate_spell_bonus(element, spell_level)
        
        # Phantom Reinforcement ability enhances illusions
        if "illusion" in element.lower() or "phantom" in element.lower():
            phantom_bonus = self.level + (spell_level // 3)
            return base_bonus + phantom_bonus
        
        # Sensory Layering enhances perception-affecting magic
        elif any(sense in element.lower() for sense in ["sight", "sound", "touch", "smell", "taste"]):
            sensory_bonus = (self.level // 2) + 1
            return base_bonus + sensory_bonus
            
        return base_bonus
    
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        Illusionists can maintain illusions longer.
        
        Their expertise in sustaining complex sensory constructs allows them
        to extend the duration of illusion-based magic significantly.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        # Special case for illusion magic - significantly extended duration
        if "illusion" in element.lower() or "phantom" in element.lower() or "mirage" in element.lower():
            return int(base_duration * (1.8 + (self.level * 0.15)))
        
        # Standard extension for preferred elements
        elif element.lower() in self.preferred_elements:
            return int(base_duration * (1.4 + (self.level * 0.1)))
            
        return base_duration
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        Illusionists can project illusions at greater distances.
        
        Their Minor Illusion ability allows them to extend the reach of
        their illusion-based magic.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Modified range value
        """
        # Extend range for illusion magic
        if "illusion" in element.lower() or "phantom" in element.lower() or "mirage" in element.lower():
            return int(base_range * (1.3 + (self.level * 0.05)))
            
        return base_range

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
        
        Enchanting Voice ability enhances charm and sound-based magic.
        Emotional Resonance amplifies emotion-affecting spells.
        Sonic Disruption allows using sound to disrupt enemy spellcasting.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        base_bonus = super().calculate_spell_bonus(element, spell_level)
        
        # Enchanting Voice enhances charm effects
        if "charm" in element.lower() or "enchant" in element.lower():
            charm_bonus = self.level + (spell_level // 2)
            return base_bonus + charm_bonus
            
        # Emotional Resonance enhances emotion-based magic
        elif "emotion" in element.lower() or "feel" in element.lower() or "mood" in element.lower():
            emotion_bonus = (self.level // 2) + 3
            return base_bonus + emotion_bonus
            
        # Sonic Disruption enhances sound-based magic
        elif element.lower() == "song" or "sound" in element.lower() or "sonic" in element.lower():
            sound_bonus = self.level + 2
            return base_bonus + sound_bonus
            
        return base_bonus
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        Sirens have extended range with sound-based magic.
        
        Their Sonic Disruption ability allows sound to travel further
        and their voice to carry magical effects over greater distances.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Modified range value
        """
        # Sonic Disruption significantly extends the range of sound magic
        if element.lower() == "song" or "sound" in element.lower() or "sonic" in element.lower():
            return int(base_range * (1.6 + (self.level * 0.12)))
            
        # Enchanting Voice extends the range of emotion/charm effects
        elif "emotion" in element.lower() or "charm" in element.lower() or "enchant" in element.lower():
            return int(base_range * (1.3 + (self.level * 0.08)))
            
        return base_range
    
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        Sirens can maintain emotional effects for extended periods.
        
        Their Emotional Resonance ability allows them to sustain
        emotion-affecting magic for longer durations.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        # Emotional Resonance extends duration of emotion-based magic
        if "emotion" in element.lower() or "charm" in element.lower() or "enchant" in element.lower():
            return int(base_duration * (1.4 + (self.level * 0.1)))
            
        return base_duration

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
        
        Battle Instinct ability enhances combat-oriented magic, providing
        bonuses to initiative and spell effectiveness in combat situations.
        
        Focused Destruction ability allows for more precise and devastating
        offensive magic targeting.
        
        Spell Shield provides enhanced defensive capabilities, converting
        offensive power into protective barriers.
        
        Args:
            element: The element of the spell
            spell_level: The level of the spell being cast
            
        Returns:
            Bonus value to add to spell effects
        """
        base_bonus = super().calculate_spell_bonus(element, spell_level)
        
        # Battle Instinct bonus for combat magic
        if any(x in element.lower() for x in ["combat", "battle", "initiative", "tactical"]):
            battle_bonus = (self.level * 1.5) // 1  # Integer division after multiplication
            return base_bonus + battle_bonus
        
        # Focused Destruction bonus for offensive spells with preferred elements
        if element.lower() in self.preferred_elements and any(x in element.lower() for x in ["attack", "strike", "bolt", "blast"]):
            # Enhanced precision and power
            focused_bonus = self.level + spell_level + (self.level // 3)
            return base_bonus + focused_bonus
            
        # Spell Shield bonus for defensive magic
        if "protection" in element.lower() or any(x in element.lower() for x in ["shield", "barrier", "ward", "defense"]):
            shield_bonus = self.level + (spell_level // 2) + 2
            return base_bonus + shield_bonus
            
        # General offensive magic bonus
        if any(x in element.lower() for x in ["attack", "strike", "bolt", "blast", "damage"]):
            return base_bonus + self.level
            
        return base_bonus
    
    def modify_range(self, base_range: int, element: str) -> int:
        """
        WarMages have extended range with offensive magic.
        
        Focused Destruction ability allows War Mages to concentrate their 
        destructive magic into precise strikes at greater distances, enhancing
        both accuracy and range of offensive spells.
        
        Args:
            base_range: The base range of the spell in feet
            element: The element of the spell
            
        Returns:
            Modified range value
        """
        # Focused Destruction significantly increases range for precise offensive magic
        if any(x in element.lower() for x in ["precise", "aimed", "focused"]):
            return int(base_range * (1.5 + (self.level * 0.08)))
            
        # Standard increase for offensive magic
        if element.lower() == "fire" or any(x in element.lower() for x in ["attack", "strike", "bolt", "blast"]):
            return int(base_range * (1.3 + (self.level * 0.06)))
            
        # Modest increase for tactical and battlefield control spells
        if any(x in element.lower() for x in ["tactical", "battlefield", "control", "zone"]):
            return int(base_range * (1.15 + (self.level * 0.04)))
            
        return base_range
        
    def modify_duration(self, base_duration: int, element: str) -> int:
        """
        WarMages can maintain defensive barriers and tactical effects longer.
        
        Spell Shield ability allows War Mages to convert offensive power into
        defensive barriers, extending the duration of protective magic.
        
        Args:
            base_duration: The base duration of the spell in rounds
            element: The element of the spell
            
        Returns:
            Modified duration value
        """
        # Spell Shield extends duration for protective magic
        if "protection" in element.lower() or any(x in element.lower() for x in ["shield", "barrier", "ward", "defense"]):
            # Significant extension for defensive magic
            return int(base_duration * (1.6 + (self.level * 0.1)))
            
        # Battle Instinct extends duration for tactical and battlefield control spells
        if any(x in element.lower() for x in ["tactical", "battlefield", "control", "zone"]):
            return int(base_duration * (1.3 + (self.level * 0.07)))
            
        return base_duration

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
