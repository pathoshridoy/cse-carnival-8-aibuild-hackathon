import json
import sqlite3
import os
from google import genai
from google.genai import types
import db

def query_campus_data(category: str, keyword: str = "") -> str:
    """Queries live campus data for schedules, rooms, events, announcements, or assignments."""
    conn = db.get_connection()
    cursor = conn.cursor()
    valid_tables = ["schedules", "rooms", "events", "announcements", "assignments"]
    if category not in valid_tables:
        return f"Error: Category must be one of {valid_tables}"
    
    cursor.execute(f"SELECT * FROM {category}")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if keyword:
        rows = [r for r in rows if any(keyword.lower() in str(v).lower() for v in r.values())]
    return json.dumps(rows[:15], ensure_ascii=False)

def book_room(room_number: str, date: str, start_time: str, end_time: str, purpose: str) -> str:
    """Books an available room for a specific date and time slot."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bookings FROM rooms WHERE room_number = ?", (room_number,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return f"Room {room_number} does not exist."

    bookings = json.loads(row["bookings"]) if row["bookings"] else []
    
    for b in bookings:
        if b.get("date") == date and not (end_time <= b.get("start_time") or start_time >= b.get("end_time")):
            conn.close()
            return f"Room {room_number} is already booked on {date} between {b.get('start_time')} and {b.get('end_time')}."

    new_booking = {
        "booking_id": f"bk-{len(bookings) + 1:03d}",
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "purpose": purpose
    }
    bookings.append(new_booking)
    cursor.execute("UPDATE rooms SET bookings = ? WHERE room_number = ?", (json.dumps(bookings), room_number))
    conn.commit()
    conn.close()
    return f"Success: Room {room_number} booked for {date} ({start_time} - {end_time}) for '{purpose}'."

def register_event(event_name_or_id: str, student_name: str, student_id: str) -> str:
    """Registers a student for a campus event if capacity permits."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id = ? OR name LIKE ?", (event_name_or_id, f"%{event_name_or_id}%"))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Event not found."

    event = dict(row)
    if event["registered"] >= event["capacity"]:
        conn.close()
        return f"Registration failed: Event '{event['name']}' is already full."

    regs = json.loads(event["registrations"]) if event["registrations"] else []
    regs.append({"student_id": student_id, "name": student_name})
    new_count = event["registered"] + 1
    new_status = "full" if new_count >= event["capacity"] else "upcoming"

    cursor.execute("UPDATE events SET registered = ?, registrations = ?, status = ? WHERE id = ?",
                   (new_count, json.dumps(regs), new_status, event["id"]))
    conn.commit()
    conn.close()
    return f"Success: {student_name} registered for '{event['name']}'."

def ask_campus_agent(prompt: str) -> str:
    client = genai.Client(api_key="AQ.Ab8RN6KlGYEW_3s0Uufw-KhqvA6iP3adQamiRb00Mu6c0UPZaQ")
    tools = [query_campus_data, book_room, register_event]
    system_instruction = (
        "You are CampusOS AI Agent for university students. "
        "Reference current date September 4, 2026. "
        "ALWAYS check live data through query_campus_data tool before answering. "
        "When asked to book or register, only act if complete parameters (time, date, room/event) are provided. "
        "If ambiguous, clarify with user first. Deny unauthorized actions politely."
    )
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=tools,
            system_instruction=system_instruction
        )
    )
    return response.text