# CampusOS — Autonomous Campus Management & AI Senior Agent

### Hackathon Project Submission
* **Track / Category:** AI / Web Application
* **Team Name:** Autonomous Builders
* **Team Lead:** Hridoy Sheikh

---

## 📌 Project Overview
**CampusOS** is a unified campus management system and autonomous AI agent designed to streamline university routines, notice broadcasts, room bookings, and assignment tracking.

### 🌟 Key Features
1. **Interactive Data Manager (Full CRUD):**
   - Live viewing, dynamic filtering, and deletion for `schedules`, `rooms`, `events`, `announcements`, and `assignments`.
   - Complete input forms for inserting live records directly into the SQLite database.
2. **Campus AI Senior Assistant:**
   - Powered by Google's `gemini-3.6-flash` model.
   - Grounded on live campus database via Function Calling (`query_campus_data`, `book_room`, `register_event`).
   - Zero hallucination — answers queries based purely on real-time academic records.
3. **Multi-System Architecture:**
   - High-performance, lightweight SQLite3 database (`campusos.db`) managed via Streamlit.

---

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Database:** SQLite3
* **AI Model:** Google Gemini (`gemini-3.6-flash`) via `google-genai`
* **Language:** Python 3.14

---

## 🚀 How to Run Locally

```bash
# 1. Clone Repo
git clone [https://github.com/pathoshridoy/cse-carnival-8-aibuild-hackathon.git](https://github.com/pathoshridoy/cse-carnival-8-aibuild-hackathon.git)
cd cse-carnival-8-aibuild-hackathon

# 2. Virtual Env & Dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit google-genai

# 3. Launch App
streamlit run app.py