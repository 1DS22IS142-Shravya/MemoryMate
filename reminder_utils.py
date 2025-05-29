import faiss
import numpy as np
from datetime import datetime

index = faiss.IndexFlatL2(128)  # 128-dim vector space
reminders = []

def add_reminder(task, reminder_time):
    task_vec = text_to_vector(task)
    time_vec = time_to_vector(reminder_time)
    vector = np.concatenate((task_vec, time_vec)).astype('float32')
    
    index.add(np.array([vector]))
    reminders.append((task, reminder_time))

def get_reminders():
    return reminders

def due_reminders():
    now = datetime.now().strftime("%H:%M")
    return [task for task, time in reminders if time == now]

def remove_reminder(task):
    global reminders
    reminders = [reminder for reminder in reminders if reminder[0] != task]

def time_to_vector(time_str):
    hours, minutes = map(int, time_str.split(":"))
    return np.array([hours, minutes] + [0] * 30)  # 32-dim vector

def text_to_vector(text):
    ascii_values = [ord(c) for c in text.ljust(96)]
    return np.array(ascii_values[:96])  # 96-dim vector
