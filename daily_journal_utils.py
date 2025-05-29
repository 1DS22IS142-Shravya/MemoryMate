import faiss
import numpy as np
from datetime import datetime

# FAISS index to store embeddings
index = faiss.IndexFlatL2(128)  # 128-dim vector space for storing the journal embeddings
journals = []  # List to store journal entries and their corresponding time

def add_journal_entry(entry):
    """Add a journal entry and its corresponding embedding to the FAISS index."""
    # Convert journal text to a vector
    entry_vec = text_to_vector(entry)
    # Get the current time
    journal_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Add to FAISS index
    index.add(np.array([entry_vec]).astype('float32'))
    # Store journal with its time
    journals.append((entry, journal_time))

def get_journals():
    """Return all stored journal entries."""
    return journals

def text_to_vector(text):
    """Convert text into a 128-dimensional vector (embedding)."""
    ascii_values = [ord(c) for c in text.ljust(128)]
    return np.array(ascii_values[:128])  # 128-dim vector
