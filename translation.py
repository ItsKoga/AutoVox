import json

def load_translation(language_code):
    try:
        with open(f"locales/{language_code}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("locales/en.json", "r", encoding="utf-8") as f:  # Fallback to English
            return json.load(f)
        
def translate(language_code, key):
    translation = load_translation(language_code)
    try:
        return translation[key]
    except:
        return "Translation not found"
    
