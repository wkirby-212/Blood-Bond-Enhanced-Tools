# Changelog

All notable changes to the Blood Bond Enhanced Tools project will be documented in this file.

## [0.3.2] - 2025-03-09

### Added
- Added 'Write Spell' functionality to the Random Generator page, allowing users to save randomly generated spells to history
- Implemented duplicate spell detection in Spell History functionality, providing users with a dialog to choose which version to keep when adding spells with identical incantations

## [0.3.1] - 2025-03-09

### Added
- Added "No Specialty" option to the Magic Specialties dropdown
- Implemented proper display of spell formula in spell descriptions
- Added final formula calculation for spell effectiveness based on bloodline compatibility

### Fixed
- Fixed issue where spell effectiveness formulas were not correctly shown in the UI
- Resolved a bug with formula variable being undefined in spell description generation
- Fixed line ending inconsistencies in Python files

### Changed
- Improved spell effectiveness display with both base and final formulas
- Updated Magic Specialties integration to better handle cases with no specialty selected

## [0.3.0] - 2025-03-01

### Added
- Implemented Magic Specialties classes
  - Chronomage
  - Graveturgy
  - Illusionist
  - Siren
  - War Mage
  - Alchemist
  - Nature Shaman
- Complete UI integration for Magic Specialties
- Standardized elements system for consistent spell creation

### Changed
- Enforced standardized elements across the application
- Enhanced UI to display bloodline compatibility information
- Improved directory structure for better maintainability

### Fixed
- Fixed Moon bloodline compatibility with Song element showing incorrectly as 0%
- Synchronized bloodline affinity data between JSON files and SpellCalculator code
- Resolved "weird numbers" issue in bloodline compatibility calculations

