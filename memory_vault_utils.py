import faiss
import numpy as np
import os
from datetime import datetime
from PIL import Image
import io
import base64

# FAISS index for storing text embeddings (descriptions of people, places, events)
index = faiss.IndexFlatL2(128)  # 128-dim vector space for storing the text embeddings
memories = []  # List to store the text and image paths

# Directory to store images
image_directory = "stored_images"
if not os.path.exists(image_directory):
    os.makedirs(image_directory)

def add_memory(description, image):
    """Add a memory with text description and image."""
    # Convert text description to vector (embedding)
    description_vec = text_to_vector(description)
    
    # Generate a unique filename for the image
    image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    image_path = os.path.join(image_directory, image_filename)
    
    # Save the image
    image.save(image_path)

    # Add text vector to FAISS index
    index.add(np.array([description_vec]).astype('float32'))
    
    # Store memory with text and image path
    memories.append((description, image_path))

def get_memories():
    """Return all stored memories (text and image paths)."""
    return memories

def search_memory(query):
    """Search for a memory based on the query description."""
    query_vec = text_to_vector(query)  # Convert query to vector
    D, I = index.search(np.array([query_vec]).astype('float32'), 1)  # Find closest memory
    
    # If a match is found, return the memory description and image path
    if I[0][0] != -1:
        match_description = memories[I[0][0]][0]
        match_image_path = memories[I[0][0]][1]
        return match_description, match_image_path
    else:
        return None, None

def text_to_vector(text):
    """Convert text to a vector (embedding)."""
    ascii_values = [ord(c) for c in text.ljust(128)]
    return np.array(ascii_values[:128])  # 128-dim vector
