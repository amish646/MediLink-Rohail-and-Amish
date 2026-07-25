import json
import os
import datetime
import threading

MONGO_URI = "mongodb+srv://amish:AmishPassword123@cluster0.ivayay0.mongodb.net/MediLinkDB?retryWrites=true&w=majority"
CONFIG_FILE = "pharmacy_config.json"

_config_lock = threading.Lock()

def load_config():
    with _config_lock:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    return (
                        data.get('name', 'MediLink Pharmacy'),
                        data.get('license', ''),
                        data.get('lat', ''),
                        data.get('lng', ''),
                        data.get('gemini_key', '')
                    )
            except Exception as e:
                print(f"Error: {e}")
        return "MediLink Pharmacy", "", "", "", ""

def save_config(name, license_no, lat, lng, gemini_key):
    with _config_lock:
        config_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config_data = json.load(f)
            except Exception:
                pass
        
        config_data.update({
            'name': name,
            'license': license_no,
            'lat': lat,
            'lng': lng,
            'gemini_key': gemini_key
        })
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)

def save_last_sync_time():
    with _config_lock:
        config_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config_data = json.load(f)
            except Exception:
                pass
                
        config_data['last_sync'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"Error: {e}")

def get_last_sync_time():
    with _config_lock:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('last_sync', None)
            except Exception:
                pass
        return None
