# VibeTrack Backend API

This is the backend API component of VibeTrack, providing endpoints for activity tracking and AI-powered interactions.

## Environment Variables
The following environment variables need to be set in the Space:
- `GROQ_API_KEY`: Your Groq API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `JWT_SECRET`: Secret key for JWT token generation (use a secure random string)
- `OPENAI_API_KEY`: Your OpenAI API key for Whisper speech recognition

## API Configuration
- Type: Docker
- Base Image: python:3.10-slim
- Port: 7860
- Health Check: `/health` 