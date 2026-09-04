import streamlit as st
import json
import db
from agent import ask_campus_agent

# Initialize Database
db.init_db()

st.set_page_config(page_title="CampusOS", page_icon="🎓", layout="wide")
st.title("🎓 CampusOS — University Platform & AI Agent")

tab_dash, tab_ai = st.tabs(["📊 Campus Data Manager (CRUD)", "🤖 Campus AI Assistant"])

# ==========================================
# TAB 1: DATA MANAGER (CRUD)
# ==========================================
with tab_dash:
    table = st.selectbox(
        "Select System to Manage:", 
        ["schedules", "rooms", "events", "announcements", "assignments"]
    )
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table}")
    rows = [dict(r) for r in cursor.fetchall()]

    st.subheader(f"Current {table.capitalize()} Records ({len(rows)})")
    st.dataframe(rows, use_container_width=True)

    col1, col2 = st.columns(2)

    # 1. Delete Section
    with col1:
        st.write("### 🗑️ Delete Record")
        if rows:
            record_ids = [r["id"] for r in rows]
            selected_id = st.selectbox("Select ID to Delete", record_ids)
            if st.button("Delete Record", type="secondary"):
                cursor.execute(f"DELETE FROM {table} WHERE id = ?", (selected_id,))
                conn.commit()
                st.success(f"Record {selected_id} deleted successfully!")
                st.rerun()
        else:
            st.info("No records found to delete.")

    # 2. Insert/Add Forms for All Systems
    with col2:
        st.write(f"### ➕ Add New Record ({table.capitalize()})")

        if table == "schedules":
            with st.form("add_schedule_form"):
                sc_id = st.text_input("Schedule ID (e.g., SCH101)")
                course_id = st.text_input("Course Code (e.g., CSE 4113)")
                course_name = st.text_input("Course Name")
                section = st.text_input("Section (e.g., A)")
                day = st.selectbox("Day", ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
                start_time = st.text_input("Start Time (e.g., 08:30)")
                end_time = st.text_input("End Time (e.g., 10:00)")
                room_id = st.text_input("Room (e.g., 7A01)")
                instructor = st.text_input("Instructor Name")
                submit_sc = st.form_submit_button("Add Schedule")

                if submit_sc:
                    if sc_id and course_id:
                        cursor.execute(
                            "INSERT INTO schedules VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (sc_id, course_id, course_name, section, day, start_time, end_time, room_id, instructor)
                        )
                        conn.commit()
                        st.success(f"Schedule {sc_id} added successfully!")
                        st.rerun()
                    else:
                        st.error("Schedule ID and Course Code are required!")

        elif table == "rooms":
            with st.form("add_room_form"):
                r_id = st.text_input("Room ID (e.g., 7A05)")
                building = st.text_input("Building", value="Main Building")
                floor = st.text_input("Floor", value="7th Floor")
                capacity = st.number_input("Capacity", min_value=1, max_value=500, value=40)
                room_type = st.selectbox("Type", ["Theory Room", "Computer Lab", "Auditorium"])
                features = st.text_input("Features (Comma separated, e.g., Projector, AC)")
                submit_room = st.form_submit_button("Add Room")

                if submit_room:
                    if r_id:
                        feat_json = json.dumps([f.strip() for f in features.split(",") if f.strip()])
                        cursor.execute(
                            "INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?)",
                            (r_id, building, floor, int(capacity), room_type, feat_json)
                        )
                        conn.commit()
                        st.success(f"Room {r_id} added successfully!")
                        st.rerun()
                    else:
                        st.error("Room ID is required!")

        elif table == "events":
            with st.form("add_event_form"):
                ev_id = st.text_input("Event ID (e.g., EVT001)")
                title = st.text_input("Event Title")
                date = st.text_input("Date (e.g., 2026-09-10)")
                time_slot = st.text_input("Time (e.g., 10:00 - 16:00)")
                location = st.text_input("Location")
                capacity = st.number_input("Max Capacity", min_value=1, max_value=2000, value=100)
                submit_evt = st.form_submit_button("Add Event")

                if submit_evt:
                    if ev_id and title:
                        cursor.execute(
                            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (ev_id, title, date, time_slot, location, int(capacity), 0, "open", json.dumps([]))
                        )
                        conn.commit()
                        st.success(f"Event '{title}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Event ID and Title are required!")

        elif table == "announcements":
            with st.form("add_announcement_form"):
                ann_id = st.text_input("Announcement ID (e.g., ANN001)")
                title = st.text_input("Title")
                content = st.text_area("Content Details")
                date = st.text_input("Date (e.g., 2026-09-04)")
                dept = st.text_input("Target Audience", value="All Students")
                submit_ann = st.form_submit_button("Publish Announcement")

                if submit_ann:
                    if ann_id and title:
                        cursor.execute(
                            "INSERT INTO announcements VALUES (?, ?, ?, ?, ?)",
                            (ann_id, title, content, date, dept)
                        )
                        conn.commit()
                        st.success("Announcement published successfully!")
                        st.rerun()
                    else:
                        st.error("Announcement ID and Title are required!")

        elif table == "assignments":
            with st.form("add_assignment_form"):
                asg_id = st.text_input("Assignment ID (e.g., ASG001)")
                course_id = st.text_input("Course Code (e.g., CSE 4113)")
                title = st.text_input("Assignment Title")
                deadline = st.text_input("Deadline (e.g., 2026-09-15 23:59)")
                description = st.text_area("Description")
                submit_asg = st.form_submit_button("Add Assignment")

                if submit_asg:
                    if asg_id and course_id:
                        cursor.execute(
                            "INSERT INTO assignments VALUES (?, ?, ?, ?, ?)",
                            (asg_id, course_id, title, deadline, description)
                        )
                        conn.commit()
                        st.success(f"Assignment {asg_id} added successfully!")
                        st.rerun()
                    else:
                        st.error("Assignment ID and Course Code are required!")

# ==========================================
# TAB 2: AI ASSISTANT
# ==========================================
with tab_ai:
    st.write("### 💬 Ask Campus AI Senior")
    st.caption("AI reads live data from backend for schedules, room bookings, deadlines, and announcements.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about classes, notices, deadlines, or room bookings..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing campus live database..."):
                response = ask_campus_agent(prompt)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})