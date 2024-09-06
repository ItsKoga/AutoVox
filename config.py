import json

# load the config date from the config.json
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)
    
# load a specific value from the config.json
def load_value(key):
    try:
        with open("config.json", "r") as f:
            return json.load(f)[key]
    except:
        return None