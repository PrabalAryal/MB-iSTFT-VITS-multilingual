_pad        = "_"
_whitespace = " "
_punctuation = ";:,.!?¡¿—…«»“”+-–()[]{}<>/\\|@#&*~`<>^%$="
_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_dutch_accented_letters = "áéíóúýäëïöüÿàèòùâêôû"

# Core Dutch IPA
_dutch_ipa = "' ()abdefhijklmnoprstuvwxyzøŋœɑɒɔəɛɜɡɣɪɲɵɹɾʃʊʋʌʒʲˈˌː'' ()abdefhijklmnoprstvwyzŋœɑɔəɛɜɡɪʃʊʋˈˌːθ'"

# Diacritics and suprasegmentals (needed to avoid KeyErrors!)
_dutch_diacritics = "ˈˌː̥̩̃"

# Export all symbols
symbols = (
    [_whitespace] +
    [_pad] +
    list(_punctuation) +
    list(_letters) +
    list(_dutch_accented_letters) +
    list(_dutch_ipa) +
    list(_dutch_diacritics)
)

SPACE_ID = symbols.index(" ")
