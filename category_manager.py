import json
import os
import discord

CATEGORY_STORE_FILE = 'category_store.json'

def load_store():
    if not os.path.exists(CATEGORY_STORE_FILE):
        return {"base_category_id": None, "overflow_categories": []}
    try:
        with open(CATEGORY_STORE_FILE, 'r') as f:
            data = json.load(f)
            # Ensure structure
            if "base_category_id" not in data:
                data["base_category_id"] = None
            if "overflow_categories" not in data:
                data["overflow_categories"] = []
            return data
    except json.JSONDecodeError:
        return {"base_category_id": None, "overflow_categories": []}

def save_store(data):
    with open(CATEGORY_STORE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def set_base_category(category_id):
    data = load_store()
    data["base_category_id"] = category_id
    # Reset overflow when base changes to avoid confusion, or keep them? 
    # For now, let's keep them but the logic will prioritize the new base.
    # Actually, if we change base, we probably want to start fresh or continue from there.
    # Let's just update the base ID.
    save_store(data)

def get_base_category_id():
    data = load_store()
    return data.get("base_category_id")

async def get_target_category(guild: discord.Guild):
    data = load_store()
    base_id = data.get("base_category_id")

    if not base_id:
        return None

    # Check base category
    base_category = guild.get_channel(int(base_id))
    if not base_category:
        # If base is missing, we can't do much.
        return None

    if len(base_category.channels) < 50:
        return base_category

    # Check existing overflow categories
    overflow_ids = data.get("overflow_categories", [])
    for cat_id in overflow_ids:
        cat = guild.get_channel(int(cat_id))
        if cat and len(cat.channels) < 50:
            return cat

    # If we are here, all categories are full. Create a new one.
    # Determine the name.
    # Try to parse the number from the last overflow or the base.
    
    # Simple naming strategy: Base Name + " " + (Count + 2)
    # Count + 2 because Base is 1.
    
    new_suffix_num = len(overflow_ids) + 2
    new_name = f"{base_category.name} {new_suffix_num}"
    
    try:
        new_category = await guild.create_category(name=new_name)
        overflow_ids.append(str(new_category.id))
        data["overflow_categories"] = overflow_ids
        save_store(data)
        return new_category
    except discord.HTTPException:
        # Failed to create category (maybe server limit reached?)
        return None
