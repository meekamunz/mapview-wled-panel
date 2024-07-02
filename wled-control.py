import requests
import sys
import re

def get_effects(ip_address):
    url = f"http://{ip_address}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'effects' in data:
            effects = data['effects']
            # Extract only the effect names by splitting at "@" and taking the first part
            effect_names = [effect.split('@')[0] for effect in effects]
            return effect_names
        else:
            return None
    else:
        return None

def get_palettes(ip_address):
    url = f"http://{ip_address}/json"
    response = requests.get(url)
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
    return response.status_code == 200

def sync_off(ip_address):
    url = f"http://{ip_address}/json/state"
    payload = {"udpn": {"send": False}}
    response = requests.post(url, json=payload)
    return response.status_code == 200

def sync_on(ip_address):
    url = f"http://{ip_address}/json/state"
    payload = {"udpn": {"send": True}}
    response = requests.post(url, json=payload)
    return response.status_code == 200

def set_colour(ip_address, colour):
    url = f"http://{ip_address}/json/state"
    # Get current segments
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        segments = data.get('seg', [])
        for segment in segments:
            segment_id = segment.get('id')
            payload = {"seg": [{"id": segment_id, "col": [colour]}]}
            response = requests.post(url, json=payload)
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
    if response.status_code == 200:
        data = response.json()
        segments = data['seg']
        payload = {"seg": [{"id": seg["id"], "pal": palette_id} for seg in segments]}
        response = requests.post(url, json=payload)
        return response.status_code == 200
    else:
        return False

def get_sync_state(ip_address):
    url = f"http://{ip_address}/json"
    response = requests.get(url)
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
    if response.status_code == 200:
        data = response.json()
        segments = data.get('seg', [])
        if segments:
            # Assuming the first segment's primary color is desired
            colour = segments[0].get('col', [])
            if colour:
                return colour[0]  # Returns the first color in the list
    return None

def set_effect(ip_address, effect_name):
    effects = get_effects(ip_address)
    if not effects:
        return False
    if effect_name not in effects:
        return False
    effect_id = effects.index(effect_name)
    url = f"http://{ip_address}/json/state"
    payload = {"seg": [{"fx": effect_id}]}
    response = requests.post(url, json=payload)
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
    if len(sys.argv) < 3:
        print("Usage:")
        print("  <ip_address> get-effects")
        print("  <ip_address> get-palettes")
        print("  <ip_address> preset <preset_id>")
        print("  <ip_address> sync-off")
        print("  <ip_address> sync-on")
        print("  <ip_address> colour <r> <g> <b>")
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

    elif command == "get-palettes":
        palettes = get_palettes(ip_address)
        if palettes:
            print(';'.join(palettes))
        else:
            print("Failed to get palettes or no palettes available.")

    elif command == "preset":
        if len(sys.argv) < 4:
            print("Usage: <ip_address> preset <preset_id>")
            sys.exit(1)
        preset_id = sys.argv[3]
        if set_preset(ip_address, preset_id):
            print(f"Preset '{preset_id}' set successfully.")
        else:
            print(f"Failed to set preset '{preset_id}'.")

    elif command == "sync-off":
        if sync_off(ip_address):
            print("Sync turned off successfully.")
        else:
            print("Failed to turn off sync.")

    elif command == "sync-on":
        if sync_on(ip_address):
            print("Sync turned on successfully.")
        else:
            print("Failed to turn on sync.")

    elif command == "colour":
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

    elif command == "set-palette":
        if len(sys.argv) < 4:
            print("Usage: <ip_address> set-palette <palette_name>")
            sys.exit(1)
        palette_name = sys.argv[3]
        if set_palette(ip_address, palette_name):
            print(f"Palette '{palette_name}' set successfully.")
        else:
            print(f"Failed to set palette '{palette_name}'.")

    elif command == "get-sync":
        sync_state = get_sync_state(ip_address)
        print(sync_state)

    elif command == "get-presets":
        presets = get_presets(ip_address)
        if presets:
            print(';'.join(presets))
        else:
            print("Failed to get presets or no presets available.")

    elif command == "get-colour":
        colour = get_colour(ip_address)
        if colour:
            print(colour)
        else:
            print("Failed to get colour or no colour available.")

    elif command == "set-effect":
        if len(sys.argv) < 4:
            print("Usage: <ip_address> set-effect <effect_name>")
            sys.exit(1)
        effect_name = sys.argv[3]
        if set_effect(ip_address, effect_name):
            print(f"Effect '{effect_name}' set successfully.")
        else:
            print(f"Failed to set effect '{effect_name}'.")

    elif command == "set-preset":
        if len(sys.argv) < 4:
            print("Usage: <ip_address> set-preset <preset_name>")
            sys.exit(1)
        preset_name = sys.argv[3]
        if set_preset_by_name(ip_address, preset_name):
            print(f"Preset '{preset_name}' set successfully.")
        else:
            print(f"Failed to set preset '{preset_name}'.")

    else:
        print(f"Unknown command: {command}")
