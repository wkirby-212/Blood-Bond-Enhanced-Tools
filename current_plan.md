# Magic Specialties UI Integration Plan

This document outlines the steps for integrating the Magic Specialties classes into the Blood Bond Enhanced Tools user interface.

## Implementation Steps

### 1. Add Magic Specialty Selection to the UI

- Add a new Magic Specialty dropdown to the main spell creator interface
- Implement similar to the existing Bloodline dropdown
- Use the following specialty types:
  - Chronomage
  - Graveturgy
  - Illusionist
  - Siren
  - War Mage
  - Alchemist
  - Nature Shaman

`python
# Get available magic specialties
self.magic_specialties = ["Chronomage", "Graveturgy", "Illusionist", "Siren", "War Mage", "Alchemist", "Nature Shaman"]

# Add to tk_vars
self.tk_vars["magic_specialty"] = var_class()

# Add UI element in _setup_spell_creator_tab function
specialty_label = label_class(left_column, text="Magic Specialty:")
specialty_label.pack(anchor=tk.W, pady=(0, 5))

if USE_CTK:
    specialty_dropdown = combobox_class(left_column, values=self.magic_specialties,
                                variable=self.tk_vars["magic_specialty"])
else:
    specialty_dropdown = combobox_class(left_column, values=self.magic_specialties,
                                textvariable=self.tk_vars["magic_specialty"])
specialty_dropdown.pack(fill=tk.X, pady=(0, 10))
if self.magic_specialties:
    self.tk_vars["magic_specialty"].set(self.magic_specialties[0])
`

### 2. Update the SpellCreatorApp Class

- Import the required Magic Specialty classes
- Create a mapping dictionary between specialty names and their class implementations
- Initialize this in the SpellCreatorApp constructor

`python
from bloodbond.core.magic_specialties import (
    Chronomage, Graveturgy, Illusionist, Siren, WarMage, Alchemist, NatureShaman
)

# Add this to the __init__ method
self.specialty_classes = {
    "Chronomage": Chronomage,
    "Graveturgy": Graveturgy,
    "Illusionist": Illusionist,
    "Siren": Siren,
    "War Mage": WarMage,
    "Alchemist": Alchemist,
    "Nature Shaman": NatureShaman
}
`

### 3. Modify SpellCalculator Integration

- Update the create_spell method to pass magic specialty information
- Create specialty instances with appropriate level
- Create a SpecialtyCaster object that includes specialty information
- Pass specialty instance to spell creation methods

`python
def create_spell(self):
    # Get values including magic specialty
    magic_specialty = self.tk_vars["magic_specialty"].get()
    
    # Create specialty instance with appropriate level
    specialty_class = self.specialty_classes.get(magic_specialty)
    specialty_instance = None
    if specialty_class:
        specialty_instance = specialty_class(level=power_level)
    
    # Create a caster object that includes specialty
    class SpecialtyCaster:
        def __init__(self, bloodline, specialty, level, affinity=0):
            self.bloodline = bloodline
            self.magical_affinity = affinity
            self.specialty = specialty
            self.level = level
            # Get preferred/restricted elements from specialty
            self.preferred_elements = specialty.preferred_elements if specialty else []
            self.restricted_elements = specialty.restricted_elements if specialty else []
            self.class_die = specialty.class_die if specialty else 10
    
    caster = SpecialtyCaster(bloodline, specialty_instance, power_level)
    
    # Create the spell with specialty-specific calculations
    spell = self.spell_maker.create_spell(
        effect=effect,
        element=element,
        duration=duration,
        range_value=range_val,
        level=power_level,
        bloodline=bloodline,
        magical_affinity=0,
        specialty=specialty_instance
    )
`

### 4. Update SpellMaker and SpellCalculator

- Modify SpellMaker.create_spell to accept specialty parameter
- Pass the specialty to SpellCalculator methods
- Use specialty-specific modifiers for duration, range, and spell bonuses
- Implement specialty-specific calculation methods if needed

`python
# In SpellMaker class
def create_spell(self, effect, element, duration, range_value, level, bloodline=None, magical_affinity=0, specialty=None):
    # Add specialty parameter to the method signature
    # Pass specialty to SpellCalculator methods
    
    # Modify calculation methods to use specialty
    if specialty:
        # Apply specialty-specific modifiers
        duration_value = specialty.modify_duration(base_duration, element)
        range_value = specialty.modify_range(base_range, element)
        spell_bonus = specialty.calculate_spell_bonus(element, level)
`

### 5. Add Magic Specialty Information Display

- Update spell description to include specialty-specific bonuses
- Show class die, preferred elements, and restricted elements
- Include information about special abilities that were used in the spell

`python
# Add specialty information to the description
if specialty_instance:
    specialty_info = (
        f"\n\nMagic Specialty: {magic_specialty}\n"
        f"Class Die: d{specialty_instance.class_die}\n"
        f"Preferred Elements: {', '.join(specialty_instance.preferred_elements)}\n"
        f"Restricted Elements: {', '.join(specialty_instance.restricted_elements)}\n"
    )
    
    # Add any special ability that was used
    if specialty_used_ability:
        specialty_info += f"Special Ability: {specialty_used_ability_name} - {specialty_used_ability_description}\n"
        
    description += specialty_info
`

### 6. Create a Magic Specialty Tab

- Add a new tab to the notebook for Magic Specialty information
- Display detailed information about each specialty
- Show abilities and how they modify spells
- Provide visual guidance on specialty selection based on element preferences

`python
# Add tab in the _setup_ui method
self.specialty_tab = frame_class(self.notebook)
self.notebook.add(self.specialty_tab, text="Magic Specialties")
self._setup_magic_specialty_tab()

def _setup_magic_specialty_tab(self):
    # Similar structure to bloodline compatibility tab
    # Show specialty information, abilities, preferred elements, etc.
`

### 7. Update the PROGRESS.md File

- Move "Complete UI integration for Magic Specialties" to "What We've Accomplished"
- Update "Currently Working On" section with the next task from the list

## Rollback Procedure

If issues are encountered during implementation:

1. Revert UI changes in gui.py
2. Remove specialty parameters from SpellMaker and SpellCalculator
3. Return to the original spell calculation methods
4. Remove imports of Magic Specialty classes if they cause issues
5. Update PROGRESS.md to reflect the current state

## Testing

After implementation, test the following:
- Specialty selection in the UI
- Specialty-specific spell calculations
- Display of specialty information in spell descriptions
- Specialty tab functionality
