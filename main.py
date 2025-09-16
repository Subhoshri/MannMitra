import streamlit as st
import os
import requests
import json
import time
from datetime import date, timedelta
import calendar

def get_gemini_api_key():
    return st.secrets["GEMINI_API_KEY"]

def get_gemini_response(prompt, persona_system_instruction=""):
    """
    Sends a prompt to the Gemini API and returns the response.
    Includes a retry mechanism for transient errors.
    """
    if "gemini_api_key" not in st.session_state:
        st.error("API key not found in session state. Please log in again.")
        return "An error occurred. Please log in again."
    
    api_key = st.session_state.gemini_api_key
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    if persona_system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": persona_system_instruction}]}

    try:
        for i in range(3):
            response = requests.post(api_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                return text
            elif response.status_code == 429:
                time.sleep(2 ** i)
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return "An error occurred with the API call."
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return "An error occurred with the network request."
    
    return "Failed to get a response after multiple retries."

def check_crisis():
    """Checks for a persistent negative mood and displays a crisis alert."""
    if "journal_entries" not in st.session_state or not st.session_state.journal_entries:
        return
    
    negative_moods = {"sad", "stressed", "anxious"}
    negative_count = 0
    
    last_three_days_moods = [entry["mood"].lower() for entry in st.session_state.journal_entries[-3:]]
    
    for mood in last_three_days_moods:
        if mood in negative_moods:
            negative_count += 1
            
    if negative_count >= 3:
        st.error(
            f"""
            <div style="text-align: center; border: 2px solid red; padding: 10px; border-radius: 10px; font-weight: bold;">
                <h3 style="color: red;">Feeling Overwhelmed?</h3>
                <p>It seems like you've been going through a tough time recently. Remember that help is always available.</p>
                <p>📞 Crisis Helpline: 1-800-273-8255</p>
                <p>💬 Text Helpline: Text "HOME" to 741741</p>
                <p>A trusted contact can also provide support.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")
        if st.button("Notify Trusted Contact (Simulated)"):
            st.info("A notification has been sent to your trusted contact.")

def login_page():
    """Renders the login page for API key input."""
    st.title("Welcome to MannMitra")
    st.markdown("Please log in with your Gemini API key to get started.")

    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    
    if st.button("Login"):
        if api_key:
            st.session_state.logged_in = True
            st.session_state.gemini_api_key = api_key
            st.rerun()
        else:
            st.warning("Please enter your API key to proceed.")

def personality_quiz_page():
    """Renders the Personality Quiz page and determines initial persona."""
    st.title("Let's Get to Know You")
    st.subheader("A Quick Mental Wellness Quiz")
    st.write("This quiz will help us tailor the AI's responses to your needs. There are no right or wrong answers!")
    
    quiz_questions = [
        {
            "question": "When you're facing a problem, your first instinct is to:",
            "options": {
                "A": "Talk it out with a friend or a trusted person.",
                "B": "Break it down into actionable steps and create a plan.",
                "C": "Find someone who has gone through something similar.",
                "D": "Reflect on your feelings and try to understand them.",
                "E": "Distract yourself with a fun activity or hobby.",
                "F": "Run away from it and hope it resolves itself.",
            },
            "scores": {"A": "Supportive Friend", "B": "Motivational Mentor", "C": "Peer Companion", "D": "Supportive Friend", "E": "Peer Companion", "F": "Peer Companion"}
        },
        {
            "question": "How do you recharge after a stressful week?",
            "options": {
                "A": "Spending quality time with friends and family.",
                "B": "Setting a new goal or learning a new skill.",
                "C": "Engaging in a shared hobby or a social activity.",
                "D": "Journaling or meditating to process your thoughts.",
                "E": "Watching movies or playing games to unwind.",
                "F": "Avoiding social interactions and staying alone.",
            },
            "scores": {"A": "Supportive Friend", "B": "Motivational Mentor", "C": "Peer Companion", "D": "Supportive Friend", "E": "Peer Companion", "F": "Peer Companion"}
        },
        {
            "question": "You feel most motivated when:",
            "options": {
                "A": "You have a strong support system cheering you on.",
                "B": "You have a clear task list and a deadline to meet.",
                "C": "You see how others have overcome similar challenges.",
                "D": "You take time to reflect on your personal growth.",
                "E": "You engage in fun activities that make you happy.",
                "F": "You avoid thinking about your responsibilities.",
            },
            "scores": {"A": "Supportive Friend", "B": "Motivational Mentor", "C": "Peer Companion", "D": "Supportive Friend", "E": "Peer Companion", "F": "Peer Companion"}
        }
    ]

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}

    for i, q in enumerate(quiz_questions):
        st.subheader(f"Question {i+1}")
        answer = st.radio(q["question"], list(q["options"].values()), key=f"q{i}")
        st.session_state.quiz_answers[f"q{i}"] = answer

    if st.button("Submit Quiz"):
        if len(st.session_state.quiz_answers) < len(quiz_questions):
            st.warning("Please answer all questions before submitting.")
        else:
            persona_counts = {"Supportive Friend": 0, "Motivational Mentor": 0, "Peer Companion": 0}
            for i, q in enumerate(quiz_questions):
                answer_text = st.session_state.quiz_answers[f"q{i}"]
                for key, value in q["options"].items():
                    if value == answer_text:
                        persona_counts[q["scores"][key]] += 1
            
            most_frequent_persona = max(persona_counts, key=persona_counts.get)
            
            st.session_state.selected_persona = most_frequent_persona
            st.session_state.quiz_complete = True
            st.success(f"Quiz complete! Your primary persona is: **{most_frequent_persona}**")
            st.rerun()

def home_page():
    """Renders the Home page with a welcome message."""
    st.header("Welcome to MannMitra")
    st.markdown(
        """
        <p style="font-size: 1.1em; line-height: 1.6;">
            MannMitra is your personal mental wellness companion. This app is designed to help you
            understand your emotions, manage daily tasks, and connect with supportive resources.
            Explore the features in the sidebar to get started:
        </p>
        <ul style="font-size: 1.1em; line-height: 1.6;">
            <li>Personality Quiz: Discover your inner strengths.</li>
            <li>Chat: Talk to an empathetic AI companion.</li>
            <li>Journal: Reflect on your day and get insights.</li>
            <li>Planner: Organize your tasks based on your mood.</li>
            <li>Stories: Read uplifting, relatable stories.</li>
        </ul>
        <p style="font-size: 1.1em; line-height: 1.6;">
            Your data is stored securely in your browser's session and is not shared with anyone.
        </p>
        """,
        unsafe_allow_html=True
    )

def chat_page():
    """Renders the Chat page."""
    st.header("Chat")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "personas" not in st.session_state:
        st.session_state.personas = {
            "Supportive Friend": "You are a warm, empathetic friend who listens without judgment and offers encouragement.",
            "Motivational Mentor": "You are a direct and positive mentor who provides structured advice, helps set goals, and pushes for action.",
            "Peer Companion": "You are a peer who shares relatable experiences and understands struggles from a similar point of view.",
            "Calm Counselor": "You are a calm and soothing counselor who helps users navigate their feelings with patience and understanding.",
            "Cheerful Coach": "You are an upbeat and energetic coach who motivates users with positivity and practical tips.",
            "Reflective Guide": "You are a thoughtful guide who encourages self-reflection and personal growth through insightful questions and observations.",
        }

    # Persona selection
    st.subheader("Choose your AI Companion")
    selected_persona = st.selectbox(
        "Select a persona:",
        list(st.session_state.personas.keys()),
        index=list(st.session_state.personas.keys()).index(st.session_state.selected_persona) if "selected_persona" in st.session_state else 0,
        help="The AI's response style will change based on your selection."
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is on your mind?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("MannMitra is thinking..."):
                persona_instruction = st.session_state.personas[selected_persona]
                ai_response = get_gemini_response(f"Persona: {selected_persona}. User message: {prompt}", persona_instruction)
            
            message_placeholder = st.empty()
            full_response = ""
            for chunk in ai_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    if st.button("Start New Chat"):
        st.session_state.messages = []
        st.rerun()
    
def journal_page():
    """Renders the Journal page."""
    st.header("Journal")
    st.write("Write about your day and get instant insights.")
    
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []

    journal_text = st.text_area("How are you feeling today?", height=200)

    if st.button("Analyze Journal Entry"):
        if journal_text:
            with st.spinner("Analyzing your entry..."):
                analysis_prompt = (
                    f"Analyze the following journal entry for mood, summarize it, and suggest a coping tip:\n\n"
                    f"Journal Entry:\n{journal_text}\n\n"
                    f"Please provide the output in the following format:\n"
                    f"Mood: [mood (e.g., happy, sad, stressed, anxious, calm)]\n"
                    f"Summary: [2-3 sentence summary]\n"
                    f"Coping Tip: [One specific, actionable coping tip or micro-intervention]"
                )
                analysis_result = get_gemini_response(analysis_prompt)
                
                try:
                    lines = analysis_result.split('\n')
                    mood = lines[0].replace("Mood:", "").strip()
                    summary = lines[1].replace("Summary:", "").strip()
                    tip = lines[2].replace("Coping Tip:", "").strip()
                    
                    st.success("Analysis complete!")
                    st.subheader("Your Insights")
                    st.markdown(f"Mood: {mood}")
                    st.markdown(f"Summary: {summary}")
                    st.markdown(f"Coping Tip: {tip}")

                    entry = {
                        "date": time.strftime("%Y-%m-%d"),
                        "text": journal_text,
                        "mood": mood,
                        "summary": summary,
                        "tip": tip
                    }
                    st.session_state.journal_entries.append(entry)
                    st.info("Journal entry saved!")
                    
                except (IndexError, AttributeError):
                    st.error("Could not parse the API response. Please try again.")
        else:
            st.warning("Please write something in your journal before analyzing.")

    st.markdown("---")
    st.subheader("Past Journal Entries")
    if not st.session_state.journal_entries:
        st.info("You don't have any saved journal entries yet.")
    else:
        for i, entry in enumerate(reversed(st.session_state.journal_entries)):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"{entry['date']} - Mood: {entry['mood']}")
                st.write(f"Summary: {entry['summary']}")
            with col2:
                if st.button("Delete", key=f"delete_journal_{i}"):
                    original_index = len(st.session_state.journal_entries) - 1 - i
                    del st.session_state.journal_entries[original_index]
                    st.rerun()
            st.markdown("---")


def planner_page():
    """Renders the Planner page with tasks based on mood history."""
    st.header("Planner")
    st.write("Plan your day with tasks tailored to your emotional state.")

    st.subheader(f"{date.today().strftime('%B %Y')}")
    
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(date.today().year, date.today().month)
    today = date.today()

    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-weight: bold; padding-bottom: 5px;">
            {' '.join([f'<div>{day}</div>' for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']])}
        </div>
        """,
        unsafe_allow_html=True
    )

    for week in month_days:
        week_html = ""
        for day in week:
            if day == 0:
                week_html += f'<div class="day-cell"></div>'
            else:
                is_today = today.day == day
                day_class = "today" if is_today else ""
                week_html += f'<div class="day-cell {day_class}">{day}</div>'
        st.markdown(
            f"""
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); text-align: center;">
                {week_html}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    if "journal_entries" not in st.session_state or not st.session_state.journal_entries:
        st.info("Write a few journal entries to get personalized task suggestions.")
        return

    last_mood = st.session_state.journal_entries[-1]["mood"].lower()
    low_moods = {"sad", "stressed", "anxious"}

    st.subheader("Today's Suggested Tasks")
    
    if last_mood in low_moods:
        task_type = "self-care and small, achievable tasks (e.g., drink water, stretch, take a short walk)"
    else:
        task_type = "productive and challenging tasks (e.g., study for 30 minutes, organize your desk, work on a project)"
    
    task_prompt = (
        f"Generate a list of 3-5 {task_type}. "
        f"Each task should be on a new line, starting with a bullet point."
    )
    
    with st.spinner("Generating tasks..."):
        tasks = get_gemini_response(task_prompt)
    
    if tasks:
        st.markdown(tasks)

def stories_page():
    """Renders the Stories page with AI-generated content."""
    st.header("Stories")
    st.write("Read inspiring stories from peers who understand.")

    current_mood = "a student"
    if "journal_entries" in st.session_state and st.session_state.journal_entries:
        current_mood = st.session_state.journal_entries[-1]["mood"]

    story_prompt = (
        f"Generate 3 short, peer-simulated stories about student struggles. "
        f"Each story should be related to a different realistic theme (e.g., exams, family pressure, friendships). "
        f"The stories should be relatable to someone feeling {current_mood}."
        f"For each story, provide a title, a short content section, and a simple coping action. "
        f"Format each story as follows:\n\n"
        f"Title: [Story Title]\n"
        f"Content: [Story Content]\n"
        f"Coping Action: [One Coping Action]\n\n"
        f"Example:\nTitle: The Procrastination Monster\nContent: I had a huge project due but couldn't focus. I just kept watching videos and felt more and more stressed.\nCoping Action: Start with a 15-minute timer and just begin."
    )
    
    if st.button("Generate New Stories"):
        with st.spinner("Generating stories..."):
            stories_raw = get_gemini_response(story_prompt)
            if stories_raw:
                st.session_state["stories"] = stories_raw
    
    if "stories" in st.session_state:
        stories = st.session_state["stories"].split("\n\n")
        st.subheader("Stories for you")
        
        with st.container():
            st.markdown(
                """
                <style>
                .scrollable-container {
                    max-height: 600px;
                    overflow-y: auto;
                    border: 1px solid #444;
                    border-radius: 10px;
                    padding: 15px;
                }
                .story-card {
                    background-color: #2c2c2c;
                    border-left: 5px solid #6c757d;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
            for story_block in stories:
                lines = story_block.strip().split("\n")
                if len(lines) >= 3:
                    title = lines[0].replace("Title:", "").strip()
                    content = lines[1].replace("Content:", "").strip()
                    action = lines[2].replace("Coping Action:", "").strip()
                    
                    st.markdown('<div class="story-card">', unsafe_allow_html=True)
                    st.markdown(f"**{title}**")
                    st.write(content)
                    st.write(f"**Coping Action:** *{action}*")
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

def main():
    """
    Main function to set up the Streamlit app and navigation.
    """
    st.set_page_config(
        page_title="MannMitra",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #121212;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #bb86fc; /* A bright purple for headings */
        }
        .stTextInput label, .stTextArea label, .stSelectbox label {
            color: #ffffff;
        }
        .stTextInput > div > div > input, .stTextArea > textarea {
            background-color: #2c2c2c;
            color: #ffffff;
            border-radius: 5px;
            border: 1px solid #555;
        }
        .stButton > button {
            background-color: #03dac6; /* A teal color for buttons */
            color: #000000;
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        .stMarkdown p {
            color: #e0e0e0;
        }
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            color: #fff;
        }
        .day-cell {
            width: 40px;
            height: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 5px;
            font-weight: bold;
            margin: 2px;
        }
        .day-cell.today {
            background-color: #03dac6;
            color: #121212;
            border-radius: 50%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "quiz_complete" not in st.session_state:
        st.session_state.quiz_complete = False

    if not st.session_state.logged_in:
        login_page()
    elif not st.session_state.quiz_complete:
        personality_quiz_page()
    else:
        st.sidebar.title("MannMitra")
        
        pages = {
            "Home": home_page,
            "Chat": chat_page,
            "Journal": journal_page,
            "Planner": planner_page,
            "Stories": stories_page,
        }

        selection = st.sidebar.selectbox("Go to", list(pages.keys()))

        check_crisis()

        page_function = pages[selection]
        page_function()

if __name__ == "__main__":
    main()