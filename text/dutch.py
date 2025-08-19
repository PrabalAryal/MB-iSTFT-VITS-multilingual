import re
from unidecode import unidecode
import subprocess
import os
import pyphen

# Regular expression for matching Dutch characters (including accented vowels)
_dutch_characters = re.compile(r'[A-Za-z\d\u00C0-\u017F\u0300-\u036F]')

# Regular expression matching non-Dutch characters or punctuation marks
_dutch_marks = re.compile(r'[^A-Za-z\d\u00C0-\u017F\u0300-\u036F\s]')

# List of (symbol, Dutch) pairs for marks
_symbols_to_dutch = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('€', 'euro'),
    ('$', 'dollar'),
    ('£', 'pond')
]]

# List of (espeak, ipa) pairs for Dutch-specific phonetic refinement
_espeak_to_ipa = [(re.compile('%s' % x[0]), x[1]) for x in [
    # Vowels
    ('a:', 'aː'), ('a', 'a'), ('@', 'ə'), ('e:', 'eː'), ('E', 'ɛ'), ('i:', 'iː'), ('I', 'ɪ'), ('o:', 'oː'), ('O', 'ɔ'), ('u:', 'yː'), ('y', 'ʏ'), ('A', 'ɑ'),
    # Diphthongs
    ('Ei', 'ɛi'), ('9', 'œy'), ('Au', 'ʌu'),
    # Consonants
    ('b', 'b'), ('d', 'd'), ('f', 'f'), ('g', 'ɣ'), ('h', 'h'), ('j', 'j'), ('k', 'k'), ('l', 'l'), ('m', 'm'), ('n', 'n'), ('N', 'ŋ'), ('p', 'p'), ('r', 'r'), ('s', 's'), ('S', 'ʃ'), ('t', 't'), ('v', 'v'), ('z', 'z'), ('Z', 'ʒ'), ('x', 'χ'),
    # Special characters
    ('tS', 'tʃ'), ('dZ', 'dʒ')
]]

# Dutch language hyphenator
dic = pyphen.Pyphen(lang='nl_NL')


def symbols_to_dutch(text):
    """Replaces symbols with their Dutch word equivalents."""
    for regex, replacement in _symbols_to_dutch:
        text = re.sub(regex, replacement, text)
    return text


def dutch_to_phonemes_with_stress(text):
    """
    Uses eSpeak-NG to convert Dutch text to phonemes with stress markers.
    The logic is similar to japanese_to_romaji_with_accent.
    """
    text = symbols_to_dutch(text)
    sentences = re.split(_dutch_marks, text)
    marks = re.findall(_dutch_marks, text)
    ipa_text = ''
    
    # Process each segment of text
    for i, sentence in enumerate(sentences):
        if re.match(_dutch_characters, sentence):
            if ipa_text != '':
                ipa_text += ' '
                
            # Use eSpeak-NG to get the phonemes and stress
            # -vnl: Dutch voice
            # -q: quiet mode
            # -x: IPA phonemes with stress marks
            try:
                result = subprocess.run(
                    ['espeak-ng', '-vnl', '-q', '-x', '--ipa=2', sentence],
                    capture_output=True, text=True, check=True
                )
                phonemes = result.stdout.strip()
                ipa_text += phonemes
            except FileNotFoundError:
                print("eSpeak-NG not found. Please ensure it is installed and in your system's PATH.")
                return ""
            except subprocess.CalledProcessError as e:
                print(f"Error calling eSpeak-NG: {e.stderr}")
                return ""

        if i < len(marks):
            ipa_text += unidecode(marks[i]).replace(' ', '')
    
    return ipa_text


def get_real_stress(text):
    """
    Apply rules to convert eSpeak-NG stress markers to a more
    consistent format.
    'ˈ' for primary stress, 'ˌ' for secondary stress.
    eSpeak-NG uses ' for primary stress.
    """
    # Replace eSpeak-NG's stress markers with standard IPA symbols
    text = text.replace("'", "ˈ")
    text = text.replace("%", "ˌ")
    return text


def dutch_to_ipa(text):
    """
    Main function to convert Dutch text to IPA.
    This corresponds to japanese_to_ipa in the original script.
    """
    ipa_output = dutch_to_phonemes_with_stress(text)
    ipa_output = get_real_stress(ipa_output)
    
    # Apply phonetic refinements using the defined regex list
    for regex, replacement in _espeak_to_ipa:
        ipa_output = re.sub(regex, replacement, ipa_output)
    
    # Handle long vowels (e.g., e: -> eː)
    ipa_output = re.sub(r'([aiuɛɔ])([:])', r'\1ː', ipa_output)

    # Handle glottal stop. eSpeak-ng can be inconsistent.
    # A glottal stop is common before a stressed vowel at the start of a word.
    ipa_output = re.sub(r'(^|\s)(\ˈ?[aiuɛɔ])', r'\1ʔ\2', ipa_output)
    
    return ipa_output

def dutch_to_ipa2(text):
    """
    An alternative IPA conversion.
    This corresponds to japanese_to_ipa2 in the original script.
    """
    ipa_output = dutch_to_ipa(text)
    # Apply additional or alternative rules here.
    # For instance, a different dialect or simplified phonemes.
    return ipa_output

def dutch_to_ipa3(text):
    """
    Another alternative IPA conversion, potentially with more detail.
    This corresponds to japanese_to_ipa3 in the original script.
    """
    ipa_output = dutch_to_ipa(text)
    # Example: A rule for unvoiced stops at the end of a word, which is common in Dutch.
    ipa_output = re.sub(r'([bdg])\s*$', r'\1̥', ipa_output)
    # Example: A rule for final devoicing.
    ipa_output = re.sub(r'([bdgvz])(\s|$)', r'\\1\u0325\2', ipa_output)
    # Add more specific rules for your purpose.
    return ipa_output


# Example usage:
# if __name__ == '__main__':
#     dutch_text = "Het is een mooie dag in Amsterdam. Dit is een test! En dit is ook een test, in het Duits. Maar ook in het Nederlands."
    
#     print("--- Dutch to IPA (with eSpeak-NG) ---")
#     print("Original Text:", dutch_text)
    
#     ipa_result = dutch_to_ipa(dutch_text)
#     print("\nIPA Result 1:", ipa_result)
    
#     ipa_result2 = dutch_to_ipa2(dutch_text)
#     print("IPA Result 2:", ipa_result2)
    
#     ipa_result3 = dutch_to_ipa3(dutch_text)
#     print("IPA Result 3:", ipa_result3)