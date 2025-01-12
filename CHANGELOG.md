# Changelog

All notable changes to the VibeTrack project will be documented in this file.

## [Unreleased]

### Added
- User authentication with JWT tokens
- User profile management
- Secure password hashing with bcrypt
- Voice agent integration with ElevenLabs
- Dark theme UI with improved styling
- Draggable circular voice button
- Activity visualization with pie charts
- Real-time conversation history
- User data isolation and multi-user support
- Profile-based activity tracking
- Session management improvements

### Changed
- Updated bcrypt implementation for better compatibility
- Improved error handling in authentication flow
- Enhanced frontend UI with three-panel layout
- Optimized voice recording interface
- Refactored user authentication system
- Enhanced data storage with user isolation
- Improved session state management

### Security
- Implemented JWT-based authentication
- Added secure password hashing with bcrypt
- Protected API endpoints with token verification
- Added API key management for ElevenLabs integration
- Enhanced password validation
- Added user data isolation
- Improved token management

## [0.1.0] - 2024-03-19

### Added
- Initial release of VibeTrack
- Basic activity logging functionality
- Text and voice input support
- Category-based activity tracking
- Simple visualization dashboard

### Technical Details
- FastAPI backend with async support
- Streamlit frontend with custom styling
- ElevenLabs integration for voice processing
- Groq integration for natural language understanding
- JSON-based data storage system

### Dependencies
- FastAPI >= 0.104.1
- Streamlit >= 1.28.0
- Python-dotenv >= 1.0.0
- ElevenLabs >= 0.2.26
- Groq >= 0.3.1
- JWT >= 2.1.0
- bcrypt >= 4.0.1

### Security
- Basic authentication system
- Environment variable management
- API key validation 