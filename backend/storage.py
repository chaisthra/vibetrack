import json
import os
from typing import List, Dict, Optional
from datetime import datetime

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Define file paths
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CONVERSATIONS_FILE = os.path.join(DATA_DIR, "conversations.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")

def initialize_data_files():
    """Initialize data files with default structure if they don't exist"""
    # Initialize users.json
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({"users": []}, f)
    
    # Initialize conversations.json
    if not os.path.exists(CONVERSATIONS_FILE):
        with open(CONVERSATIONS_FILE, 'w') as f:
            json.dump([], f)
    
    # Initialize categories.json with predefined categories
    if not os.path.exists(CATEGORIES_FILE):
        default_categories = {
            "Work": 0,
            "Health": 0,
            "Learning": 0,
            "Personal": 0,
            "Creative": 0,
            "Social": 0
        }
        with open(CATEGORIES_FILE, 'w') as f:
            json.dump(default_categories, f)

# Initialize data files at module load
initialize_data_files()

def load_users() -> List[Dict]:
    """Load users from JSON file"""
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
            return data.get("users", []) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error loading users: {str(e)}")
        return []

def save_users(users: List[Dict]):
    """Save users to JSON file"""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, 'w') as f:
            json.dump({"users": users}, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {str(e)}")

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    try:
        users = load_users()
        print(f"\nLooking for user '{username}' in {len(users)} users")
        for user in users:
            if user.get("username") == username:
                print(f"✓ Found user: {username}")
                return user
        print(f"❌ User not found: {username}")
        return None
    except Exception as e:
        print(f"Error getting user by username: {str(e)}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")
        return None

def load_conversations() -> List[Dict]:
    """Load conversations from JSON file"""
    try:
        if os.path.exists(CONVERSATIONS_FILE):
            with open(CONVERSATIONS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading conversations: {e}")
        return []

def save_conversations(conversations: List[Dict]):
    """Save conversations to JSON file"""
    try:
        with open(CONVERSATIONS_FILE, 'w') as f:
            json.dump(conversations, f, indent=2)
    except Exception as e:
        print(f"Error saving conversations: {e}")

def load_categories() -> Dict[str, int]:
    """Load categories from JSON file"""
    try:
        if os.path.exists(CATEGORIES_FILE):
            with open(CATEGORIES_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading categories: {e}")
        return {}

def save_categories(categories: Dict[str, int]):
    """Save categories to JSON file"""
    try:
        with open(CATEGORIES_FILE, 'w') as f:
            json.dump(categories, f, indent=2)
    except Exception as e:
        print(f"Error saving categories: {e}")

def update_category_metadata(category: str, user_id: str, context: str = None):
    """Update category metadata"""
    categories = load_categories()
    if category not in categories:
        categories[category] = {
            "frequency": 0,
            "first_seen": datetime.utcnow().isoformat(),
            "context_clues": [],
            "related_categories": [],
            "user_stats": {}
        }
    
    cat_data = categories[category]
    cat_data["frequency"] += 1
    
    if user_id not in cat_data["user_stats"]:
        cat_data["user_stats"][user_id] = {
            "frequency": 0,
            "first_seen": datetime.utcnow().isoformat(),
            "last_used": None
        }
    
    user_stats = cat_data["user_stats"][user_id]
    user_stats["frequency"] += 1
    user_stats["last_used"] = datetime.utcnow().isoformat()
    
    if context:
        if context not in cat_data["context_clues"]:
            cat_data["context_clues"].append(context)
    
    save_categories(categories)
    return cat_data

def add_conversation(conversation_data: Dict):
    """Add a new conversation"""
    conversations = load_conversations()
    conversations.append({
        "id": conversation_data["id"],
        "timestamp": datetime.utcnow().isoformat(),
        "type": conversation_data.get("type", "voice"),
        "raw_conversation": conversation_data.get("raw_conversation", {}),
        "processed_data": conversation_data.get("processed_data", [])
    })
    save_conversations(conversations)

def get_conversations(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """Get conversations with optional date filtering"""
    conversations = load_conversations()
    filtered = []
    
    for conv in conversations:
        if conv.get("user_id") != user_id:
            continue
            
        if start_date and conv["timestamp"] < start_date:
            continue
            
        if end_date and conv["timestamp"] > end_date:
            continue
            
        filtered.append(conv)
    
    return filtered

def get_category_stats(user_id: str) -> Dict[str, Dict]:
    """Get category statistics for a user"""
    categories = load_categories()
    user_stats = {}
    
    for cat_name, cat_data in categories.items():
        if user_id in cat_data.get("user_stats", {}):
            user_stats[cat_name] = cat_data["user_stats"][user_id]
    
    return user_stats

def get_suggested_categories(user_id: str, limit: int = 5) -> List[Dict]:
    """Get suggested categories based on user's history"""
    categories = load_categories()
    user_categories = []
    
    for cat_name, cat_data in categories.items():
        if user_id in cat_data.get("user_stats", {}):
            user_categories.append({
                "name": cat_name,
                "frequency": cat_data["user_stats"][user_id]["frequency"],
                "last_used": cat_data["user_stats"][user_id]["last_used"]
            })
    
    # Sort by frequency and recency
    sorted_categories = sorted(
        user_categories,
        key=lambda x: (x["frequency"], x["last_used"]),
        reverse=True
    )
    
    return sorted_categories[:limit]

def backup_data():
    """Create a backup of all data files"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(DATA_DIR, "backups", timestamp)
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
                with open(os.path.join(backup_dir, "users.json"), 'w') as bf:
                    json.dump(users, bf, indent=2)
        
        if os.path.exists(CONVERSATIONS_FILE):
            with open(CONVERSATIONS_FILE, 'r') as f:
                conversations = json.load(f)
                with open(os.path.join(backup_dir, "conversations.json"), 'w') as bf:
                    json.dump(conversations, bf, indent=2)
        
        if os.path.exists(CATEGORIES_FILE):
            with open(CATEGORIES_FILE, 'r') as f:
                categories = json.load(f)
                with open(os.path.join(backup_dir, "categories.json"), 'w') as bf:
                    json.dump(categories, bf, indent=2)
        
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False 