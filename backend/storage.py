import json
import os
from datetime import datetime
from pathlib import Path
import shutil

# Create data directory if it doesn't exist
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# File paths
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
USERS_FILE = DATA_DIR / "users.json"

def load_json_file(file_path: Path, default_value=None):
    """Load JSON data from file, creating it if it doesn't exist."""
    if default_value is None:
        default_value = []
    
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            with open(file_path, 'w') as f:
                json.dump(default_value, f)
            return default_value
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default_value

def save_json_file(file_path: Path, data):
    """Save data to JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

# Conversation functions
def load_conversations():
    return load_json_file(CONVERSATIONS_FILE, [])

def save_conversations(conversations):
    return save_json_file(CONVERSATIONS_FILE, conversations)

def add_conversation(user_id, conversation_type, raw_conversation, activities, summary, conversation_id=None):
    conversations = load_conversations()
    new_conversation = {
        "user_id": user_id,
        "type": conversation_type,
        "raw_conversation": raw_conversation,
        "activities": activities,
        "summary": summary,
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat()
    }
    conversations.append(new_conversation)
    return save_conversations(conversations)

def get_conversations(user_id):
    conversations = load_conversations()
    return [conv for conv in conversations if conv.get("user_id") == user_id]

# Category functions
def load_categories():
    return load_json_file(CATEGORIES_FILE, {})

def save_categories(categories):
    return save_json_file(CATEGORIES_FILE, categories)

def update_category_metadata(category, metadata):
    categories = load_categories()
    if category not in categories:
        categories[category] = {"count": 0, "metadata": {}}
    categories[category]["metadata"].update(metadata)
    return save_categories(categories)

def get_category_stats(user_id):
    conversations = get_conversations(user_id)
    stats = {}
    for conv in conversations:
        for activity in conv.get("activities", []):
            category = activity.get("category", "uncategorized")
            if category not in stats:
                stats[category] = 0
            stats[category] += 1
    return stats

def get_suggested_categories(user_id):
    stats = get_category_stats(user_id)
    return sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]

# User functions
def load_users():
    return load_json_file(USERS_FILE, {})

def save_users(users):
    return save_json_file(USERS_FILE, users)

def get_user(username):
    users = load_users()
    return users.get(username)

def create_user(user_data):
    users = load_users()
    if user_data["username"] in users:
        raise ValueError("Username already exists")
    users[user_data["username"]] = user_data
    save_users(users)
    return user_data

def update_user(username, updates):
    users = load_users()
    if username not in users:
        return None
    users[username].update(updates)
    save_users(users)
    return users[username]

# Backup function
def backup_data():
    """Create a backup of all data files."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = DATA_DIR / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        # Copy all JSON files to backup directory
        for file in DATA_DIR.glob("*.json"):
            shutil.copy2(file, backup_dir / file.name)
        
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False 