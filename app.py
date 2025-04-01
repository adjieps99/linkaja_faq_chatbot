import os
import json
import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("API Key not found. Please set GOOGLE_API_KEY in .env file.")
    st.stop()

# Configure GEMINI API
configure(api_key=API_KEY)
model = GenerativeModel("gemini-1.5-flash-latest")

# Load FAQ data
FAQ_FILE = 'linkaja_pair_question_answer.json'
try:
    with open(FAQ_FILE, 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
except FileNotFoundError:
    st.error(f"FAQ file {FAQ_FILE} not found.")
    st.stop()

questions = [item['question'] for item in faq_data]
answers = [item['answer'] for item in faq_data]

# Initialize embedding model (multilingual for Indonesian support)
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Generate embeddings for FAQ questions
question_embeddings = embedder.encode(questions, show_progress_bar=True)

# Build FAISS index
dimension = question_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(question_embeddings)

# Functions
def retrieve_faqs(query, k=3):
    """Retrieve top-k relevant FAQs based on query."""
    query_embedding = embedder.encode([query])
    distances, indices = index.search(query_embedding, k)
    retrieved_faqs = [faq_data[i] for i in indices[0]]
    return retrieved_faqs, distances[0]

def generate_response(query, retrieved_faqs):
    """Generate response using GEMINI API with retrieved FAQs."""
    prompt = (
        "You are an AI assistant for LinkAja's internal Q&A system. Below are relevant FAQs "
        "to help answer the user's question. Provide an accurate and helpful response.\n\n"
        "Relevant FAQs:\n"
    )
    for i, faq in enumerate(retrieved_faqs, 1):
        prompt += f"{i}. Question: {faq['question']}\n   Answer: {faq['answer']}\n\n"
    prompt += (
        f"User's question: {query}\n\n"
        "Respond based on the FAQs if applicable, or generate a helpful answer if the "
        "question is not directly covered."
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

def compute_quality_score(query, response, retrieved_faqs, distances):
    """Compute quality score if query closely matches an FAQ."""
    SIMILARITY_THRESHOLD = 0.2
    if distances[0] < SIMILARITY_THRESHOLD:
        ground_truth = retrieved_faqs[0]['answer']
        response_embedding = embedder.encode([response])
        ground_truth_embedding = embedder.encode([ground_truth])
        similarity = np.dot(response_embedding, ground_truth_embedding.T) / (
            np.linalg.norm(response_embedding) * np.linalg.norm(ground_truth_embedding)
        )
        return similarity[0][0]
    return None

# Streamlit UI
st.set_page_config(page_title="LinkAja Internal Q&A", layout="wide")
st.header("LinkAja Internal Q&A Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
input_query = st.chat_input("Ask your question:")

if input_query:
    if len(input_query.strip()) < 3:
        bot_message = "Please enter a question with at least 3 characters."
        st.session_state.messages.append({"role": "assistant", "content": bot_message})
        with st.chat_message("assistant"):
            st.markdown(bot_message)
    else:
        # Step 1: Display user question immediately
        st.session_state.messages.append({"role": "user", "content": input_query})
        with st.chat_message("user"):
            st.markdown(input_query)
        
        # Step 2: Show "Typing..." while processing
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Typing...")
        
        # Step 3: Generate response
        retrieved_faqs, distances = retrieve_faqs(input_query)
        response = generate_response(input_query, retrieved_faqs)
        quality_score = compute_quality_score(input_query, response, retrieved_faqs, distances)
        
        # Prepare full response with quality score if applicable
        full_response = response
        if quality_score is not None:
            full_response += f"\n\n**Quality Score**: {quality_score:.2f} (based on similarity to FAQ)"
        
        # Step 4: Simulate typing effect
        words = full_response.split()
        current_response = ""
        for i in range(len(words)):
            current_response = " ".join(words[:i+1])
            message_placeholder.markdown(current_response + "▌")  # Cursor for effect
            time.sleep(0.05)  # Adjust delay (e.g., 0.05s per word)
        message_placeholder.markdown(full_response)
        
        # Step 5: Save final response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Optional: Show retrieved FAQs in sidebar
if st.sidebar.checkbox("Show Retrieved FAQs (Debug)"):
    if 'retrieved_faqs' in locals():
        st.sidebar.subheader("Retrieved FAQs")
        for i, faq in enumerate(retrieved_faqs, 1):
            st.sidebar.write(f"{i}. **Q**: {faq['question']}\n   **A**: {faq['answer']}")