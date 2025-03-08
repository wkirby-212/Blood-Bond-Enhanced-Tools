"""
Natural Language Processor for Blood Bond spell text analysis.
This module extracts spell parameters (effect, element, duration, range) from natural language text.
Enhanced with weighted synonyms and combination term detection capabilities.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Set

# Set up logging
logger = logging.getLogger(__name__)

class NLProcessor:
    """
    Natural Language Processor for extracting spell parameters from text descriptions.
    Uses weighted synonym matching, keyword detection, and combination term analysis
    to extract effect, element, duration, and range.
    """
    
    def __init__(self, synonyms_path: Optional[str] = None):
        """
        Initialize the NL processor with synonyms data.
        
        Args:
            synonyms_path: Path to the synonyms.json file. If None, tries to find it in the default location.
        """
        self.synonyms = {}
        try:
            if synonyms_path is None:
                # Try to find the synonyms file in the default location
                data_dir = Path(__file__).parent.parent / "data"
                synonyms_path = data_dir / "synonyms.json"
            
            with open(synonyms_path, 'r', encoding='utf-8') as f:
                synonyms_data = json.load(f)
                
                # Convert keys to lowercase to standardize access
                self.synonyms = {}
                # Store synonym-to-parameter mapping for quick lookup
                self.synonym_to_param = {}
                # Store combination terms
                self.combination_terms = {}
                
                for key, value in synonyms_data.items():
                    # Map "Effect" -> "effect", "Element" -> "element", etc.
                    lowercase_key = key.lower()
                    self.synonyms[lowercase_key] = value
                    
                    # Build reverse lookup dictionary for each parameter type
                    param_type = lowercase_key
                    if param_type not in ['effect', 'element', 'duration', 'range']:
                        continue
                        
                    # For each parameter in this type (e.g., each element name)
                    for param_name, synonyms in value.items():
                        # For each synonym or list of synonyms
                        for synonym_entry in synonyms:
                            # Check if it's a weighted synonym (dictionary) or plain string
                            if isinstance(synonym_entry, dict):
                                synonym = synonym_entry.get('term', '').lower()
                                # Check if this is a combination term
                                if 'combines' in synonym_entry:
                                    if param_type not in self.combination_terms:
                                        self.combination_terms[param_type] = []
                                    self.combination_terms[param_type].append({
                                        'term': synonym,
                                        'primary': param_name,
                                        'combines': synonym_entry['combines']
                                    })
                            else:
                                synonym = synonym_entry.lower()
                                
                            if synonym:
                                # Create parameter entry if not exists
                                if param_type not in self.synonym_to_param:
                                    self.synonym_to_param[param_type] = {}
                                # Associate this synonym with its parameter
                                self.synonym_to_param[param_type][synonym] = param_name
                
                logger.debug(f"Loaded synonyms from {synonyms_path}")
                
        except Exception as e:
            logger.error(f"Error loading synonyms: {e}")
            # Initialize with empty dictionaries to prevent errors
            self.synonyms = {
                "effect": {},
                "element": {},
                "duration": {},
                "range": {}
            }
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process natural language text to extract spell parameters.
        
        Args:
            text: The natural language text describing a spell
            
        Returns:
            Dictionary containing extracted parameters: effect, element, duration, range,
            along with confidence scores, possible secondary parameters for combinations,
            and a needs_clarification flag when appropriate.
        """
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid input text: {text}")
            return {
                "effect": None,
                "element": None, 
                "duration": None,
                "range": None,
                "confidence": 0.0
            }
        
        # Check for blood magic terms in the text early
        has_blood_magic = self._check_for_blood_magic(text)
        # Clean and normalize the text
        cleaned_text = self._preprocess_text(text)
        
        # Extract each parameter
        effect_info = self._extract_effect(cleaned_text)
        element_info = self._extract_element(cleaned_text)
        duration = self._extract_duration(cleaned_text)
        spell_range = self._extract_range(cleaned_text)
        
        # Check for combination terms
        combination_effects = self._check_for_combinations(cleaned_text, "effect")
        combination_elements = self._check_for_combinations(cleaned_text, "element")
        
        # Process primary effect and element, considering combinations
        effect = effect_info[0] if effect_info else None
        effect_confidence = effect_info[1] if effect_info else 0
        secondary_effect = None
        
        element = element_info[0] if element_info else None
        element_confidence = element_info[1] if element_info else 0
        secondary_element = None
        
        # If we found combination terms, consider them as secondary parameters
        if combination_effects:
            for combo in combination_effects:
                if combo['primary'] != effect and combo['confidence'] > 0.6:
                    secondary_effect = combo['combines']
                    break
                    
        if combination_elements:
            for combo in combination_elements:
                if combo['primary'] != element and combo['confidence'] > 0.6:
                    secondary_element = combo['combines']
                    break
        
        # Resolve any Death vs Death Mark conflicts
        death_mark_conflict = self._resolve_death_vs_deathmark_conflict(cleaned_text, effect, element, effect_confidence, element_confidence)
        if death_mark_conflict:
            effect = death_mark_conflict.get('effect', effect)
            effect_confidence = death_mark_conflict.get('effect_confidence', effect_confidence)
            element = death_mark_conflict.get('element', element)
            element_confidence = death_mark_conflict.get('element_confidence', element_confidence)
            needs_clarification = death_mark_conflict.get('needs_clarification', False)
        else:
            needs_clarification = False
        
        # Apply blood magic-specific adjustments if detected
        if has_blood_magic:
            # If we have blood magic terms but no element, suggest Death
            if not element:
                element = "Death"
                element_confidence = 0.7
                logger.debug(f"Blood magic terms detected, suggesting Death element with confidence {element_confidence}")
            # If element is already Death, boost confidence
            elif element == "Death":
                element_confidence = min(element_confidence + 0.2, 1.0)
                logger.debug(f"Blood magic terms reinforced Death element, boosting confidence to {element_confidence}")
        
        # Fix "shield from harm" misidentification
        # Improved shield/protection term detection
        shield_patterns = [
            r'\b(shield|protect|guard|defend)\b.*\b(from|against)\b.*\b(harm|damage|danger|attack|magic|spell|curse)',
            r'\b(defensive|protective|shielding)\b.*\b(barrier|ward|aegis|spell|enchantment)',
            r'\b(ward|barrier|aegis|bulwark|bastion)\b.*\b(protect|shield|defend|guard|block)',
            r'\b(immunity|resistance|protection|defense)\b.*\b(against|from)\b',
            r'\b(deflect|block|parry|repel)\b.*\b(attack|spell|harm|damage)'
        ]
        
        for pattern in shield_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if effect != "Shield":
                    logger.debug(f"Detected protective phrase matching '{pattern}', changed effect to Shield")
                    effect = "Shield"
                    effect_confidence = 0.85
                else:
                    # If already Shield, boost confidence
                    effect_confidence = min(effect_confidence + 0.1, 1.0)
                    logger.debug(f"Additional protective pattern reinforced Shield effect, confidence now {effect_confidence}")
                break

        # Calculate overall confidence
        params = [
            (effect, effect_confidence),
            (element, element_confidence),
            duration,
            spell_range
        ]
        confidences = [p[1] for p in params if p is not None]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        result = {
            "effect": effect,
            "element": element,
            "duration": duration[0] if duration else None,
            "range": spell_range[0] if spell_range else None,
            "confidence": overall_confidence,
            "needs_clarification": needs_clarification
        }
        
        # Add secondary parameters if found
        if secondary_effect:
            result["secondary_effect"] = secondary_effect
        if secondary_element:
            result["secondary_element"] = secondary_element
            
        # Add suggested options when disambiguation is needed
        if needs_clarification and effect == "Death Mark" and element == "Death":
            result["suggested_options"] = [
                {"effect": "Death Mark", "element": None, "description": "Mark enemies with death or doom (Death Mark effect)"},
                {"effect": None, "element": "Death", "description": "Use the power of necromancy and death (Death element)"}
            ]
            logger.debug("Added disambiguation options for Death vs Death Mark conflict")
        return result
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess the text for better matching (lowercase, remove punctuation, etc).
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation that might interfere with matching
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_effect(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Extract the spell effect from text.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Tuple of (effect_name, confidence) or None if not found
        """
        return self._extract_parameter(text, "effect")
    
    def _extract_element(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Extract the spell element from text.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Tuple of (element_name, confidence) or None if not found
        """
        return self._extract_parameter(text, "element")
    
    def _extract_duration(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Extract the spell duration from text.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Tuple of (duration_name, confidence) or None if not found
        """
        # First try to find duration expressions through regex patterns
        duration_patterns = [
            (r'\b(\d+)\s*minute', '1_minute'),
            (r'\b(\d+)\s*min', '1_minute'),
            (r'\b(\d+)\s*hour', '1_hour'),
            (r'\b(\d+)\s*day', '1_day'),
            (r'\bone\s*minute', '1_minute'),
            (r'\bone\s*hour', '1_hour'),
            (r'\bone\s*day', '1_day'),
            (r'\binstant', 'instant'),
            (r'\bmomentary', 'instant'),
            (r'\bpermanent', 'permanent'),
            (r'\bcontinuous', 'permanent'),
            (r'\buntil dispelled', 'permanent')
        ]
        
        for pattern, duration_key in duration_patterns:
            match = re.search(pattern, text)
            if match:
                # Check if there's a number captured
                if match.groups() and match.group(1).isdigit():
                    number = int(match.group(1))
                    if number <= 1:
                        return (duration_key, 0.9)
                    elif "minute" in pattern or "min" in pattern:
                        if number <= 5:
                            return ("5_minute", 0.9)
                        elif number <= 10:
                            return ("10_minute", 0.9)
                        elif number <= 30:
                            return ("30_minute", 0.9)
                        else:
                            return ("1_hour", 0.8)
                    elif "hour" in pattern:
                        if number <= 1:
                            return ("1_hour", 0.9)
                        elif number <= 8:
                            return ("8_hour", 0.9)
                        else:
                            return ("1_day", 0.8)
                    elif "day" in pattern:
                        if number <= 1:
                            return ("1_day", 0.9)
                        else:
                            return ("7_day", 0.8)
                else:
                    return (duration_key, 0.9)
        
        # If no regex pattern matches, try synonym matching
        return self._extract_parameter(text, "duration")
    
    def _extract_range(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Extract the spell range from text.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Tuple of (range_name, confidence) or None if not found
        """
        # First try to find range expressions through regex patterns
        range_patterns = [
            (r'\b(\d+)\s*feet', 'Self'),  # Default unless very specific
            (r'\b(\d+)\s*ft', 'Self'),
            (r'\b(\d+)\s*meter', 'Self'),
            (r'\b(\d+)\s*m\b', 'Self'),
            (r'\bself\b', 'Self'),
            (r'\btouch\b', 'Touch'),
            (r'\bsight\b', 'Sight'),
            (r'\bvisible\b', 'Sight'),
            (r'\bcan see\b', 'Sight')
        ]
        
        for pattern, default_range in range_patterns:
            match = re.search(pattern, text)
            if match:
                # Check if there's a number captured for feet/meters
                if match.groups() and match.group(1).isdigit():
                    distance = int(match.group(1))
                    # Convert distance to appropriate range category
                    if distance <= 5:
                        return ("Touch", 0.8)
                    elif distance <= 30:
                        return ("30ft", 0.9)
                    elif distance <= 60:
                        return ("60ft", 0.9)
                    elif distance <= 120:
                        return ("120ft", 0.9)
                    else:
                        return ("Sight", 0.8)
                else:
                    return (default_range, 0.9)
        
        # If no regex pattern matches, try synonym matching
        return self._extract_parameter(text, "range")
    
    def _extract_parameter(self, text: str, param_type: str) -> Optional[Tuple[str, float]]:
        """
        Generic method to extract a parameter using weighted synonym matching.
        
        Args:
            text: Preprocessed text
            param_type: Type of parameter to extract ('effect', 'element', 'duration', 'range')
            
        Returns:
            Tuple of (param_name, confidence) or None if not found
        """
        if param_type not in self.synonyms:
            logger.warning(f"No synonyms found for parameter type: {param_type}")
            return None
        
        best_match = None
        best_score = 0.0
        
        # Word boundaries for better matching
        words = set(re.findall(r'\b\w+\b', text))
        
        # Check each parameter option and its synonyms
        for param_name, synonyms in self.synonyms[param_type].items():
            # Check the parameter name itself (with word boundary check)
            param_words = set(re.findall(r'\b\w+\b', param_name.lower()))
            if param_words and param_words.issubset(words):
                score = 1.0
                if score > best_score:
                    best_match = param_name
                    best_score = score
            
            # Check each synonym with position-based weighting
            for idx, synonym_entry in enumerate(synonyms):
                # Handle both weighted (dict) and simple (string) synonyms
                weight = 1.0  # Default weight
                synonym = ""
                context_boost = 0.0
                
                # Position-based weight adjustment - earlier synonyms are more direct matches
                position_factor = max(1.0 - (idx * 0.03), 0.7)  # Decrease weight by position, min 0.7
                
                if isinstance(synonym_entry, dict):
                    synonym = synonym_entry.get('term', '').lower()
                    # Explicit weight in dictionary overrides position-based weight
                    weight = synonym_entry.get('weight', position_factor)
                    
                    # Check for contextual terms that boost score
                    context_terms = synonym_entry.get('context', [])
                    if context_terms:
                        for term in context_terms:
                            if term.lower() in text:
                                context_boost += 0.15  # Boost for each context term
                else:
                    synonym = synonym_entry.lower()
                    weight = position_factor
                
                # Check if synonym appears in the text - use word boundaries for precise matching
                if re.search(r'\b' + re.escape(synonym) + r'\b', text):
                    # Calculate score based on weight and context boost
                    score = weight + context_boost
                    
                    # Blood magic terminology gets a boost
                    if self._is_blood_magic_term(synonym):
                        score += 0.1
                    
                    # Length bonus for longer, more specific terms
                    length_bonus = min(len(synonym) / 40, 0.1)  # Max 0.1 bonus for length
                    score += length_bonus
                    
                    # Cap the score at 1.0
                    score = min(score, 1.0)
                    
                    # Update best match if we have a better score
                    if score > best_score:
                        best_match = param_name
                        best_score = score
                        logger.debug(f"Found better match for {param_type}: '{param_name}' with score {score:.2f} from synonym '{synonym}'")
        
        # If we found a match with sufficient confidence, return it
        if best_match and best_score >= 0.5:
            return (best_match, best_score)
            
        return None

    def _check_for_combinations(self, text: str, param_type: str) -> List[Dict[str, Any]]:
        """
        Check for combination terms that might indicate multiple elements or effects.
        
        Args:
            text: Preprocessed text
            param_type: Type of parameter to check for combinations ('effect' or 'element')
            
        Returns:
            List of dictionaries with information about found combinations
        """
        combinations = []
        
        if param_type not in self.combination_terms:
            return combinations
        
        # Look for direct combination terms first
        for combo in self.combination_terms[param_type]:
            term = combo.get('term', '').lower()
            if not term:
                continue
                
            # Look for the combination term in the text
            if term in text:
                # Calculate confidence based on term specificity
                confidence = 0.7 + (min(len(term), 20) / 40)
                
                # Check for blood magic terms and boost confidence
                if self._is_blood_magic_term(term):
                    confidence += 0.15
                
                # Check for contextual cues that support this combination
                context_boost = self._check_contextual_support(text, combo.get('combines', ''))
                confidence += context_boost
                
                # Ensure confidence doesn't exceed 1.0
                confidence = min(confidence, 1.0)
                
                combinations.append({
                    'primary': combo.get('primary', ''),
                    'combines': combo.get('combines', ''),
                    'term': term,
                    'confidence': confidence
                })
                
                logger.debug(f"Found combination term '{term}' linking {combo.get('primary', '')} and {combo.get('combines', '')}")
        
        # If no explicit combinations were found, try to detect secondary parameters
        if not combinations and param_type in ['effect', 'element']:
            
            # Special handling for Death Mark vs Death element disambiguation
                if param_type == 'effect':
                    death_mark_patterns = [
                        # Core Death Mark patterns
                        r'\b(mark|brand|curse|branded|marked|cursed)\s+(with|of|by)\s+(death|doom|fate|demise)\b',
                        r'\b(death|doom|fatal|mortal)\s+(mark|brand|curse|hex|stigma|stain|brand)\b',
                        r'\bmark\s+.{0,20}\s+with\s+.{0,20}\s+(death|doom|mortality)\b',
                        r'\bafflict\s+.{0,20}\s+with\s+.{0,20}\s+(death|doom|mortality)\b',
                        r'\b(death\'s|doom\'s|mortality\'s)\s+(mark|brand|curse|sign|seal)\b',
                        r'\b(brand|mark|curse)\s+of\s+death\b',
                        r'\b(herald|harbinger|omen|portent)\s+of\s+(death|doom|demise)\b',
                        r'\bmark\s+.{0,20}\s+(for|by|with)\s+death\b',
                        # Judgment/Condemnation patterns
                        r'\b(doom|fatal|death|dark)\s+(judgment|sentence|verdict|condemnation)\b',
                        r'\b(inscribe|etched|engrave)\s+.{0,15}\s+(mark|sign|rune|sigil)\s+.{0,15}\s+(death|mortality)\b',
                        r'\bmortality\s+(mark|brand|sign|curse)\b',
                        r'\b(mark|brand|curse|branded|marked|cursed).*\b(soul|spirit|essence|heart|mind)\b',
                        r'\b(destined|condemned|doomed)\s+(to|for|by)\s+(death|end|demise|destruction)\b',
                        # Extended Death Mark patterns
                        r'\b(label|tag|target|designate)\s+.{0,15}\s+(with|by|for)\s+.{0,15}\s+(death|mortality|doom)\b',
                        r'\b(place|put|set|leave)\s+.{0,15}\s+(mark|sign|brand|curse)\s+.{0,15}\s+(death|doom|mortality)\b',
                        r'\b(imprint|impress|stamp|emboss)\s+(death|doom|mortality)\s+(mark|symbol|sigil|sign)\b',
                        r'\bfated\s+(to|for)\s+(die|death|perish|doom)\b',
                        r'\b(execute|reap|claim)\s+(target|victim|foe|enemy)\s+(with|using|by)\s+(death|doom)\b',
                        r'\bseal\s+.{0,15}\s+(fate|doom|destiny|future)\b'
                    ]
                    
                    for pattern in death_mark_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            combinations.append({
                                'primary': 'Death Mark',
                                'combines': None,
                                'term': re.search(pattern, text, re.IGNORECASE).group(0),
                                'confidence': 0.85
                            })
                    death_element_patterns = [
                        # Energy/Power patterns
                        r'\b(power|energy|force|essence)\s+of\s+(death|undeath|grave|tomb|crypt|burial)\b',
                        r'\b(necrotic|death|spectral|ghostly|grave)\s+(energy|force|power|essence|mana|magic)\b',
                        # Magic/Element patterns
                        r'\b(necromancy|undeath|decay|decomposition|entropy)\s+(magic|spell|power|aura|presence|energy)\b',
                        r'\b(death|undeath|grave|decay|necrotic|corruption)\s+(magic|element|energy|domain|realm|force)\b',
                        r'\bdeath\s+as\s+(an|the)\s+(element|power|force|source|energy|catalyst)\b',
                        # Aura/Presence patterns
                        r'\b(necromantic|necrotic|death|deathly|mortifying)\s+(aura|presence|emanation|radiation|wave|field)\b',
                        # Creature patterns
                        r'\b(spirit|ghost|phantom|wraith|spectre|skeleton|zombie|undead|revenant|lich|shade)\s+(magic|power|energy|force)\b',
                        # Decay patterns
                        r'\b(putrefaction|rot|decay|decomposition|corruption|entropy|withering)\s+(energy|aura|emanation|force|magic)\b',
                        # Animation patterns
                        r'\b(animate|raise|resurrect|command|control|summon)\s+(dead|corpse|body|undead|skeleton|bones|remains)\b',
                        # Soul/Spirit patterns
                        r'\b(life|soul|spirit|essence|vitality)\s+(drain|stealing|taking|extraction|absorption|harvest|consumption)\b',
                        # Energy patterns
                        r'\b(negative|death|dark|shadow|void|abyssal|netherworld)\s+(energy|force|power|magic)\b',
                        # Extended Death element patterns
                        r'\b(channel|harness|wield|command|control)\s+(death|necrotic|grave|tomb|undeath)\s+(magic|energy|power)\b',
                        r'\bcall\s+(forth|upon|on)\s+(death|necrotic|grave|spirits|undead)\s+(forces|powers|energies)\b',
                        r'\b(death|grave|tomb|crypt|burial)\s+(essence|energy|force)\s+(flows|courses|surges|pulses)\b',
                        r'\b(beyond|between|past)\s+(life|living|death|grave|veil)\b',
                        r'\bpower\s+(from|of|beyond)\s+(grave|death|tomb|crypt|underworld|netherworld)\b'
                    ]
                    
                    for pattern in death_element_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            combinations.append({
                                'primary': 'Death',
                                'combines': None,
                                'term': re.search(pattern, text, re.IGNORECASE).group(0),
                                'confidence': 0.85
                            })
                            logger.debug(f"Detected Death element via specific pattern")
                            break
                # Check for common combination patterns
                if param_type == 'effect':
                    patterns = [
                        (r'\b(create|make|form|generate).*\b(and|while).*\b(protect|shield|defend)', ('Creation', 'Shield')),
                        (r'\b(damage|harm|hurt).*\b(and|while).*\b(heal|cure|restore)', ('Damage', 'Heal')),
                        (r'\b(change|transform|alter).*\b(and|while).*\b(curse|hex|blight)', ('Change', 'Curse')),
                        (r'\b(boost|enhance|strengthen).*\b(and|while).*\b(add|augment|supplement)', ('Boost', 'Add')),
                        (r'\b(shield|protect|guard).*\b(from|against).*\b(harm|damage|danger)', ('Shield', None)),
                        (r'\b(shield|protect|guard|defensive).*\b(barrier|ward|aegis)', ('Shield', None))
                    ]
                else:  # element
                    patterns = [
                        (r'\b(fire|flame|blaze).*\b(and|with|plus).*\b(water|liquid|fluid)', ('Fire', 'Water')),
                        (r'\b(water|liquid|fluid).*\b(and|with|plus).*\b(fire|flame|blaze)', ('Water', 'Fire')),
                        (r'\b(earth|soil|stone|rock).*\b(and|with|plus).*\b(wind|air|breeze)', ('Earth', 'Wind')),
                        (r'\b(wind|air|breeze).*\b(and|with|plus).*\b(earth|soil|stone)', ('Wind', 'Earth')),
                        (r'\b(moon|lunar|silver).*\b(and|with|plus).*\b(sun|solar|golden)', ('Moon', 'Sun')),
                        (r'\b(sun|solar|golden).*\b(and|with|plus).*\b(moon|lunar|silver)', ('Sun', 'Moon')),
                        (r'\b(song|music|melody).*\b(and|with|plus).*\b(love|heart|passion)', ('Song', 'Love')),
                        (r'\b(love|heart|passion).*\b(and|with|plus).*\b(song|music|melody)', ('Love', 'Song')),
                        (r'\b(protection|defend|guard).*\b(and|with|plus).*\b(death|decay|end)', ('Protection', 'Death')),
                        (r'\b(death|decay|end).*\b(and|with|plus).*\b(protection|defend|guard)', ('Death', 'Protection')),
                        # Blood magic element combinations
                        (r'\b(blood|crimson|vitae).*\b(fire|flame|heat)', ('Death', 'Fire')),
                        (r'\b(blood|crimson|vitae).*\b(water|liquid|fluid)', ('Death', 'Water')),
                        (r'\b(blood|crimson|vitae).*\b(earth|soil|stone)', ('Death', 'Earth')),
                        (r'\b(blood|crimson|vitae).*\b(wind|air|breeze)', ('Death', 'Wind')),
                        (r'\b(blood|crimson|vitae).*\b(moon|lunar|silver)', ('Death', 'Moon')),
                        (r'\b(blood|crimson|vitae).*\b(sun|solar|golden)', ('Death', 'Sun'))
                    ]
                
                # Look for patterns in the text
                for pattern, (primary, secondary) in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        confidence = 0.75
                        
                        # Blood magic combinations get a boost
                        if 'blood' in pattern or 'crimson' in pattern or 'vitae' in pattern:
                            confidence += 0.1
                        
                        combinations.append({
                            'primary': primary,
                            'combines': secondary,
                            'term': re.search(pattern, text, re.IGNORECASE).group(0),
                            'confidence': confidence
                        })
                        logger.debug(f"Detected element combination pattern: {primary} + {secondary}")
        
        # Sort combinations by confidence
        combinations.sort(key=lambda x: x['confidence'], reverse=True)
        return combinations

    def _check_for_blood_magic(self, text: str) -> bool:
        """
        Check text for blood magic terminology and return whether blood magic is detected.
        
        Args:
            text: The text to analyze
            
        Returns:
            True if blood magic terminology is detected, False otherwise
        """
        # Normalize text for matching
        text = text.lower()
        
        # Primary blood magic patterns with context
        blood_magic_patterns = [
            r'\b(blood|crimson|vitae|sanguine)\s+(magic|spell|ritual|pact|sacrifice|offering)',
            r'\b(sacrifice|offer|give|draw|spill|shed)\s+(blood|vitae|life\s*force|life\s*essence)',
            r'\b(blood|life)\s+(cost|price|payment|debt|oath|bind|seal)',
            r'\b(vital|life)\s+(essence|energy|force|power)\s+(drain|consume|take|steal)',
            r'\b(crimson|scarlet|red)\s+(ritual|ceremony|rite|circle|sigil|rune)',
            r'\b(dark|forbidden|occult|ancient|primal)\s+(blood|vitae|life)\s+(magic|art|craft)',
            r'\b(blood|vitae)\s+(ward|shield|barrier|protection)',
            r'\b(hemato|sangui|cruor)[a-z]+'  # Blood-related prefixes
        ]
        
        # Check for direct blood magic patterns
        for pattern in blood_magic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.debug(f"Blood magic detected via pattern: {pattern}")
                return True
        
        # Check for specific blood magic terms
        return self._is_blood_magic_term(text)
    
    def _is_blood_magic_term(self, term: str) -> bool:
        """
        Check if a term is related to blood magic for confidence boosting.
        
        Args:
            term: The term to check
            
        Returns:
            True if it's a blood magic term, False otherwise
        """
        # Primary blood-specific terms (highest importance)
        primary_blood_terms = {
            'blood', 'sacrifice', 'vein', 'artery', 'crimson', 'vitae', 'lifeforce',
            'ichor', 'hemato', 'hematurgy', 'cruor', 'sanguine', 'lifeblood', 'life-blood',
            'bloodletting', 'bloodshed', 'gore', 'hemorrhage', 'exsanguinate', 'bleed',
            'bloodline', 'bloodbond', 'blood bond', 'blood-bond', 'sanguimancy',
            'blood-magic', 'blood magic', 'vitality', 'life-essence', 'blood-ritual',
            'bloodpact', 'blood pact', 'blood-pact', 'bloodcurse', 'blood curse'
        }
        
        # Secondary related terms (supporting terms)
        secondary_blood_terms = {
            'offering', 'essence', 'life force', 'vital', 'visceral', 'plasma', 'ritual',
            'pact', 'covenant', 'oath', 'bind', 'binding', 'seal', 'sigil', 'mark', 'brand',
            'consecration', 'sanctify', 'hex', 'curse', 'bane', 'doom', 'fate', 'destiny',
            'scarlet', 'ruby', 'carmine', 'vermilion', 'incarnadine', 'red', 'dark',
            'forbidden', 'ancient', 'primal', 'occult', 'arcane', 'mystical', 'unholy',
            'corrupt', 'tainted', 'defiled', 'profane', 'blasphemous', 'taboo',
            'obscure', 'hidden', 'veiled', 'shrouded', 'shadowy', 'eldritch'
        }
        
        term_words = set(re.findall(r'\b\w+\b', term.lower()))
        
        # Check if any primary blood terms are present
        for word in term_words:
            if word in primary_blood_terms:
                return True
        
        # Check if the full term is in primary blood terms
        if term.lower() in primary_blood_terms:
            return True
            
        # Check if any secondary blood terms are present
        # Only return true if we have at least 2 secondary terms in combination
        secondary_matches = sum(1 for word in term_words if word in secondary_blood_terms)
        if secondary_matches >= 2:
            return True
            
        # Check for blood-related phrases
        blood_phrases = [
            'life essence', 'vital force', 'life force', 'crimson flow',
            'dark ritual', 'blood rite', 'blood oath', 'living sacrifice'
        ]
        for phrase in blood_phrases:
            if phrase in term.lower():
                return True
                
        return False
    
    def _check_contextual_support(self, text: str, target_param: str) -> float:
        """
        Check if there are contextual cues in the text that support the target parameter.
        
        Args:
            text: The preprocessed text
            target_param: The parameter to look for contextual support
            
        Returns:
            Confidence boost based on contextual support (0.0-0.2)
        """
        # If target parameter is empty, no context to check
        if not target_param:
            return 0.0
            
        boost = 0.0
        
        # Check if the target parameter itself is mentioned
        if target_param.lower() in text:
            boost += 0.1
        
        # Look for related terms that might indicate the target parameter
        param_type = ''
        # Find which parameter type the target_param belongs to
        for pt in ['effect', 'element', 'duration', 'range']:
            if target_param in self.synonym_to_param.get(pt, {}):
                param_type = pt
                break
            
            # Also check if it's a direct parameter name
            if pt in self.synonyms and target_param in self.synonyms[pt]:
                param_type = pt
                break
        
        if param_type and target_param in self.synonyms.get(param_type, {}):
            # Check for synonyms of the target parameter
            for synonym_entry in self.synonyms[param_type][target_param]:
                if isinstance(synonym_entry, dict):
                    synonym = synonym_entry.get('term', '').lower()
                else:
                    synonym = str(synonym_entry).lower()
                
                if synonym and synonym in text:
                    boost += 0.1
                    break  # Found one synonym, that's enough
        
        return min(boost, 0.2)  # Cap the boost at 0.2
    
    def _resolve_death_vs_deathmark_conflict(self, text: str, effect: Optional[str], 
                                            element: Optional[str], effect_confidence: float, 
                                            element_confidence: float) -> Optional[Dict[str, Any]]:
        """
        Resolve conflicts between "Death" element and "Death Mark" effect.
        
        When both "Death Mark" effect and "Death" element are detected with similar confidence,
        this method uses contextual clues and pattern matching to determine the appropriate
        interpretation or to flag the need for clarification.
        
        Args:
            text: The preprocessed text
            effect: The detected effect (if any)
            element: The detected element (if any)
            effect_confidence: Confidence in the effect detection
            element_confidence: Confidence in the element detection
            
        Returns:
            Dict with resolved parameters or None if no conflict exists:
            - When needs_clarification=True, suggested_options are added
            - When one option is clearly preferred, it's returned with adjusted confidence
        """
        # Check if we have a potential conflict (both Death element and Death Mark effect detected)
        if not (effect == "Death Mark" and element == "Death"):
            return None
            
        logger.debug(f"Death vs Death Mark conflict detected. Effect confidence: {effect_confidence:.2f}, " 
                    f"Element confidence: {element_confidence:.2f}")
            
        # Calculate confidence difference to determine if disambiguation is needed
        confidence_diff = abs(effect_confidence - element_confidence)
        
        # When confidence scores are similar (difference less than 0.25), we need clarification
        needs_clarification = confidence_diff < 0.25
            
        # Check for keywords that strongly suggest Death Mark effect
        death_mark_patterns = [
            r'\b(mark|brand|curse|afflict|doom|bane|hex|seal|sigil)\b',
            r'\b(mark|brand|curse|afflict).*with.*death\b',
            r'\bdeath.*(mark|brand|curse|affliction)\b',
            r'\bdoom mark\b',
            r'\bfatal brand\b',
            r'\bdeath.*(stigma|stain|taint)\b',
            r'\b(mark|brand).*(soul|spirit|life)\b',
            r'\b(condemn|sentence|judge|destine).*(death|doom|end|destruction)\b',
            r'\b(branded|marked|cursed).*(mortality|doom|death)\b',
            r'\b(dark|fatal|mortal)\s+(inscription|marking|sigil)\b'
        ]
        
        # Check for keywords that strongly suggest Death element
        death_element_patterns = [
            r'\b(necromancy|necrotic|undeath|decay|rot|putrefaction|decomposition)\b',
            r'\bpower.*(death|darkness|shadow|grave|tomb)\b',
            r'\bdeath.*(energy|force|power|magic|essence|aura|element)\b',
            r'\b(necrotic|death|grave|shadow).*(force|energy|power|essence)\b',
            r'\bendless night\b',
            r'\bdeath.*(realm|domain|kingdom)\b',
            r'\b(tomb|grave|crypt|mausoleum).*(magic|power|force)\b',
            r'\b(undead|skeleton|zombie|ghost|spectre|phantom|wraith|spirit)\b',
            r'\b(animate|raise|resurrect|control).*(dead|corpse|undead|body|bones|skeleton|remains)\b',
            r'\b(life|soul|spirit).*(drain|steal|consume|absorb)\b',
            r'\b(negative|dark|death).*(energy|force|essence)\b',
            r'\b(necromantic|deathly|grave|skeletal).*(magic|power|spell|energy)\b'
        ]
        
        # Count matches for each category
        death_mark_score = 0
        death_mark_matches = []
        for pattern in death_mark_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                death_mark_score += 1
                death_mark_matches.append(match.group(0))
                
        death_element_score = 0
        death_element_matches = []
        for pattern in death_element_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                death_element_score += 1
                death_element_matches.append(match.group(0))
        
        logger.debug(f"Death Mark pattern matches: {death_mark_score}, phrases: {death_mark_matches}")
        logger.debug(f"Death element pattern matches: {death_element_score}, phrases: {death_element_matches}")
                
        # Create a result dictionary with information about both options for clarification
        result = {
            "effect": "Death Mark" if effect_confidence >= element_confidence else None,
            "element": "Death" if element_confidence >= effect_confidence else None,
            "effect_confidence": effect_confidence,
            "element_confidence": element_confidence,
            "needs_clarification": needs_clarification
        }
        
        # Adjust based on pattern matching when we have clear patterns
        if death_mark_score > death_element_score + 1:
            # Strong indication of Death Mark effect
            result["effect"] = "Death Mark"
            result["element"] = None
            result["effect_confidence"] = max(effect_confidence, 0.85)
            # Only set needs_clarification to False if the pattern match is very strong
            if death_mark_score >= 3:
                result["needs_clarification"] = False
                logger.debug(f"Strong Death Mark pattern matches ({death_mark_score}) override clarification need")
                
        elif death_element_score > death_mark_score + 1:
            # Strong indication of Death element
            result["effect"] = None
            result["element"] = "Death"
            result["element_confidence"] = max(element_confidence, 0.85)
            # Only set needs_clarification to False if the pattern match is very strong
            if death_element_score >= 3:
                result["needs_clarification"] = False
                logger.debug(f"Strong Death element pattern matches ({death_element_score}) override clarification need")
                
        # Ensure suggested options are included when clarification is needed
        if result["needs_clarification"]:
            result["suggested_options"] = [
                {
                    "effect": "Death Mark", 
                    "element": None, 
                    "description": "Mark enemies with death's curse (Death Mark effect)"
                },
                {
                    "effect": None, 
                    "element": "Death", 
                    "description": "Use the power of necromancy and death energy (Death element)"
                }
            ]
            logger.debug("Death vs Death Mark requires clarification, added suggested options")

        return result
            
    def get_best_parameters(self, text: str) -> Dict[str, Any]:
        """
        Get the best parameters from text, with simplified output.
        Includes secondary effects/elements when detected.
        
        Args:
            text: Natural language text
            
        Returns:
            Dictionary with parameter names as keys and values, including
            secondary_effect and secondary_element when applicable
        """
        result = self.process_text(text)
        
        # Remove confidence from the output
        if "confidence" in result:
            del result["confidence"]
            
        # Handle needs_clarification flag
        if "needs_clarification" in result and not result["needs_clarification"]:
            del result["needs_clarification"]
            
        # Ensure we include secondary parameters if they exist
        return result

    def get_weighted_synonyms(self, param_type: str, param_name: str) -> List[Dict[str, Any]]:
        """
        Get weighted synonyms for a specific parameter.
        
        Args:
            param_type: Type of parameter ('effect', 'element', 'duration', 'range')
            param_name: Name of the specific parameter
            
        Returns:
            List of dictionaries with term and weight for each synonym
        """
        weighted_synonyms = []
        
        if param_type not in self.synonyms or param_name not in self.synonyms[param_type]:
            return weighted_synonyms
            
        synonyms_list = self.synonyms[param_type][param_name]
        
        for idx, synonym_entry in enumerate(synonyms_list):
            position_factor = max(1.0 - (idx * 0.03), 0.7)  # Decrease weight by position, min 0.7
            
            if isinstance(synonym_entry, dict):
                term = synonym_entry.get('term', '').lower()
                weight = synonym_entry.get('weight', position_factor)
                context = synonym_entry.get('context', [])
                
                weighted_synonyms.append({
                    'term': term,
                    'weight': weight,
                    'context': context
                })
            else:
                weighted_synonyms.append({
                    'term': str(synonym_entry).lower(),
                    'weight': position_factor,
                    'context': []
                })
                
        return weighted_synonyms

    def suggest_alternatives(self, text: str, param_type: str) -> List[Tuple[str, float]]:
        """
        Suggest alternative parameters based on partial matches in the text.
        
        Args:
            text: Preprocessed text
            param_type: Type of parameter to suggest
            
        Returns:
            List of tuples with (param_name, confidence) sorted by confidence
        """
        suggestions = []
        
        if param_type not in self.synonyms:
            return suggestions
            
        words = set(re.findall(r'\b\w+\b', text))
        
        for param_name, synonyms in self.synonyms[param_type].items():
            best_score = 0.0
            
            # Check for partial word matches
            for word in words:
                if len(word) < 3:  # Skip very short words
                    continue
                    
                if word in param_name.lower():
                    score = len(word) / len(param_name) * 0.8  # Partial parameter name match
                    best_score = max(best_score, score)
                
                # Check each synonym for partial matches
                for synonym_entry in synonyms:
                    synonym = ""
                    if isinstance(synonym_entry, dict):
                        synonym = synonym_entry.get('term', '').lower()
                    else:
                        synonym = str(synonym_entry).lower()
                        
                    if len(synonym) < 3:  # Skip very short synonyms
                        continue
                        
                    if word in synonym:
                        score = len(word) / len(synonym) * 0.7  # Partial synonym match
                        best_score = max(best_score, score)
                        
            if best_score > 0:
                suggestions.append((param_name, best_score))
                
        # Sort by confidence and return top matches
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions

def process_text(text: str) -> Dict[str, Any]:
    """
    Convenience function to process text using the NLProcessor.
    
    Args:
        text: Natural language text describing a spell
        
    Returns:
        Dictionary containing extracted parameters
    """
    processor = NLProcessor()
    return processor.process_text(text)


def extract_effect(text: str) -> Optional[str]:
    """
    Extract the effect from text.
    
    Args:
        text: Natural language text
        
    Returns:
        Extracted effect or None if not found
    """
    processor = NLProcessor()
    result = processor._extract_effect(processor._preprocess_text(text))
    return result[0] if result else None


def extract_element(text: str) -> Optional[str]:
    """
    Extract the element from text.
    
    Args:
        text: Natural language text
        
    Returns:
        Extracted element or None if not found
    """
    processor = NLProcessor()
    result = processor._extract_element(processor._preprocess_text(text))
    return result[0] if result else None


def extract_duration(text: str) -> Optional[str]:
    """
    Extract the duration from text.
    
    Args:
        text: Natural language text
        
    Returns:
        Extracted duration or None if not found
    """
    processor = NLProcessor()
    result = processor._extract_duration(processor._preprocess_text(text))
    return result[0] if result else None


def extract_range(text: str) -> Optional[str]:
    """
    Extract the range from text.
    
    Args:
        text: Natural language text
        
    Returns:
        Extracted range or None if not found
    """
    processor = NLProcessor()
    result = processor._extract_range(processor._preprocess_text(text))
    return result[0] if result else None

