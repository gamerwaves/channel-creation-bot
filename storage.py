import json
import os

STORAGE_FILE = 'user_channels.json'

def load_data():
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_data(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_channels(user_id):
    """Get list of channels created by user"""
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        return []
    if isinstance(data[user_id_str], int):
        return []
    return data[user_id_str].get('channels', [])

def get_user_channel_count(user_id):
    """Get count of channels created by user"""
    return len(get_user_channels(user_id))

def add_user_channel(user_id, channel_id, channel_name):
    """Add a channel to user's created channels"""
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data or isinstance(data[user_id_str], int):
        data[user_id_str] = {'channels': []}
    
    data[user_id_str]['channels'].append({
        'id': channel_id,
        'name': channel_name
    })
    
    save_data(data)
    return len(data[user_id_str]['channels'])

def remove_user_channel(user_id, channel_id):
    """Remove a channel from user's created channels"""
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data or isinstance(data[user_id_str], int):
        return False
    
    channels = data[user_id_str]['channels']
    for i, channel in enumerate(channels):
        if channel['id'] == channel_id:
            channels.pop(i)
            save_data(data)
            return True
    
    return False
def remove_channel_from_all_users(channel_id):
    """Find original channel maker and delete channel from storage for admin deletes."""
    data = load_data()
    modified = False
    
    for user_id_str in data:
        if isinstance(data[user_id_str], dict) and 'channels' in data[user_id_str]:
            channels = data[user_id_str]['channels']
            for i, channel in enumerate(channels):
                if channel['id'] == channel_id:
                    channels.pop(i)
                    modified = True
                    break
    
    if modified:
        save_data(data)
    
    return modified
