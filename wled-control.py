import requests
import sys

def get_effects(ip_address):
    url = f"http://{ip_address}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'effects' in data:
            effects = data['effects']
            return effects
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

def set_palette(ip_address, palette_id):
    url = f"http://{ip_address}/json/state/seg"
    response = requests.get(url.replace("/seg", ""))
    if response.status_code == 200:
        data = response.json()
        segments = data['seg']
        payload = {"seg": [{"id": seg["id"], "pal": int(palette_id)} for seg in segments]}
        response = requests.post(url, json=payload)
        return response.status_code == 200
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  <ip_address> get-effects")
        print("  <ip_address> get-palettes")
        print("  <ip_address> preset <preset_id>")
        print("  <ip_address> sync-off")
        print("  <ip_address> sync-on")
        print("  <ip_address> colour <r> <g> <b>")
        print("  <ip_address> set-palette <palette_id>")
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
            print("Usage: <ip_address> set-palette <palette_id>")
            sys.exit(1)
        palette_id = sys.argv[3]
        if set_palette(ip_address, palette_id):
            print(f"Palette '{palette_id}' set successfully.")
        else:
            print(f"Failed to set palette '{palette_id}'.")

    else:
        print("Unknown command.")
        print("Usage:")
        print("  <ip_address> get-effects")
        print("  <ip_address> get-palettes")
        print("  <ip_address> preset <preset_id>")
        print("  <ip_address> sync-off")
        print("  <ip_address> sync-on")
        print("  <ip_address> colour <r> <g> <b>")
        print("  <ip_address> set-palette <palette_id>")
