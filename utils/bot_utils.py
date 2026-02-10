from telegram import Update
from telegram.ext import ContextTypes
from json_utils import load_json, save_json

ADMINS_FILE = "admins.json"
GROUPS_FILE = "groups.json"
PRAYERS_FILE = "prayers.json"
EVENTS_FILE = "events.json"

# --- Admin utilities ---
def get_admins():
    return load_json(ADMINS_FILE, [])

def add_admin(user_id: str):
    admins = get_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_json(ADMINS_FILE, admins)
        return True
    return False

def remove_admin(user_id: str):
    admins = get_admins()
    if user_id in admins:
        admins.remove(user_id)
        save_json(ADMINS_FILE, admins)
        return True
    return False

def is_admin(user_id: str) -> bool:
    return str(user_id) in get_admins()

# --- Group utilities ---
def get_groups():
    return load_json(GROUPS_FILE, [])

def add_group(group_id: str):
    groups = get_groups()
    if group_id not in groups:
        groups.append(group_id)
        save_json(GROUPS_FILE, groups)
        return True
    return False

def remove_group(group_id: str):
    groups = get_groups()
    if group_id in groups:
        groups.remove(group_id)
        save_json(GROUPS_FILE, groups)
        return True
    return False

# --- Prayer utilities ---
def get_prayers():
    return load_json(PRAYERS_FILE, [])

def add_prayer(user_id: str, text: str):
    prayers = get_prayers()
    prayers.append({"user": user_id, "text": text})
    save_json(PRAYERS_FILE, prayers)

# --- Event utilities ---
def get_events():
    return load_json(EVENTS_FILE, [])

def add_event(event: str):
    events = get_events()
    events.append(event)
    save_json(EVENTS_FILE, events)

def clear_events():
    save_json(EVENTS_FILE, [])
