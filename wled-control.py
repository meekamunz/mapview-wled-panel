import requests
import sys
import re
import json
import logging

# Set up logging
logging.basicConfig(filename='wled.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s')

def clean_json_response(text):
    # Remove invalid control characters
    cleaned_text = re.sub(r'[\x00-\x1f\x7f]', '', text)
    return cleaned_text

def log_response(response):
    logging.info(f"URL: {response.url}")
    logging.info(f"Status Code: {response.status_code}")
    logging.info(f"Response Text: {response.text}")

def get_effects(ip_address):
    url = f"http://{ip_address}/json"
    response = requests.get(url)
    #log_response(response)
    if response.status_code == 200:
        try:
            cleaned_response_text = clean_json_response(response.text)
            data = json.loads(cleaned_response_text)
            if 'effects' in data:
                effects = data['effects']
                effect_names = [effect.split('@')[0] for effect in effects]
                cleaned_effects = []
                for effect in effect_names:
                    effect = effect.replace("♪", "Aud:")
                    effect = re.sub(r'[^a-zA-Z0-9 Aud:]', '', effect).strip()
                    cleaned_effects.append(effect)
                return cleaned_effects
            else:
                return None
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return None
    else:
        return None

def get_palettes(ip_address):
    url = f"http://{ip_address}/json"
    response = requests.get(url)
    #log_response(response)
    if response.status_code == 200:
        data = response.json()
        if 'palettes' in data:
            palettes = data['palettes']
            return palettes
        else:
            return None
    else:
        return None

def set_preset(ip_address, preset_id):
    url = f"http://{ip_address}/json/state"
    payload = {"ps": int(preset_id)}
    response = requests.post(url, json=payload)
    #log_response(response)
    return response.status_code == 200

def sync_off(ip_address):
    url = f"http://{ip_address}/json/state"
    payload = {"udpn": {"send": False}}
    response = requests.post(url, json=payload)
    #log_response(response)
    return response.status_code == 200

def sync_on(ip_address):
    url = f"http://{ip_address}/json/state"
    payload = {"udpn": {"send": True}}
    response = requests.post(url, json=payload)
    #log_response(response)
    return response.status_code == 200

def set_colour(ip_address, colour):
    url = f"http://{ip_address}/json/state"
    response = requests.get(url)
    #log_response(response)
    if response.status_code == 200:
        data = response.json()
        segments = data.get('seg', [])
        for segment in segments:
            segment_id = segment.get('id')
            payload = {"seg": [{"id": segment_id, "col": [colour]}]}
            response = requests.post(url, json=payload)
            log_response(response)
            if response.status_code != 200:
                return False
        return True
    else:
        return False

def set_palette(ip_address, palette_name):
    palettes = get_palettes(ip_address)
    if not palettes:
        return False
    if palette_name not in palettes:
        return False
    palette_id = palettes.index(palette_name)
    url = f"http://{ip_address}/json/state"
    response = requests.get(url)
    #log_response(response)
    if response.status_code == 200:
        data = response.json()
        segments = data['seg']
        payload = {"seg": [{"id": seg["id"], "pal": palette_id} for seg in segments]}
        response = requests.post(url, json=payload)
        log_response(response)
        return response.status_code == 200
    else:
        return False

def get_sync_state(ip_address):
    url = f"http://{ip_address}/json"
    response = requests.get(url)
    #log_response(response)
    if response.status_code == 200:
        data = response.json()
        sync_state = data.get('state', {}).get('udpn', {}).get('send', None)
        if sync_state is not None:
            return "true" if sync_state else "false"
        else:
            return "Failed to get sync state or sync state not available."
    else:
        return "Failed to connect to the device."

def get_presets(ip_address):
    url = f"http://{ip_address}/json/presets"
    response = requests.get(url)
    #log_response(response)
    if response.status_code == 200:
        data = response.json()
        if 'ps' in data:
            return list(data['ps'].values())
        else:
            return None
    else:
        return None

def get_colour(ip_address):
    url = f"http://{ip_address}/json/state"
    response = requests.get(url)
    #log_response(response)
    if response.status_code == 200:
        data = response.json()
        segments = data.get('seg', [])
        if segments:
            colour = segments[0].get('col', [])
            if colour:
                return colour[0]
    return None

def closest_match(input_name, available_names):
    input_name = input_name.lower()
    closest = None
    min_distance = float('inf')
    for name in available_names:
        distance = levenshtein_distance(input_name, name.lower())
        if distance < min_distance:
            min_distance = distance
            closest = name
    return closest

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def set_effect(ip_address, effect_name):
    effects = get_effects(ip_address)
    if not effects:
        return False
    closest_effect = closest_match(effect_name, effects)
    effect_id = effects.index(closest_effect)
    url = f"http://{ip_address}/json/state"
    payload = {"seg": [{"fx": effect_id}]}
    response = requests.post(url, json=payload)
    #log_response(response)
    return response.status_code == 200

def set_preset_by_name(ip_address, preset_name):
    presets = get_presets(ip_address)
    if not presets:
        return False
    preset_id = None
    for key, value in presets.items():
        if value == preset_name:
            preset_id = key
            break
    if preset_id is None:
        return False
    return set_preset(ip_address, preset_id)

if __name__ == "__main__":
    logging.info(f"Script started with arguments: {sys.argv}")
    
    if len(sys.argv) < 3:
        logging.error("Insufficient arguments provided.")
        print("Usage:")
        print("  <ip_address> get-effects")
        print("  <ip_address> get-palettes")
        print("  <ip_address> preset <preset_id>")
        print("  <ip_address> sync-off")
        print("  <ip_address> sync-on")
        print("  <ip_address> set-colour <r> <g> <b>")
        print("  <ip_address> set-palette <palette_name>")
        print("  <ip_address> get-sync")
        print("  <ip_address> get-presets")
        print("  <ip_address> get-colour")
        print("  <ip_address> set-effect <effect_name>")
        print("  <ip_address> set-preset <preset_name>")
        sys.exit(1)

    command = sys.argv[2]
    ip_address = sys.argv[1]

    if command == "get-effects":
        effects = get_effects(ip_address)
        if effects:
            print(';'.join(effects))
        else:
            print("Failed to get effects or no effects available.")
        logging.info(f"get-effects command executed. Result: {effects}")

    elif command == "get-palettes":
        palettes = get_palettes(ip_address)
        if palettes:
            print(';'.join(palettes))
        else:
            print("Failed to get palettes or no palettes available.")
        logging.info(f"get-palettes command executed. Result: {palettes}")

    elif command == "preset":
        if len(sys.argv) < 4:
            print("Usage: <ip_address> preset <preset_id>")
            sys.exit(1)
        preset_id = sys.argv[3]
        if set_preset(ip_address, preset_id):
            print(f"Preset '{preset_id}' set successfully.")
        else:
            print(f"Failed to set preset '{preset_id}'.")
        logging.info(f"preset command executed. Preset ID: {preset_id}")

    elif command == "sync-off":
        if sync_off(ip_address):
            print("Sync turned off successfully.")
        else:
            print("Failed to turn off sync.")
        logging.info("sync-off command executed.")

    elif command == "sync-on":
        if sync_on(ip_address):
            print("Sync turned on successfully.")
        else:
            print("Failed to turn on sync.")
        logging.info("sync-on command executed.")

    elif command == "set-colour":
        if len(sys.argv) < 6:
            print("Usage: <ip_address> colour <r> <g> <b>")
            sys.exit(1)
        r = int(sys.argv[3])
        g = int(sys.argv[4])
        b = int(sys.argv[5])
        colour = [r, g, b]
        if set_colour(ip_address, colour):
            print(f"Colour set to [{r}, {g}, {b}] successfully.")
        else:
            print(f"Failed to set colour [{r}, {g}, {b}].")
        logging.info(f"set-colour command executed. Colour: {colour}")

    elif command == "set-palette":
        if len(sys.argv) < 4:
            print("Usage: <ip_address> set-palette <palette_name>")
            sys.exit(1)
        palette_name = sys.argv[3]
        if set_palette(ip_address, palette_name):
            print(f"Palette '{palette_name}' set successfully.")
        else:
            print(f"Failed to set palette '{palette_name}'.")
        logging.info(f"set-palette command executed. Palette name: {palette_name}")

    elif command == "get-sync":
        sync_state = get_sync_state(ip_address)
        print(sync_state)
        logging.info(f"get-sync command executed. Sync state: {sync_state}")

    elif command == "get-presets":
        presets = get_presets(ip_address)
        if presets:
            print(';'.join(presets))
        else:
            print("Failed to get presets or no presets available.")
        logging.info(f"get-presets command executed. Presets: {presets}")

    elif command == "get-colour":
        colour = get_colour(ip_address)
        if colour:
            print(colour)
        else:
            print("Failed to get colour or no colour available.")
        logging.info(f"get-colour command executed. Colour: {colour}")

    elif command == "set-effect":
        if len(sys.argv) < 4:
            print("Usage: <ip_address> set-effect <effect_name>")
            sys.exit(1)
        effect_name = sys.argv[3]
        if set_effect(ip_address, effect_name):
            print(f"Effect '{effect_name}' set successfully.")
        else:
            print(f"Failed to set effect '{effect_name}'.")
        logging.info(f"set-effect command executed. Effect name: {effect_name}")

    elif command == "set-preset":
        if len(sys.argv) < 4:
            print("Usage: <ip_address> set-preset <preset_name>")
            sys.exit(1)
        preset_name = sys.argv[3]
        if set_preset_by_name(ip_address, preset_name):
            print(f"Preset '{preset_name}' set successfully.")
        else:
            print(f"Failed to set preset '{preset_name}'.")
        logging.info(f"set-preset command executed. Preset name: {preset_name}")

    else:
        print(f"Unknown command: {command}")
        logging.error(f"Unknown command: {command}")
