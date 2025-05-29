import streamlit as st
from datetime import datetime
import threading
import time
from reminder_utils import add_reminder, get_reminders, due_reminders, remove_reminder
from daily_journal_utils import add_journal_entry, get_journals
from voice_utils import listen_to_user, speak
from memory_vault_utils import add_memory, get_memories, search_memory
from PIL import Image

st.set_page_config(page_title="All-in-One App", layout="centered")

# Sidebar for navigation between sections
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose a section", ["MemoryMate", "Daily Journal", "Memory Vault"])

# Function to run MemoryMate – Smart Voice Reminders
def memory_mate():
    st.markdown("## 🧠 MemoryMate – Smart Voice Reminders")
    st.write("Say something like: `Remind me to take medicine at 9 PM`")

    if "reminder_list" not in st.session_state:
        st.session_state.reminder_list = []

    # Manual input field for adding reminders as a backup
    manual_task = st.text_input("Or manually type a reminder", placeholder="Remind me to take medicine at 9 PM")
    manual_time = st.text_input("Time", placeholder="e.g. 9 PM")

    if st.button("Add Reminder Manually"):
        if manual_task and manual_time:
            try:
                time_part = manual_time.strip().upper().replace(".", "").replace(" ", "")
                if "PM" in time_part or "AM" in time_part:
                    time_obj = datetime.strptime(time_part, "%I:%M%p") if ":" in time_part else datetime.strptime(time_part, "%I%p")
                    formatted_time = time_obj.strftime("%H:%M")
                    add_reminder(manual_task, formatted_time)
                    st.session_state.reminder_list.append((manual_task, formatted_time))
                    st.success("Manual reminder added!")
                else:
                    st.error("Couldn't detect a valid time (e.g., 9 PM).")
            except Exception as e:
                st.error(f"Failed to parse reminder: {e}")
        else:
            st.warning("Please fill both task and time fields.")

    # Voice recording section
    if st.button("🎙️ Record Reminder"):
        with st.spinner("Listening..."):
            spoken_text = listen_to_user().lower()
            st.success(f"You said: {spoken_text}")

            # Basic parsing: "remind me to take medicine at 9 pm"
            if "remind me to" in spoken_text and "at" in spoken_text:
                try:
                    task = spoken_text.split("remind me to")[1].split("at")[0].strip()
                    time_part = spoken_text.split("at")[1].strip().upper().replace(".", "").replace(" ", "")
                    if "PM" in time_part or "AM" in time_part:
                        time_obj = datetime.strptime(time_part, "%I:%M%p") if ":" in time_part else datetime.strptime(time_part, "%I%p")
                        formatted_time = time_obj.strftime("%H:%M")
                        add_reminder(task, formatted_time)
                        st.session_state.reminder_list.append((task, formatted_time))
                        st.success("Reminder added!")
                    else:
                        st.error("Couldn't detect a valid time (e.g., 9 PM).")
                except Exception as e:
                    st.error(f"Failed to parse reminder: {e}")
            else:
                st.warning("Please follow the format: Remind me to [task] at [time]")

    # Display upcoming reminders only
    st.markdown("## 📋 Upcoming Reminders")
    current_time = datetime.now().strftime("%H:%M")
    upcoming_reminders = [r for r in get_reminders() if r[1] > current_time]

    for task, t in upcoming_reminders:
        st.markdown(f"- **{task}** at 🕒 {t}")

    # Background reminder thread
    def reminder_loop():
        while True:
            due = due_reminders()
            for task in due:
                speak(f"It's time to {task}")
                # Remove task after it's spoken
                remove_reminder(task)
            time.sleep(60)  # Check every minute

    if st.button("🔔 Start Reminder Checker"):
        threading.Thread(target=reminder_loop, daemon=True).start()
        st.success("Reminder checker started.")

# Function for Daily Journal – Write or Speak Your Day
def daily_journal():
    st.markdown("## 📝 Daily Journal – Write or Speak Your Day")

    # Display the journal entries
    st.markdown("### 📜 Your Journal Entries")
    for entry, timestamp in get_journals():
        st.markdown(f"- **{timestamp}**: {entry}")

    # Manual journal input field
    manual_entry = st.text_area("Write your journal for today...", placeholder="Write your day here...")

    if st.button("Save Journal Entry"):
        if manual_entry:
            add_journal_entry(manual_entry)
            st.success("Journal entry saved!")
        else:
            st.warning("Please write something before saving.")

    # Voice recording section for journal
    if st.button("🎙️ Record Journal"):
        with st.spinner("Listening..."):
            spoken_text = listen_to_user().lower()
            st.success(f"You said: {spoken_text}")

            if spoken_text:
                add_journal_entry(spoken_text)
                st.success("Journal entry saved!")
            else:
                st.warning("No speech detected. Please try again.")

    # Background thread to speak journal summaries
    def journal_summary_loop():
        while True:
            if get_journals():  # Check if there are any journal entries
                last_entry, _ = get_journals()[-1]  # Get the last journal entry
                speak(f"Your last journal entry: {last_entry}")
            time.sleep(3600)  # Check every hour for a summary

    if st.button("🔔 Start Journal Summary Checker"):
        threading.Thread(target=journal_summary_loop, daemon=True).start()
        st.success("Journal summary checker started.")

# Function for Memory Vault – Store Past People, Places, Events
def memory_vault():
    st.markdown("## 🧠 Memory Vault – Store Past People, Places, Events")

    # Display stored memories (text + images)
    st.markdown("### 🗂️ Your Stored Memories")
    memories = get_memories()
    for description, image_path in memories:
        st.markdown(f"#### {description}")
        image = Image.open(image_path)
        st.image(image, caption=description, use_column_width=True)

    # Input fields for adding a new memory
    memory_description = st.text_area("Describe your memory (person, place, event)")
    uploaded_image = st.file_uploader("Upload an image related to your memory", type=["jpg", "jpeg", "png"])

    if st.button("Save Memory"):
        if memory_description and uploaded_image:
            # Load the uploaded image
            image = Image.open(uploaded_image)
            
            # Add memory with description and image
            add_memory(memory_description, image)
            st.success("Memory saved!")
        else:
            st.warning("Please provide both a description and an image.")

    # Search for a specific memory (e.g., asking about your daughter)
    query = st.text_input("Ask about a person (e.g., Who is my daughter?)")

    if query:
        result_description, result_image_path = search_memory(query)
        if result_description:
            # Display the result only once (showing the image once when querying)
            st.markdown(f"### {result_description}")
            
            # Check if the image is not displayed above already
            if result_image_path:
                image = Image.open(result_image_path)
                st.image(image, caption=result_description, use_column_width=True)
        else:
            st.warning("No memory found for your query.")

# Main app
def main():
    if app_mode == "MemoryMate":
        memory_mate()
    elif app_mode == "Daily Journal":
        daily_journal()
    elif app_mode == "Memory Vault":
        memory_vault()

if __name__ == "__main__":
    main()
