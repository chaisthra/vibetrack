# VibeTrack on Hugging Face Spaces 🎯

VibeTrack is a modern activity tracking application with AI-powered insights and voice interactions. This version is specifically configured for deployment on Hugging Face Spaces.

## Features

- 📝 Activity tracking through text input
- 🤖 AI Chat Assistant powered by Groq
- 📊 Interactive visualizations for activity insights
- 👵 Voice Assistant with ElevenLabs integration
- 📱 Responsive design for all devices

## Environment Variables Required

Make sure to set these environment variables in your HF Space:

- `GROQ_API_KEY`: Your Groq API key
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `OPENAI_API_KEY`: Your OpenAI API key (optional, for voice transcription)

## Deployment Instructions

1. Fork this repository
2. Create a new Space on Hugging Face
3. Choose "Docker" as the Space SDK
4. Connect your forked repository
5. Add the required environment variables
6. Deploy!

## Usage

1. Create an account or log in
2. Start logging your activities via text
3. Use the AI assistant to get insights
4. View your activity patterns in the visualization panel

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- AI: Groq, ElevenLabs
- Visualization: Plotly
- Authentication: JWT
- Deployment: Docker on HF Spaces 