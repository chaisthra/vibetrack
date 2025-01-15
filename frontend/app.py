import streamlit as st
import requests
import json
import base64
from datetime import datetime
import os
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import time
from groq import Groq
import sounddevice as sd
import soundfile as sf
import numpy as np
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure page
st.set_page_config(
    page_title="VibeTrack",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
/* Base styles */
.main {
    background: linear-gradient(135deg, #2D1F3D, #1E1E2E, #2D1F3D) !important;
    color: white;
}

.stApp {
    background: linear-gradient(135deg, #2D1F3D, #1E1E2E, #2D1F3D) !important;
}

/* Widget container styling */
.widget-container {
    background-color: rgba(45, 45, 68, 0.7);
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    min-height: 500px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    backdrop-filter: blur(10px);
}

.elevenlabs-widget {
    width: 100%;
    height: 100%;
    border: none;
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Chat interface styling */
.stChatMessage {
    background-color: rgba(45, 45, 68, 0.7) !important;
    border-radius: 15px !important;
    padding: 15px !important;
    margin: 10px 0 !important;
    color: white !important;
    backdrop-filter: blur(10px);
}

.chat-message {
    background-color: rgba(45, 45, 68, 0.7) !important;
    border-radius: 15px !important;
    padding: 15px !important;
    margin: 10px 0 !important;
    color: white !important;
    backdrop-filter: blur(10px);
}

.stChatMessage p {
    color: white !important;
}

.stChatMessage [data-testid="chatAvatarIcon"] {
    background: linear-gradient(135deg, #9D4EDD, #6C63FF) !important;
}

.stChatInput {
    border-radius: 20px !important;
    border: 1px solid rgba(74, 74, 106, 0.5) !important;
    background-color: rgba(45, 45, 68, 0.7) !important;
    color: white !important;
    padding: 10px 15px !important;
    backdrop-filter: blur(10px);
}

.stChatInput::placeholder {
    color: #A0A0A0 !important;
}

/* Voice assistant widget styling */
.voice-assistant {
    background-color: rgba(45, 45, 68, 0.7);
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    min-height: 100%;
    backdrop-filter: blur(10px);
}

/* Divider styling */
.stDivider {
    margin: 15px 0 !important;
    border-color: rgba(74, 74, 106, 0.5) !important;
}

/* Button and form styling */
.stButton button {
    background: linear-gradient(135deg, #9D4EDD, #6C63FF) !important;
    color: white;
    border: none;
    border-radius: 25px;
    padding: 15px 25px;
    font-weight: bold;
}

.auth-form {
    background-color: rgba(45, 45, 68, 0.7);
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    backdrop-filter: blur(10px);
}

.auth-form input {
    background-color: rgba(30, 30, 46, 0.7) !important;
    color: white !important;
    border: 1px solid rgba(74, 74, 106, 0.5) !important;
    border-radius: 10px !important;
    padding: 10px !important;
    margin: 5px 0 !important;
}

.visualization-card {
    background-color: rgba(45, 45, 68, 0.7);
    padding: 20px;
    border-radius: 15px;
    margin: 10px 0;
    backdrop-filter: blur(10px);
}

/* Additional chat styling for better visibility */
.stChatMessage div[data-testid="StyledLinkIconContainer"] {
    color: white !important;
}
.stChatMessage div[data-testid="StyledMessageContainer"] {
    color: white !important;
}
.stChatMessage div[data-testid="StyledMessageContainer"] p {
    color: white !important;
}
.stChatMessage div[data-testid="StyledMessageContainer"] span {
    color: white !important;
}
.stChatMessage div {
    color: white !important;
}
.stMarkdown p {
    color: white !important;
}
.stChatMessage code {
    color: white !important;
}
.stTextArea textarea {
    color: white !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(45, 45, 68, 0.7) !important;
    border-radius: 15px !important;
    padding: 5px !important;
}

.stTabs [data-baseweb="tab"] {
    color: white !important;
    border-radius: 10px !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background: linear-gradient(135deg, #9D4EDD, #6C63FF) !important;
    border-radius: 10px !important;
}

/* Plotly chart background */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

.js-plotly-plot .plotly .bg {
    fill: rgba(45, 45, 68, 0.7) !important;
}

/* Add app name styling */
.app-title {
    background: linear-gradient(135deg, #E9D5FF, #B388FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3em;
    font-weight: bold;
    text-align: center;
    margin-bottom: 1em;
}

/* Header styling */
h1, h2, h3 {
    color: #E9D5FF !important;
    font-weight: 600 !important;
}

/* Feature explanation styling */
.feature-explanation {
    color: #B388FF;
    font-style: italic;
    margin-bottom: 15px;
    font-size: 0.9em;
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="app-title">VibeTrack</h1>', unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "categories" not in st.session_state:
    st.session_state.categories = {}
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

# API endpoints
API_URL = "http://localhost:8000"

def get_auth_header():
    if st.session_state.auth_token:
        return {"Authorization": f"Bearer {st.session_state.auth_token}"}
    return {}

def login(username: str, password: str) -> bool:
    try:
        # Attempt login
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Store the auth token
            st.session_state.auth_token = data["access_token"]
            
            # Fetch user profile with the new token
            profile_response = requests.get(
                f"{API_URL}/users/me",
                headers={"Authorization": f"Bearer {data['access_token']}"}
            )
            
            if profile_response.status_code == 200:
                # Store user profile in session state
                st.session_state.user_profile = profile_response.json()
                st.success("Login successful!")
                return True
            else:
                print(f"Profile fetch error: {profile_response.status_code}")
                return False
                
        else:
            error_msg = response.json().get("detail", "Invalid credentials")
            st.error(error_msg)
            return False
            
    except Exception as e:
        print(f"Login error details: {str(e)}")  # Detailed error logging
        st.error("Login failed. Please try again.")
        return False

def signup(username: str, email: str, password: str, full_name: str) -> bool:
    try:
        response = requests.post(
            f"{API_URL}/auth/signup",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data["access_token"]
            # Get user profile after signup
            profile_response = requests.get(
                f"{API_URL}/users/me",
                headers={"Authorization": f"Bearer {data['access_token']}"}
            )
            if profile_response.status_code == 200:
                st.session_state.user_profile = profile_response.json()
            st.success("User created successfully! Welcome to VibeTrack!")
            return True
        else:
            error_msg = response.json().get("detail", "Error creating account")
            st.error(error_msg)
            return False
    except Exception as e:
        st.error(f"Signup error: {str(e)}")
        return False

def send_text_activity(text):
    try:
        headers = {}
        if st.session_state.auth_token:
            headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
        
        # Send activity to backend for processing and storage
        response = requests.post(
            f"{API_URL}/log-text", 
            json={"text": text},
            headers=headers
        )
        
        if response.status_code == 200:
            # Add to session state for immediate display
            data = response.json().get("data", {})
            st.session_state.messages.append({
                "timestamp": data.get("timestamp"),
                "category": data.get("category"),
                "processed_text": data.get("processed_text"),
                "raw_text": data.get("raw_text")
            })
            return True
        return False
    except Exception as e:
        print(f"Error sending activity: {str(e)}")
        return False

def get_user_activities():
    try:
        headers = {}
        if st.session_state.auth_token:
            headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
        
        # Get activities from backend storage
        response = requests.get(f"{API_URL}/activities", headers=headers)
        if response.status_code == 200:
            return response.json().get("activities", [])
        return []
    except Exception as e:
        print(f"Error getting activities: {str(e)}")
        return []

def send_voice_activity(audio_data):
    headers = {}
    if st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    if st.session_state.elevenlabs_api_key:
        headers["X-API-Key"] = st.session_state.elevenlabs_api_key
    
    response = requests.post(
        f"{API_URL}/log-voice",
        files={"audio": audio_data},
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        st.session_state.messages.append({
            "text": data["text"],
            "timestamp": datetime.now().isoformat(),
            "category": data.get("category", "Other"),
            "processed_text": data.get("processed_text", data["text"])
        })
        return True
    return False

def get_categories():
    try:
        response = requests.get(
            f"{API_URL}/categories",
            headers=get_auth_header()
        )
        if response.status_code == 200:
            return response.json()
        return {"categories": {}, "suggested": []}
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return {"categories": {}, "suggested": []}

def toggle_voice_agent():
    try:
        headers = {
            **get_auth_header(),
            "X-API-KEY": st.session_state.elevenlabs_api_key
        }
        
        if not st.session_state.recording:
            response = requests.post(
                f"{API_URL}/start-conversation",
                headers=headers
            )
            if response.status_code == 200:
                st.session_state.recording = True
                st.success("Voice agent started successfully!")
                return True
            else:
                st.error(f"Error starting voice agent: {response.text}")
        else:
            response = requests.post(
                f"{API_URL}/end-conversation",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.recording = False
                st.session_state.conversation_id = data.get("conversation_id")
                st.success("Voice conversation ended successfully!")
                st.rerun()
                return True
            else:
                st.error(f"Error ending voice agent: {response.text}")
        return False
    except Exception as e:
        st.error(f"Error toggling voice agent: {str(e)}")
        return False

def logout():
    st.session_state.auth_token = None
    st.session_state.user_profile = None
    st.session_state.messages = []
    st.session_state.recording = False
    st.session_state.voice_enabled = False
    st.session_state.conversation_id = None

def init_session_state():
    """Initialize session state variables"""
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

def record_audio(duration=10, sample_rate=44100):
    """Record audio from microphone"""
    try:
        st.info("🎤 Recording... Speak now!")
        audio_data = sd.rec(int(duration * sample_rate),
                          samplerate=sample_rate,
                          channels=1,
                          dtype='float32')
        sd.wait()
        st.success("✓ Recording complete!")
        return audio_data, sample_rate
    except Exception as e:
        st.error(f"Error recording audio: {str(e)}")
        return None, None

def transcribe_audio(audio_data, sample_rate):
    """Transcribe audio using OpenAI Whisper"""
    try:
        # Save the audio data temporarily
        temp_file = "temp_recording.wav"
        sf.write(temp_file, audio_data, sample_rate)
        
        # Transcribe using OpenAI Whisper
        with open(temp_file, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Clean up temp file
        os.remove(temp_file)
        return transcript.text
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

# Initialize session state at the start of the app
init_session_state()

# Main app logic
if not st.session_state.auth_token or not st.session_state.user_profile:
    st.title("Welcome to VibeTrack")
    
    # Login/Signup tabs
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if login(username, password):
                    st.rerun()  # Rerun the app after successful login

    with tab2:
        with st.form("signup_form", clear_on_submit=True):
            st.markdown('<div class="auth-form">', unsafe_allow_html=True)
            username = st.text_input("Username")
            email = st.text_input("Email")
            name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign Up")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submit:
                if signup(username, email, password, name):
                    st.balloons()  # Add a celebratory effect
                    time.sleep(2)  # Give time to see the success message
                    st.rerun()
                else:
                    st.error("Error creating account")

else:
    # Main application
    if "user_profile" in st.session_state and st.session_state.user_profile:
        st.title(f"Welcome back, {st.session_state.user_profile.get('full_name', 'User')}!")
    else:
        st.title("Welcome to VibeTrack!")
    
    # Logout button
    if st.button("Logout", key="logout"):
        logout()
        st.rerun()
    
    # Left panel - Conversation History
    st.sidebar.subheader("Activity History")
    st.sidebar.markdown('<div class="feature-explanation">View your past activities and track your journey over time.</div>', unsafe_allow_html=True)
    # Fetch activities from backend
    activities = get_user_activities()
    if activities:
        for activity in reversed(activities):  # Show most recent first
            st.sidebar.markdown(f"""
            <div class="chat-message">
                <small>{activity['timestamp']}</small><br>
                <strong>{activity.get('category', 'Personal')}</strong><br>
                {activity['raw_text']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.info("No activities logged yet")

    # Main content area - Two columns for chat/voice and visualizations
    col1, col2 = st.columns([3, 2])

    # Left column - Activity Logging
    with col1:
        st.subheader("Log Activity")
        st.markdown('<div class="feature-explanation">Record your activities through text or voice input to keep track of your daily accomplishments.</div>', unsafe_allow_html=True)
        
        # Add tabs for text and voice input
        text_tab, voice_tab = st.tabs(["Text Input", "Voice Input"])
        
        with text_tab:
            # Text input form
            with st.form(key='activity_form', clear_on_submit=True):
                user_input = st.text_area("Enter your activity:")
                submit_button = st.form_submit_button("Send")
                
                if submit_button and user_input:
                    if send_text_activity(user_input):
                        st.success("Activity logged successfully!")
                    else:
                        st.error("Error logging activity")
        
        with voice_tab:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write("Click 'Record' to start recording your activity (10 seconds)")
            with col_b:
                if st.button("🎤 Record", key="record_button"):
                    audio_data, sample_rate = record_audio()
                    if audio_data is not None:
                        transcribed_text = transcribe_audio(audio_data, sample_rate)
                        if transcribed_text:
                            st.info(f"Transcribed text: {transcribed_text}")
                            if send_text_activity(transcribed_text):
                                st.success("Voice activity logged successfully!")
                            else:
                                st.error("Error logging voice activity")

    # Right column - Insights and Visualizations
    with col2:
        st.subheader("Insights")
        st.markdown('<div class="feature-explanation">Visualize your activity patterns and get meaningful insights about your habits.</div>', unsafe_allow_html=True)
        
        # Make refresh button more prominent
        st.markdown("""
            <style>
            div[data-testid="stButton"] button {
                background: linear-gradient(135deg, #9D4EDD, #6C63FF);
                color: white;
                font-weight: bold;
                border-radius: 20px;
                padding: 0.5rem 1rem;
                width: 100%;
                margin-bottom: 1rem;
            }
            </style>
        """, unsafe_allow_html=True)
        
        refresh_button = st.button("🔄 Refresh Insights", key="refresh_viz")
        
        # Function to load visualization data
        def load_visualization_data():
            headers = {}
            if st.session_state.auth_token:
                headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
            
            try:
                response = requests.get(f"{API_URL}/visualizations", headers=headers)
                if response.status_code == 200:
                    return response.json().get("data", {})
                return None
            except Exception as e:
                st.error(f"Error fetching visualization data: {str(e)}")
                return None

        # Load data either on refresh or initially
        if "viz_data" not in st.session_state or refresh_button:
            with st.spinner("Loading insights..."):
                st.session_state.viz_data = load_visualization_data()

        # Display visualizations if data is available
        if st.session_state.viz_data:
            data = st.session_state.viz_data
            stats = data.get("stats", {})
            
            # Category Distribution
            st.markdown('<div class="visualization-card">', unsafe_allow_html=True)
            st.subheader("Activity Distribution")
            
            distribution = stats.get("distribution", {})
            if distribution:
                fig = go.Figure(data=[go.Pie(
                    labels=list(distribution.keys()),
                    values=list(distribution.values()),
                    marker=dict(colors=[stats.get("color_mapping", {}).get(cat, "#808080") for cat in distribution.keys()]),
                    hole=0.3
                )])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=True,
                    legend=dict(
                        font=dict(color='white'),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    margin=dict(t=30, b=30, l=30, r=30)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No activity data available yet")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Activity Patterns
            st.markdown('<div class="visualization-card">', unsafe_allow_html=True)
            st.subheader("Activity Patterns")
            
            # Daily patterns
            daily_patterns = stats.get("daily_patterns", {})
            if daily_patterns:
                daily_data = []
                for day, categories in daily_patterns.items():
                    for category, count in categories.items():
                        daily_data.append({
                            "Day": day,
                            "Category": category,
                            "Count": count
                        })
                
                if daily_data:
                    df_daily = pd.DataFrame(daily_data)
                    fig_daily = px.bar(df_daily, x="Day", y="Count", color="Category",
                                     title="Daily Activity Patterns")
                    fig_daily.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        showlegend=True,
                        legend=dict(
                            font=dict(color='white'),
                            bgcolor='rgba(0,0,0,0)'
                        ),
                        margin=dict(t=50, b=30, l=30, r=30)
                    )
                    st.plotly_chart(fig_daily, use_container_width=True)
            
            # Activity Trends
            trends = data.get("trends", {})
            if trends:
                st.subheader("Activity Trends")
                st.markdown("""
                    <div style="background-color: rgba(45, 45, 68, 0.7); padding: 20px; border-radius: 10px; margin-top: 10px;">
                        <h4 style="color: #E9D5FF; margin-bottom: 15px;">Summary</h4>
                        <ul style="color: white; list-style-type: none; padding-left: 0;">
                            <li>🗓️ Most active day: {}</li>
                            <li>⏰ Most active hour: {}</li>
                            <li>📊 Most common category: {}</li>
                        </ul>
                    </div>
                """.format(
                    trends.get('most_active_day', 'N/A'),
                    trends.get('most_active_hour', 'N/A'),
                    trends.get('most_common_category', 'N/A')
                ), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Click the refresh button above to load your activity insights!")

    # Divider between sections
    st.divider()

    # AI Chat Assistant (outside of any container)
    st.subheader("AI Chat Assistant")
    st.markdown('<div class="feature-explanation">Get personalized insights and answers about your activities from our AI assistant.</div>', unsafe_allow_html=True)

    # Initialize chat messages in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input (outside of any container)
    if prompt := st.chat_input("Ask me anything about your activities..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        try:
            # Get user activities for context
            activities = get_user_activities()
            activities_context = "Here are your recent activities:\n" + "\n".join([
                f"- {activity['timestamp']}: {activity.get('raw_text', '')} (Category: {activity.get('category', 'Personal')})"
                for activity in activities[-10:]
            ]) if activities else "No previous activities found."
            
            # Get response from Groq
            response = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": """You are a helpful AI assistant for VibeTrack, an activity tracking app. 
                     Help users understand their activities, suggest improvements, and provide insights."""},
                    {"role": "system", "content": activities_context},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=1024
            )
            
            assistant_response = response.choices[0].message.content
            st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.write(assistant_response)
        except Exception as e:
            st.error(f"Error getting response: {str(e)}")

    # Divider between sections
    st.divider()

    # Voice Assistant
    st.subheader("Voice Assistant")
    st.markdown('<div class="feature-explanation">Enjoy heartfelt conversations with our AI, speaking like your granny in Hindi or English, offering motivational advice and uplifting your spirit every day.</div>', unsafe_allow_html=True)
    
    # ElevenLabs widget
    st.components.v1.html("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                .widget-container {
                    width: 100%;
                    min-height: 400px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: transparent;
                }
                elevenlabs-convai {
                    width: 100%;
                    height: 100%;
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <div class="widget-container">
                <elevenlabs-convai 
                    agent-id="fznwkKVgHrHX2VrqsPr4"
                    debug="true"
                    allow-mic="true"
                    allow-camera="false"
                    allow-messages="true"
                    allow-fullscreen="true"
                    style="width: 100%; height: 400px;"
                ></elevenlabs-convai>
            </div>
            <script 
                src="https://elevenlabs.io/convai-widget/index.js" 
                async 
                type="text/javascript"
            ></script>
        </body>
        </html>
    """, height=450) 