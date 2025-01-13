from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import signal
from dotenv import load_dotenv
import groq
import json
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.storage import (
    load_conversations,
    save_conversations,
    load_categories,
    save_categories,
    update_category_metadata,
    add_conversation,
    get_conversations,
    get_category_stats,
    get_suggested_categories,
    backup_data
)
from backend.models import UserCreate, UserLogin, UserUpdate, Token, UserProfile
from backend.auth import (
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Initialize global variables

# Load environment variables
load_dotenv()

app = FastAPI(
    title="VibeTrack API",
    description="Backend API for VibeTrack activity tracking application",
    version="1.0.0",
    root_path="/api"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
groq_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

# Constants
AGENT_ID = "fznwkKVgHrHX2VrqsPr4"
PREDEFINED_CATEGORIES = ["Work", "Health", "Learning", "Personal", "Creative", "Social"]

# Models for request/response
class ActivityLog(BaseModel):
    text: str
    timestamp: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = "text"  # Can be "text" or "voice"

class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data

class QueryRequest(BaseModel):
    query: str
    timeframe: Optional[str] = None  # e.g., "today", "this week", "last month"

# Add new model for log queries
class LogQuery(BaseModel):
    query: str
    timeframe: Optional[str] = None
    category_filter: Optional[str] = None

# In-memory storage (replace with proper database in production)
# activity_logs = []
# category_stats: Dict[str, int] = {}

def update_category_stats(category: str):
    stats = load_categories()
    stats[category] = stats.get(category, 0) + 1
    save_categories(stats)

def get_suggested_categories(text: str) -> List[str]:
    # Get top 5 most used categories
    stats = load_categories()
    sorted_categories = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    top_categories = [cat for cat, _ in sorted_categories[:5]]
    return top_categories

def process_activity_text(text: str, source: str = "text", context: str = None) -> dict:
    try:
        # Use Groq to analyze the text and categorize it
        prompt = f"""Analyze this activity text and categorize it into one of these categories: {', '.join(PREDEFINED_CATEGORIES)}.
Return a simple JSON with two fields:
{{
    "processed_text": "cleaned activity text",
    "category": "category_name"
}}

The categories are:
- Work: Professional activities, meetings, tasks
- Health: Exercise, meditation, sports, wellness
- Learning: Study, courses, reading, research
- Personal: Errands, chores, self-care
- Creative: Art, music, writing, crafts
- Social: Friends, family, events, gatherings

Activity text: {text}"""
        
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an activity categorization assistant. Categorize activities accurately into the predefined categories."},
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=100
        )
        
        # Parse the response, handle potential JSON formatting issues
        content = response.choices[0].message.content.strip()
        try:
            result = json.loads(content)
            # Ensure category is one of the predefined ones
            if result.get("category") not in PREDEFINED_CATEGORIES:
                result["category"] = "Personal"  # Default to Personal if category is invalid
        except json.JSONDecodeError:
            # If JSON parsing fails, extract key information using simple text processing
            processed_text = text.strip()
            result = {"processed_text": processed_text, "category": "Personal"}
        
        return {
            "processed_text": result.get("processed_text", text),
            "category": result.get("category", "Personal"),
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error processing activity: {str(e)}")
        return {
            "processed_text": text,
            "category": "Personal",  # Default category
            "source": source,
            "timestamp": datetime.now().isoformat()
        }

# User authentication endpoints
@app.post("/auth/signup")
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Sign up a new user"""
    print(f"\n[API] Signup request received for username: {username}")
    try:
        user = create_user(username, email, password)
        print(f"[API] User created successfully: {username}")
        
        # Generate access token
        access_token = create_access_token({"sub": username})
        print(f"[API] Access token generated for user: {username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except HTTPException as he:
        print(f"[API] HTTP Exception during signup: {he.detail}")
        raise he
    except Exception as e:
        print(f"[API] Error during signup: {str(e)}")
        import traceback
        print(f"[API] Stack trace:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during signup"
        )

@app.post("/auth/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """Login a user"""
    print(f"\n[API] Login request received for username: {username}")
    try:
        user = authenticate_user(username, password)
        if not user:
            print(f"[API] Authentication failed for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate access token
        access_token = create_access_token({"sub": username})
        print(f"[API] Access token generated for user: {username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except HTTPException as he:
        print(f"[API] HTTP Exception during login: {he.detail}")
        raise he
    except Exception as e:
        print(f"[API] Error during login: {str(e)}")
        import traceback
        print(f"[API] Stack trace:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@app.get("/users/me")
async def read_users_me(current_user: UserProfile = Depends(get_current_user)):
    return current_user

@app.put("/users/me")
async def update_user_me(
    user_update: UserUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    updated_user = storage.update_user(current_user.id, user_update.dict(exclude_unset=True))
    if updated_user:
        return {"status": "success", "data": updated_user}
    raise HTTPException(status_code=404, detail="User not found")

# Update existing endpoints to use authentication

@app.post("/log-text")
async def log_text_activity(
    activity: ActivityLog,
    current_user: dict = Depends(get_current_user)
):
    try:
        processed_activity = process_activity_text(activity.text)
        
        # Store the activity with user information
        conversation = {
            "type": "text",
            "raw_text": activity.text,
            "processed_text": processed_activity["processed_text"],
            "category": processed_activity["category"],
            "timestamp": processed_activity["timestamp"],
            "source": "text",
            "user_id": current_user["username"],
            "user_email": current_user["email"]
        }
        
        # Add to storage
        conversations = load_conversations()
        conversations.append(conversation)
        save_conversations(conversations)
        
        # Update category stats
        stats = load_categories()
        category = processed_activity["category"]
        if category not in stats:
            stats[category] = 0
        stats[category] += 1
        save_categories(stats)
        
        return {"status": "success", "data": conversation}
    except Exception as e:
        print(f"Error in log_text_activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation-history")
async def get_conversation_history():
    try:
        conversations = load_conversations()
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories(current_user: UserProfile = Depends(get_current_user)):
    try:
        categories = storage.get_category_stats(current_user.id)
        return {
            "categories": categories,
            "suggested": storage.get_suggested_categories(current_user.id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/visualizations")
async def get_visualizations(current_user: dict = Depends(get_current_user)):
    try:
        conversations = load_conversations()
        
        # Filter conversations for current user
        user_conversations = [
            conv for conv in conversations 
            if conv.get("user_id") == current_user["username"]
        ]
        
        # Initialize visualization data structures
        category_stats = {
            "distribution": {cat: 0 for cat in PREDEFINED_CATEGORIES},
            "time_spent": {cat: 0 for cat in PREDEFINED_CATEGORIES},
            "daily_patterns": {},
            "hourly_patterns": {},
            "color_mapping": {}
        }
        
        # Generate consistent colors for categories
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD", "#D4A5A5"
        ]
        category_stats["color_mapping"] = {
            category: colors[i] for i, category in enumerate(PREDEFINED_CATEGORIES)
        }
        
        # Initialize time patterns
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hours = [f"{hour:02d}:00" for hour in range(24)]
        
        daily_buckets = {day: {cat: 0 for cat in PREDEFINED_CATEGORIES} for day in days}
        hourly_buckets = {hour: {cat: 0 for cat in PREDEFINED_CATEGORIES} for hour in hours}
        
        # Process conversations
        now = datetime.now()
        for conv in user_conversations:
            if not conv.get("timestamp"):
                continue
                
            # Parse timestamp
            ts = datetime.fromisoformat(conv["timestamp"])
            category = conv.get("category")
            
            # Skip if category is not in predefined categories
            if category not in PREDEFINED_CATEGORIES:
                continue
            
            # Update category distribution
            category_stats["distribution"][category] = category_stats["distribution"].get(category, 0) + 1
            
            # Update time spent (30 minutes per activity)
            category_stats["time_spent"][category] = category_stats["time_spent"].get(category, 0) + 30
            
            # Update daily and hourly patterns
            day = days[ts.weekday()]
            hour = f"{ts.hour:02d}:00"
            
            daily_buckets[day][category] += 1
            hourly_buckets[hour][category] += 1
        
        # Add patterns to category stats
        category_stats["daily_patterns"] = daily_buckets
        category_stats["hourly_patterns"] = hourly_buckets
        
        # Calculate activity trends
        activity_trends = {
            "most_active_day": max(daily_buckets.items(), key=lambda x: sum(x[1].values()))[0],
            "most_active_hour": max(hourly_buckets.items(), key=lambda x: sum(x[1].values()))[0],
            "most_common_category": max(category_stats["distribution"].items(), key=lambda x: x[1])[0],
            "category_breakdown": {
                cat: {
                    "count": category_stats["distribution"][cat],
                    "time_spent": category_stats["time_spent"][cat],
                    "color": category_stats["color_mapping"][cat]
                }
                for cat in PREDEFINED_CATEGORIES
            }
        }
        
        return {
            "status": "success",
            "data": {
                "last_updated": now.isoformat(),
                "total_activities": len(user_conversations),
                "stats": category_stats,
                "trends": activity_trends
            }
        }
    except Exception as e:
        print(f"Error generating visualizations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add backup endpoint
@app.post("/backup")
async def create_backup():
    try:
        if storage.backup_data():
            return {"status": "success", "message": "Backup created successfully"}
        return {"status": "error", "message": "Failed to create backup"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Clean shutdown handler
def handle_shutdown(signum, frame):
    pass

signal.signal(signal.SIGINT, handle_shutdown)

@app.get("/activity-history")
async def get_activity_history(current_user: dict = Depends(get_current_user)):
    try:
        # Load conversations and categories
        conversations = load_conversations()
        categories = load_categories()
        
        # Filter conversations for current user
        user_conversations = [
            conv for conv in conversations 
            if conv.get("user_id") == current_user["username"]
        ]
        
        # Process for visualization
        history = []
        category_counts = {}
        timeline_data = []
        
        for conv in user_conversations:
            if conv["type"] == "text":
                # Add to history list
                history.append({
                    "timestamp": conv["timestamp"],
                    "text": conv["raw_text"],
                    "category": conv["category"]
                })
                
                # Update category counts
                cat = conv["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1
                
                # Add to timeline
                timeline_data.append({
                    "date": conv["timestamp"],
                    "category": cat
                })
        
        # Sort history by timestamp, most recent first
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "status": "success",
            "data": {
                "history": history,
                "visualizations": {
                    "category_distribution": category_counts,
                    "timeline": timeline_data
                }
            }
        }
    except Exception as e:
        print(f"Error fetching activity history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_activities(request: QueryRequest):
    try:
        conversations = load_conversations()
        
        # Process timeframe filter
        now = datetime.now()
        start_date = None
        
        if request.timeframe:
            if request.timeframe == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif request.timeframe == "this week":
                start_date = now - timedelta(days=now.weekday())
            elif request.timeframe == "this month":
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif request.timeframe == "last month":
                last_month = now.replace(day=1) - timedelta(days=1)
                start_date = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Filter conversations by timeframe if specified
        if start_date:
            filtered_convs = [
                conv for conv in conversations 
                if datetime.fromisoformat(conv["timestamp"]) >= start_date
            ]
        else:
            filtered_convs = conversations
        
        # Analyze the query using Groq
        prompt = f"""Analyze this natural language query about activities and return a JSON response.
Query: {request.query}
Timeframe: {request.timeframe or 'all time'}

Available data:
- Total activities: {len(filtered_convs)}
- Categories: {list(set(conv.get('category', 'uncategorized') for conv in filtered_convs))}

Return a JSON with:
{{
    "analysis_type": "category_summary|time_analysis|pattern_detection",
    "description": "Natural language description of findings",
    "metrics": {{
        "key_metric_1": value,
        "key_metric_2": value
    }},
    "insights": ["insight 1", "insight 2"]
}}"""

        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=200
        )
        
        # Parse the analysis
        try:
            analysis = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            analysis = {
                "analysis_type": "error",
                "description": "Could not analyze the query",
                "metrics": {},
                "insights": []
            }
        
        # Add raw data for client-side visualization
        result = {
            "analysis": analysis,
            "raw_data": {
                "activities": [
                    {
                        "timestamp": conv["timestamp"],
                        "category": conv.get("category", "uncategorized"),
                        "text": conv.get("raw_text", ""),
                        "processed_text": conv.get("processed_text", "")
                    }
                    for conv in filtered_convs
                ],
                "timeframe": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": now.isoformat()
                }
            }
        }
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        print(f"Error analyzing activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query-logs")
async def query_logs(query_request: LogQuery):
    try:
        conversations = load_conversations()
        categories = load_categories()
        
        # Filter by timeframe if specified
        filtered_convs = conversations
        if query_request.timeframe:
            now = datetime.now()
            start_date = None
            
            if query_request.timeframe == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif query_request.timeframe == "yesterday":
                start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif query_request.timeframe == "this_week":
                start_date = now - timedelta(days=now.weekday())
            elif query_request.timeframe == "last_week":
                last_week = now - timedelta(days=now.weekday() + 7)
                start_date = last_week.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if start_date:
                filtered_convs = [
                    conv for conv in conversations 
                    if datetime.fromisoformat(conv["timestamp"]) >= start_date
                ]
        
        # Filter by category if specified
        if query_request.category_filter:
            filtered_convs = [
                conv for conv in filtered_convs 
                if conv.get("category") == query_request.category_filter
            ]
        
        # Prepare context for Groq
        activities_text = "\n".join([
            f"- {conv['timestamp']}: {conv.get('raw_text', '')} (Category: {conv.get('category', 'general')})"
            for conv in filtered_convs[-10:]  # Last 10 activities for context
        ])
        
        category_stats = {}
        for conv in filtered_convs:
            cat = conv.get("category", "general")
            category_stats[cat] = category_stats.get(cat, 0) + 1
        
        prompt = f"""Analyze this query about activity logs and provide a detailed answer.

Context:
- Total activities: {len(filtered_convs)}
- Time period: {query_request.timeframe or 'all time'}
- Category distribution: {category_stats}

Recent activities:
{activities_text}

User query: {query_request.query}

Provide a JSON response with:
{{
    "answer": "Detailed natural language answer to the query",
    "relevant_activities": ["List of relevant activity texts"],
    "metrics": {{
        "key_metric_1": "value",
        "key_metric_2": "value"
    }},
    "suggestions": ["Relevant suggestions or insights based on the query"]
}}"""

        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI assistant analyzing activity logs. Provide clear, concise answers with relevant metrics and insights."},
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=500
        )
        
        try:
            analysis = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            analysis = {
                "answer": "Could not analyze the query properly. Please try rephrasing your question.",
                "relevant_activities": [],
                "metrics": {},
                "suggestions": []
            }
        
        return {
            "status": "success",
            "data": {
                "analysis": analysis,
                "context": {
                    "total_activities": len(filtered_convs),
                    "timeframe": query_request.timeframe,
                    "category_filter": query_request.category_filter,
                    "category_stats": category_stats
                }
            }
        }
        
    except Exception as e:
        print(f"Error querying logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Activity endpoints
@app.post("/activities")
async def create_activity(
    activity: dict,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Load existing conversations
        conversations = load_conversations()
        
        # Create new activity entry
        new_activity = {
            "type": "text",
            "raw_text": activity["text"],
            "processed_text": activity["text"],
            "category": "general",  # Default category
            "timestamp": activity["timestamp"],
            "source": "text",
            "user_id": current_user["username"]  # Add user ID for isolation
        }
        
        # Add to conversations list
        conversations.append(new_activity)
        
        # Save updated conversations
        save_conversations(conversations)
        
        return {"status": "success", "message": "Activity logged successfully"}
    except Exception as e:
        print(f"Error creating activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/activities")
async def get_activities(current_user: dict = Depends(get_current_user)):
    try:
        # Load all conversations
        conversations = load_conversations()
        
        # Filter conversations for current user
        user_activities = [
            conv for conv in conversations 
            if conv.get("user_id") == current_user["username"]
        ]
        
        # Sort by timestamp, most recent first
        user_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "status": "success",
            "activities": user_activities
        }
    except Exception as e:
        print(f"Error fetching activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 