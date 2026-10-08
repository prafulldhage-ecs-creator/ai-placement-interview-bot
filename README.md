# 🎙️ AI Placement Interview Practice Bot

> **An intelligent, zero-cost, real-time campus placement interview preparation platform.**
> Practice domain-specific technical & behavioral interview questions by **voice or typing**, receive instant **recruiter-grade scoring & feedback**, and **interview your own project live** in front of your evaluation panel!

---

## 🌟 Why This Project Stands Out (The Placement & Viva Differentiator)

Most college students submit standard CGPA calculators, basic todo apps, or static portfolio websites.
This project is built directly around **campus recruitment drives and technical viva defense**:

- 🤖 **Realistic Human Technical Interviewer (Not a Chatbot)**:
  - **Active Listening & Real-Time Intervention**: Listens while candidate speaks; politely interrupts if candidate goes off-topic, rambles, or makes an immediate blunder.
  - **Conversational Corrections**: Never says "Incorrect. Score: 2/10". Explains *why* an answer is inaccurate and asks probing follow-ups (e.g. Binary Search is logarithmic because the search space halves).
  - **Multi-Turn Adaptive Probing**: Categorizes answers (`CORRECT`, `PARTIALLY_CORRECT`, `INCORRECT`, `VAGUE`, `OFF_TOPIC`, `STRONG`, `IDONTKNOW`, `RAMBLING`) and asks contextual follow-ups using the candidate's actual words.
  - **Thinking Pause Respect**: Distinguishes normal thinking silence (0-6s) from dead air, offering gentle encouragement (*"Take your time."*) rather than interrupting prematurely.
  - **Candid, Professional Tone**: Avoids constant sycophantic praise (*"Awesome!"*); speaks like an authentic corporate panelist (*"Okay."*, *"Let's go one level deeper."*, *"Be more specific."*).
- 👁️ **Camera Presence & Attention Monitoring**:
  - Non-intrusive client-side face & gaze monitoring detecting prolonged looking away, missing face, or secondary persons with a 3-tier subtle warning ladder (`1/3`, `2/3`, `3/3`).
  - Summarizes behavioral presence in the final official placement scorecard!

---

## 🏛️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT (BROWSER)                                 |
|                                                                                   |
|  [ Virtual AI Avatar ] <--- Web Speech Synthesis (TTS) <--- Speaks Question       |
|  [ Microphone Meter ]  ---> Web Speech Recognition (STT) ---> Real-time dictation |
|  [ Candidate Editor ]  ---> Voice + Typing Fallback ---> Submit Answer            |
+------------------------------------------+----------------------------------------+
                                           | HTTP REST POST
                                           v
+-----------------------------------------------------------------------------------+
|                             BACKEND (PYTHON DJANGO 6.1)                           |
|                                                                                   |
|  [ urls.py & views.py ] ---> Session State & Round Management                     |
|  [ models.py ]         ---> SQLite ORM (Questions, Sessions, Submissions)        |
+------------------------------------------+----------------------------------------+
                                           | Invokes Evaluation
                                           v
+-----------------------------------------------------------------------------------+
|                      ZERO-COST NLP SCORING ENGINE (SCIKIT-LEARN)                  |
|                                                                                   |
|  1. Semantic Similarity (35%)   : TF-IDF n-grams (1-2) + Cosine Vector Distance   |
|  2. Concept Coverage (35%)      : Multi-word technical keyword & phrase spotting  |
|  3. Depth & Vocabulary (15%)    : Word count thresholds & lexical diversity       |
|  4. Domain Rubrics (15%)        : STAR for HR, Big-O for DSA, Architecture heuristics |
|                                                                                   |
|  OUTPUT: Score (0-100), Grade (A+ to C), Covered vs Missed Concepts, Strengths,   |
|          Recruiter Improvement Tips, Gold-Standard Model Answer, Follow-up Q.    |
+-----------------------------------------------------------------------------------+
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested and compatible with Python 3.14)
- Pip

### 2. Install Dependencies
```bash
python -m pip install django scikit-learn scipy numpy
```

### 3. Apply Migrations & Seed Placement Questions
```bash
python manage.py migrate
python manage.py seed_questions
```
> Populates the database with 23+ curated high-yield placement questions across Web Dev, DSA, DS, HR, and Project Defense.

### 4. Run the Local Development Server
```bash
python manage.py runserver
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your web browser.

---

## 🧪 Running Automated Tests

Run the full Django test suite to verify the NLP scoring engine, views, and API workflows:
```bash
python manage.py test
```

---

## 🎯 How to Demo Live in Front of the Evaluation Panel

1. **Open the Homepage** (`http://127.0.0.1:8000/`):
   - Showcase the domain selection grid and highlight the **$0.00 API cost** advantage.
2. **Launch "Project Defense" Mode**:
   - Click the orange **"🔥 Project Defense"** pill in the top navigation.
   - The AI Interviewer will ask:
     > *"Walk us through the high-level architecture of this project. Why did you choose Python Django, and how do the frontend, audio, and NLP components integrate?"*
   - Click **"🔊 Speak Question"** to let the bot speak the question out loud.
   - Click the **🎙️ Microphone button** and speak your answer, or type into the editor.
   - Click **"🚀 Submit for AI Evaluation"**.
3. **Showcase the Real-Time Feedback**:
   - Point out the **Score gauge**, **Letter grade**, and **Pill badges** highlighting which concepts you covered and which you missed.
   - Show the **Gold-Standard Model Answer** and the **Expected Recruiter Follow-Up Question**.
4. **Demonstrate Full Mock Interview Simulation**:
   - Go to **Mock Interview** from the navigation bar.
   - Enter your name and run a 5-round sequential placement interview with live countdown timer and simulated panelist.
   - Complete round 5 to reveal the **Official Placement Readiness Scorecard** with the interactive **Chart.js Skill Radar**.
   - Click **"🖨️ Print / Save PDF"** to demonstrate report generation for campus placement cells!

---

## 📁 Project Structure

```
noble-hawking/
├── manage.py
├── placement_bot/
│   ├── settings.py           # Django configuration & static/template setup
│   ├── urls.py               # Root URL dispatcher
│   └── wsgi.py
├── interviews/
│   ├── models.py             # Question, InterviewSession, AnswerSubmission
│   ├── views.py              # Practice room, mock interview, report, APIs
│   ├── urls.py               # App routes
│   ├── ai_engine.py          # Scikit-Learn TF-IDF & heuristic scoring algorithm
│   ├── question_bank.py      # Curated questions across 5 domains
│   ├── tests.py              # Automated test cases
│   └── management/commands/
│       └── seed_questions.py # Database seeder
├── templates/interviews/
│   ├── base.html             # Master responsive layout & navbar
│   ├── landing.html          # Hero, domain picker, platform statistics
│   ├── practice_room.html    # Single-question drill with voice & instant scoring
│   ├── mock_interview.html   # 5-round video-style interview simulation
│   ├── report.html           # Placement Readiness Scorecard & Radar Chart
│   ├── question_bank.html    # Searchable questions & revision cheat sheet
│   └── history.html          # Past sessions and score progression
└── static/
    ├── css/styles.css        # Modern responsive design & animations
    └── js/speech_interviewer.js # Web Speech TTS & STT audio controller
```

---

## 💡 Tech Stack Summary

| Component | Technology | Rationale |
|---|---|---|
| **Backend** | Python Django 6.1 | Robust MVT architecture, ORM, secure sessions |
| **Database** | SQLite3 | Zero-configuration local database |
| **AI Scoring Engine** | Scikit-Learn, NumPy | Fast (<50ms), 100% free, deterministic NLP scoring |
| **Voice Output (TTS)** | Web Speech Synthesis | Native browser text-to-speech with natural cadence |
| **Voice Input (STT)** | Web Speech Recognition | Real-time speech dictation directly in browser |
| **Visualization** | Chart.js | Interactive 4-pillar candidate skill radar |
| **Styling** | Modern Vanilla CSS | Lightweight, responsive glassmorphism UI |
