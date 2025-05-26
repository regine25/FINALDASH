import streamlit as st
import pandas as pd
import random

# Load left and right logos properly
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.image("left_logo.png", width=150)

with col3:
    st.image("right_logo.png", width=150)

st.markdown("""
    <h1 style="text-align: center;">Don Honorio Ventura State University</h1>
    <h2 style="text-align: center;">College of Business Studies</h2>
    <h3 style="text-align: center;">Automated Class Schedule</h3>
""", unsafe_allow_html=True)

st.title("📅 Automated Class Schedule")

# ✅ Load the schedule file before using `df`
try:
    df = pd.read_excel("generated_schedulepro.xlsx")  # Load schedule BEFORE filters
except FileNotFoundError:
    st.error("⚠️ Schedule file not found! Please generate the schedule first.")
    df = pd.DataFrame(columns=["Instructor", "Subject", "Room", "Day", "Time Slot", "Section"])  # Empty table

# ✅ Expandable Sidebar: Filters
with st.sidebar.expander("🔍 Filters"):
    if "Instructor" in df.columns:
        selected_instructor = st.selectbox("Filter by Instructor", ["None"] + list(df["Instructor"].dropna().unique()))

    if "Section" in df.columns:
        selected_section = st.selectbox("Filter by Section", ["None"] + list(df["Section"].dropna().unique()))

    if "Room" in df.columns:
        selected_room = st.selectbox("Filter by Room", ["None"] + list(df["Room"].dropna().unique()))

# ✅ Apply Filters to the Schedule
filtered_df = df.copy()

if selected_instructor != "None":
    filtered_df = filtered_df[filtered_df["Instructor"] == selected_instructor]

if selected_section != "None":
    filtered_df = filtered_df[filtered_df["Section"] == selected_section]

if selected_room != "None":
    filtered_df = filtered_df[filtered_df["Room"] == selected_room]

# ✅ Expandable Sidebar: Update Schedule Dynamically with Conflict Detection
with st.sidebar.expander("✏️ Update Schedule"):
    time_slot = st.selectbox("Select Time Slot", df["Time Slot"].unique())
    day = st.selectbox("Select Day", df["Day"].unique())
    new_section = st.selectbox("Select Section", df["Section"].unique())
    new_subject = st.text_input("Enter New Subject")
    new_instructor = st.text_input("Enter Instructor")

    existing_entry = df[(df["Time Slot"] == time_slot) & (df["Day"] == day)]
    if not existing_entry.empty:
        st.warning(f"⚠️ Conflict detected! {existing_entry.iloc[0]['Subject']} is already scheduled for {existing_entry.iloc[0]['Section']} in this slot.")
    else:
        if st.button("Update Schedule"):
            df.loc[(df["Time Slot"] == time_slot) & (df["Day"] == day), ["Section", "Subject", "Instructor"]] = [new_section, new_subject, new_instructor]
            df.to_excel("generated_schedulepro.xlsx", index=False)
            st.success("✅ Schedule Updated Successfully!")

    if st.button("Remove Schedule"):
        df.loc[(df["Time Slot"] == time_slot) & (df["Day"] == day), ["Subject", "Instructor", "Section"]] = ["", "", ""]
        df.to_excel("generated_schedulepro.xlsx", index=False)
        st.success("✅ Schedule Entry Removed Successfully!")

with st.sidebar.expander("📂 Upload Files for Schedule Generation"):
    uploaded_instructors = st.file_uploader("Upload Instructors File (Excel)", type=["xlsx"])
    uploaded_rooms = st.file_uploader("Upload Rooms File (Excel)", type=["xlsx"])
    uploaded_sections = st.file_uploader("Upload Student Sections File (Excel)", type=["xlsx"])
    uploaded_subjects = st.file_uploader("Upload Subjects File (Excel)", type=["xlsx"])


def generate_schedule(instructors, rooms, student_sections, subjects):
    specialization_instructors = {}
    for _, row in instructors.iterrows():
        specialization = row["Specialization"].lower()
        specialization_instructors.setdefault(specialization, []).append(
            (row["Instructor"], row["Day"], row["Time Slot"])
        )

    day_time_rooms = {}
    for _, row in rooms.iterrows():
        key = (row["Day"], row["Time Slot"])
        day_time_rooms.setdefault(key, []).append((row["Room"], row["Max Capacity"]))

    schedule = []
    booked_instructors, booked_rooms, booked_sections = set(), set(), set()

    for _, section in student_sections.iterrows():
        section_name = section["Section"]
        student_count = section["Students"]

        for _, subject in subjects.iterrows():
            subject_name = subject["Subject Name"]
            subject_specialization = subject["Required Specialization"].lower()
            assigned = False

            if subject_specialization in specialization_instructors:
                random.shuffle(specialization_instructors[subject_specialization])
                for instructor, day, time_slot in specialization_instructors[subject_specialization]:
                    instructor_key = (instructor, day, time_slot)
                    section_key = (section_name, day, time_slot)
                    room_key = (day, time_slot)

                    if instructor_key not in booked_instructors and section_key not in booked_sections:
                        if room_key in day_time_rooms:
                            random.shuffle(day_time_rooms[room_key])
                            for room, capacity in day_time_rooms[room_key]:
                                room_full_key = (room, day, time_slot)
                                if capacity >= student_count and room_full_key not in booked_rooms:
                                    schedule.append({
                                        "Section": section_name,
                                        "Subject": subject_name,
                                        "Instructor": instructor,
                                        "Room": room,
                                        "Day": day,
                                        "Time Slot": time_slot
                                    })
                                    booked_instructors.add(instructor_key)
                                    booked_rooms.add(room_full_key)
                                    booked_sections.add(section_key)
                                    assigned = True
                                    break
                            if assigned:
                                break
                    if assigned:
                        break

            if not assigned:
                schedule.append({
                    "Section": section_name,
                    "Subject": subject_name,
                    "Instructor": "Not Assigned",
                    "Room": "Not Assigned",
                    "Day": "Not Scheduled",
                    "Time Slot": "Not Scheduled"
                })

    df_schedule = pd.DataFrame(schedule)
    return df_schedule  # ✅ Ensure function ends correctly
with st.sidebar.expander("⚡ Generate Automated Schedule"):
   if uploaded_instructors and uploaded_rooms and uploaded_sections and uploaded_subjects:
    if st.button("Generate Schedule"):
        instructors = pd.read_excel(uploaded_instructors)
        rooms = pd.read_excel(uploaded_rooms)
        student_sections = pd.read_excel(uploaded_sections)
        subjects = pd.read_excel(uploaded_subjects)
        
        df_generated = generate_schedule(instructors, rooms, student_sections, subjects)
        st.session_state["schedule"] = df_generated
        df_generated.to_excel("generated_schedulepro.xlsx", index=False)
        st.success("✅ Automated Schedule Generated!")

  
    else:  # ✅ Correct placement after a properly formatted if-block
        st.warning("⚠️ Please upload all required files before generating the schedule!")
# ✅ Color-Coded Timetable Format
subject_colors = {
    "College Algebra": "#A8DADC",  # Soft Aqua
    "Business Ethics": "#F1FAEE",  # Off White
    "Financial Accounting": "#C8D5B9",  # Soft Greenish Beige
    "Programming 1": "#BFD8D2",  # Muted Sea Green
    "Database Systems": "#F6D8AE",  # Pastel Peach
    "English Communication": "#D4A5A5",  # Soft Rose
    "Marketing Principles": "#FDE3A7",  # Warm Sand Yellow
    "Physics": "#B8B5FF",  # Lavender Blue
    "Taxation": "#E4C1F9",  # Light Purple
    "Auditing": "#C9A9A6",  # Muted Mauve
    "Law on Obligations": "#A5C1DC",  # Soft Blue
    "Rizal's Life": "#D0E3CC",  # Pastel Sage Green
    "Filipino 1": "#E9DAC1",  # Warm Beige
    "Digital Systems": "#B3DEE2",  # Soft Cyan
    "Web Development": "#C8C8A9",  # Muted Olive
    "Data Structures": "#D8E2DC",  # Misty Grayish Green
    "Managerial Accounting": "#F4E1D2",  # Light Peach
    "Computer Networks": "#AFC2D5",  # Muted Sky Blue
    "Operations Management": "#EAE7DC",  # Subtle Ivory
    "Research Methods": "#E5E5E5",  # Light Gray (Neutral)
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
time_slots = ["7:00 AM- 8:00 AM", "8:00 AM- 9:00 AM", "9:00 AM- 10:00 AM", "10:00 AM- 11:00 AM",
              "11:00 AM- 12:00 PM", "12:00 PM- 1:00 PM", "1:00 PM- 2:00 PM", "2:00 PM- 3:00 PM",
              "3:00 PM- 4:00 PM", "4:00 PM- 5:00 PM", "5:00 PM- 6:00 PM"]

timetable = pd.DataFrame(columns=days, index=time_slots)

for _, row in filtered_df.iterrows():
    subject = row["Subject"]
    color = subject_colors.get(subject, "#E0E0E0")
    entry = f'<div style="background-color:{color}; padding:10px; border-radius:5px; text-align:center; font-weight:bold">{subject}<br>({row["Instructor"]} - {row["Room"]})</div>'
    timetable.loc[row["Time Slot"], row["Day"]] = entry

timetable = timetable.fillna("")  # Remove NaN values

# ✅ Display Updated Schedule with Color Coding
st.write("📌 **Class Schedule Overview**")
st.markdown(timetable.to_html(escape=False), unsafe_allow_html=True)

import os
import streamlit as st
import pandas as pd

# ✅ Store uploaded files separately before processing
if "original_files" not in st.session_state:
    st.session_state["original_files"] = {
        "instructors": uploaded_instructors,
        "rooms": uploaded_rooms,
        "sections": uploaded_sections,
        "subjects": uploaded_subjects
    }

# ✅ Reset Schedule Button: Remove generated file but **keep original uploaded files**
if st.sidebar.button("Reset Schedule", key="reset_schedule_button"):
    try:
        os.remove("generated_schedulepro.xlsx")  # ✅ Remove only the generated file
        st.session_state.pop("schedule", None)  # ✅ Remove stored generated schedule data
        st.success("✅ Schedule reset! Reverting to original uploaded files.")
    except FileNotFoundError:
        st.warning("⚠️ No generated schedule file found!")

# ✅ Load data: Prioritize generated schedule, otherwise use uploaded files
if os.path.exists("generated_schedulepro.xlsx"):
    df = pd.read_excel("generated_schedulepro.xlsx")  # ✅ Load generated schedule file
else:
    st.warning("⚠️ No generated schedule found! Displaying uploaded files instead.")
    df = pd.concat([
        pd.read_excel(st.session_state["original_files"]["instructors"]),
        pd.read_excel(st.session_state["original_files"]["rooms"]),
        pd.read_excel(st.session_state["original_files"]["sections"]),
        pd.read_excel(st.session_state["original_files"]["subjects"])
    ])  # ✅ Preserve uploaded files


