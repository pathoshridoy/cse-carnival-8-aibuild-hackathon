import streamlit as st
import json
import db
from agent import ask_campus_agent

# ডাটাবেজ টেবিল চেক ও ইনিশিয়ালাইজেশন
db.init_db()

st.set_page_config(page_title="CampusOS", page_icon="🎓", layout="wide")
st.title("🎓 CampusOS — University Platform & AI Agent")

tab_dash, tab_ai = st.tabs(["📊 Campus Data Manager (CRUD)", "🤖 Campus AI Assistant"])

with tab_dash:
    table = st.selectbox("Select System to Manage:", ["schedules", "rooms", "events", "announcements", "assignments"])
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = [dict(r) for r in cursor.fetchall()]
    
    st.subheader(f"Current {table.capitalize()} Records ({len(rows)})")
    st.dataframe(rows, use_container_width=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 🗑️ Delete Record")
        if rows:
            record_ids = [r["id"] for r in rows]
            selected_id = st.selectbox("Select ID to Delete", record_ids)
            if st.button("Delete Record"):
                cursor.execute(f"DELETE FROM {table} WHERE id = ?", (selected_id,))
                conn.commit()
                st.success(f"Record {selected_id} deleted successfully!")
                st.rerun()
                
    with col2:
        if table == "announcements":
            st.write("### ➕ Post Announcement")
            with st.form("add_notice_form"):
                n_id = st.text_input("ID (e.g. ann-009)")
                n_title = st.text_input("Title")
                n_body = st.text_area("Body")
                n_prio = st.selectbox("Priority", ["high", "medium", "low"])
                n_posted = st.text_input("Posted By", "CSE Department")
                n_exp = st.text_input("Expires (YYYY-MM-DD)", "2026-09-30")
                if st.form_submit_button("Post Announcement"):
                    if n_id and n_title:
                        cursor.execute("INSERT INTO announcements VALUES (?,?,?,?,?,?,?)",
                                       (n_id, n_title, n_body, "2026-09-04", n_prio, n_posted, n_exp))
                        conn.commit()
                        st.success("Announcement posted!")
                        st.rerun()
    conn.close()

with tab_ai:
    st.subheader("💬 Ask Campus AI Senior")
    st.caption("AI reads live data from backend for schedules, room bookings, deadlines, and announcements.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about classes, notices, deadlines, or room bookings..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting live campus database..."):
                try:
                    response = ask_campus_agent(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    err_msg = f"Error: {e}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})