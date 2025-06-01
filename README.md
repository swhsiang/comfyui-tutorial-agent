# Comfy UI Tutorial Agent

## Overview
The Comfy UI Tutorial Agent is a sidebar/chatbot interface integrated into the Comfy UI, an open-source user interface for running the Stable Diffusion model locally. The agent assists users by providing instructions, answering questions, and linking to relevant resources such as YouTube videos. The long-term goal is for the agent to create Comfy UI elements based on user requirements.

## Objectives and Goals
- Enhance user experience by providing an interactive help system within Comfy UI.
- Reduce the learning curve for new users by offering step-by-step instructions and resources.
- Increase user engagement and satisfaction by providing quick and accurate responses to user queries.

## Architecture and Components
- **Frontend**: Built using React.js and integrated into the right sidebar of Comfy UI.
- **Backend**: Implemented using Python, handling user queries, processing them using Google Gemini for NLP, and fetching relevant information from various data sources, including Pinecone (vector database).
- **NLP Service**: Google Gemini for understanding user queries and generating appropriate responses.
- **YouTube Integration**: Backend integrates with YouTube's API to fetch video links and timestamps, and stores transcripts and screenshots in a vector database.
- **Vector Database**: Used to store and retrieve information extracted from YouTube videos and other data sources.
- **WebSocket Communication**: Facilitates real-time, bidirectional communication between the frontend and backend.

## Data Flow
1. **Video Processing Flow**: Involves video input, transcript generation, metadata extraction, and data storage.
2. **Chatbot Interaction Flow**: Involves user query, NLP processing, data retrieval, response generation, and user response.

## WebSocket Message Format
- JSON format with fields for type, timestamp, session_id, payload, and sender.

## Technical Specifications
- **Frontend**: React.js
- **Backend**: Python
- **NLP**: Google Gemini
- **Integration**: YouTube API
- **Vector Database**: Pinecone

## Database Schema Design
- **api_key** Table: Stores API keys for client authentication.

## File Structure
- **main.py**: Entry point of the application.
- **video_processing/**: Handles video processing and data storage.
- **chatbot/**: Manages user queries, data retrieval, response generation, and WebSocket communication.
- **rag_system/**: Manages embeddings and Pinecone operations.

## Milestones
1. **Design Phase**: UI/UX design, technical specifications, and documentation.
2. **Development Phase**: Frontend and backend development, video processing, and data retrieval.
3. **Testing Phase**: Unit, integration, and performance testing.
4. **Launch Phase**: Deployment, documentation, and monitoring.

## Risks and Mitigations
- **Technical Complexity**: Research and prototyping for NLP and YouTube API integration.
- **User Adoption**: Clear documentation and tutorials.

## Acceptance Criteria
- Full integration into the Comfy UI sidebar.
- Accurate responses to user queries.
- Links to YouTube videos with specific timestamps.
- Handling at least 100 concurrent users without performance issues.