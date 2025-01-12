# VibeTrack 🎯

A modern activity tracking application with AI-powered insights and voice interactions.

## Features 🌟

### 1. Activity Tracking
- Text-based activity logging
- Voice input using OpenAI Whisper
- Automatic activity categorization
- Real-time activity history

### 2. AI Assistants
- Chat-based AI assistant using Groq
- Voice conversations with ElevenLabs AI
- Personalized insights and recommendations
- Activity pattern analysis

### 3. Visualizations
- Activity distribution by category
- Daily and hourly activity patterns
- Trend analysis and insights
- Interactive charts and graphs

### 4. Categories
- Work
- Health
- Learning
- Personal
- Creative
- Social

## Tech Stack 💻

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: JSON-based storage
- **AI/ML**:
  - Groq API for chat
  - OpenAI Whisper for speech-to-text
  - ElevenLabs for voice conversations
- **Visualization**: Plotly

## Setup 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vibetrack.git
cd vibetrack
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

4. Run the application:
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
streamlit run app.py
```

## Project Structure 📁

```
vibetrack/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── auth.py           # Authentication logic
│   └── storage.py        # Data storage handling
├── frontend/
│   └── app.py           # Streamlit application
├── data/
│   ├── users.json       # User data
│   ├── conversations.json # Activity logs
│   └── categories.json   # Category statistics
└── requirements.txt     # Project dependencies
```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 