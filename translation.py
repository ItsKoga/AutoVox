import json

import database

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
    
def replace_placeholders(translation, **kwargs):
    for key, value in kwargs.items():
        translation = translation.replace(f"{{{key}}}", value)
    return translation

def get_translation(id, key, **kwargs):
    language_code = database.execute_read_query(f"SELECT language_code FROM users WHERE id = {id}")[0][0]

    translation = translate(language_code, key)
    return replace_placeholders(translation, **kwargs)
