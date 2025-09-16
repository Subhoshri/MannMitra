# MannMitra

## Overview
MannMitra is a Generative AI-powered mental wellness platform designed for Indian youth. It provides a confidential, empathetic, and interactive environment where students and young adults can engage with AI-driven companions, track their emotions, and receive personalized guidance. Built with Google Cloud’s Gemini API, MannMitra addresses the stigma and accessibility barriers that often prevent young people from seeking mental health support.

## Problem Statement
Mental health remains a significant societal taboo in India. Young adults face high academic and social pressures, yet affordable, stigma-free, and accessible resources for mental wellness are limited. This creates a gap where individuals hesitate to seek professional help due to cost, unavailability, or fear of judgment.

## Solution
MannMitra offers a personalized and interactive mental wellness experience through AI. It adapts to users’ needs by creating relatable AI personas, analyzing daily reflections, and providing actionable tools for stress management and self-care.

### Key Features

1. Login with Gemini API Key
- Users authenticate by providing their Gemini API key to enable secure access to AI-powered features.

2. Onboarding AI Quiz
- A short quiz helps identify user traits, stress levels, and coping styles.
- The system assigns 2–3 AI personas tailored to the user’s profile.

3. Persona-based AI Chat
- Users can interact with multiple AI personas, each offering distinct support styles (peer listener, mentor, empathetic friend).
- Conversations remain private and judgment-free.

4. AI Journaling and Analysis
- Users can maintain a daily journal.
- Gemini analyzes entries to detect emotions, stress patterns, and overall mood trends.
- Visualizations of emotional progress are provided.

5. Mood-Responsive Planner
- Daily and monthly planners adjust dynamically based on detected mood and stress levels.
- Includes wellness suggestions and task prioritization.

6. Peer Stories
- AI generates short, relatable stories inspired by common youth struggles.
- Encourages users to reflect, build resilience, and feel less isolated.

### System Architecture
```
flowchart TD
    A[User] -->|Quiz, Journals, Chat| B[Streamlit Frontend]
    B --> C[Backend Logic - Python]
    C --> D[Gemini API - Google Cloud]
    C --> E[(Database - SQLite/Firebase)] (Future implementation)
    E --> B
```

### Tech Stack

- Frontend: Streamlit (Python-based interactive UI)
- Backend: Python (persona logic, journaling, planner adaptation)
- AI Integration: Google Cloud Gemini API (chat, story generation, mood analysis, task suggestions)
- Database: SQLite or Firebase (user profiles, journals, planner tasks, mood logs)

### Installation and Setup

- Clone the repository
```
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

- Install dependencies
```
pip install -r requirements.txt
```

- Run the application
```
streamlit run main.py
```

- Enter Gemini API key

When prompted, input your Gemini API key to activate features.

## Deliverables for Hackathon Submission

- Prototype Demo: Streamlit application showcasing all features.
- Presentation Deck: Explaining problem, solution, architecture, and impact.
- Demo Video: Walkthrough of the solution with use-cases.
- GitHub Repository: Complete source code and documentation.

## Author

Developed by [Subhoshri Pal](https://github.com/Subhoshri) as a submission for the GenAI Exchange Hackathon 2025.
