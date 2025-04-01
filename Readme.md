LinkAja Internal Q&A Chatbot
A conversational AI chatbot designed for LinkAja’s internal Q&A system, powered by Google Generative AI and a Retrieval-Augmented Generation (RAG) pipeline. This chatbot provides accurate answers based on a predefined FAQ dataset, with an interactive Streamlit UI that mimics modern messaging apps like WhatsApp or ChatGPT, featuring immediate question display, a "Typing..." indicator, and a dynamic typing effect for responses.

Features
Interactive UI: Questions appear instantly, followed by a "Typing..." indicator and a gradual response display for a seamless chat experience.
RAG Pipeline: Uses Google Generative AI embeddings and Chroma vector store to retrieve relevant FAQs and generate concise, context-aware answers.
FAQ-Based: Answers are grounded in a JSON dataset (linkaja_pair_question_answer.json) containing question-answer pairs with metadata (topic, level).
Multilingual Support: Built with Google’s embedding model, capable of handling Indonesian and other languages effectively.
Quality Assurance: Responses are concise and include a "thanks for asking!" sign-off, with a fallback for unknown queries.
Prerequisites
Before running the chatbot, ensure you have the following:

Python 3.8+: Required for compatibility with dependencies.
Google API Key: Obtain from Google Cloud for the Generative AI API.
FAQ Dataset: A JSON file named linkaja_pair_question_answer.json with the following structure:
json

Collapse

Wrap

Copy
[
    {
        "question": "What is LinkAja?",
        "answer": "LinkAja is a digital payment platform in Indonesia.",
        "topik": "General",
        "level": "Basic"
    },
    ...
]
Installation
Clone the Repository:
bash

Collapse

Wrap

Copy
git clone https://github.com/your-username/linkaja-qa-chatbot.git
cd linkaja-qa-chatbot
Set Up a Virtual Environment (optional but recommended):
bash

Collapse

Wrap

Copy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies: Install the required Python packages using the provided requirements.txt:
bash

Collapse

Wrap

Copy
pip install -r requirements.txt
Contents of requirements.txt:
text

Collapse

Wrap

Copy
streamlit==1.29.0
langchain-google-genai==0.0.11
langchain==0.1.14
chromadb==0.4.24
python-dotenv==1.0.1
Configure Environment Variables: Create a .env file in the project root and add your Google API key:
bash

Collapse

Wrap

Copy
echo "GOOGLE_API_KEY=your-api-key-here" > .env
Prepare the FAQ Dataset: Place your linkaja_pair_question_answer.json file in the project root. Ensure it’s valid JSON with question, answer, topik, and level fields.
Running Locally
Start the Streamlit App:
bash

Collapse

Wrap

Copy
streamlit run app.py
Replace app.py with the name of your Python script (e.g., chatbot.py).
Access the Chatbot: Open your browser to http://localhost:8501 (Streamlit’s default port). You’ll see the "LinkAja Internal Q&A Chatbot" interface.
Interact:
Type a question in the chat input field (e.g., "How do I use LinkAja?").
Press Enter to submit.
Watch your question appear instantly, followed by a "Typing..." indicator, and then the bot’s response with a typing effect.
Containerization & Deployment
1. Dockerization
To containerize the application, use the provided Dockerfile. This ensures consistency across environments.

Dockerfile
dockerfile

Collapse

Wrap

Copy
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
Building and Running the Docker Container
Build the Docker Image:
bash

Collapse

Wrap

Copy
docker build -t your-docker-repo/linkaja-chatbot:latest .
Run the Container:
bash

Collapse

Wrap

Copy
docker run -p 8501:8501 your-docker-repo/linkaja-chatbot:latest
Access the App: Open http://localhost:8501 in your browser.
2. Kubernetes Deployment
Kubernetes manifests are provided for deploying the chatbot with scalability and security in mind.

Kubernetes Manifests
Deployment.yaml
yaml

Collapse

Wrap

Copy
apiVersion: apps/v1
kind: Deployment
metadata:
  name: linkaja-chatbot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: linkaja-chatbot
  template:
    metadata:
      labels:
        app: linkaja-chatbot
    spec:
      containers:
      - name: linkaja-chatbot
        image: your-docker-repo/linkaja-chatbot:latest
        ports:
        - containerPort: 8501
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: linkaja-secrets
              key: GOOGLE_API_KEY
Service.yaml
yaml

Collapse

Wrap

Copy
apiVersion: v1
kind: Service
metadata:
  name: linkaja-chatbot-service
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8501
  selector:
    app: linkaja-chatbot
Secret.yaml
yaml

Collapse

Wrap

Copy
apiVersion: v1
kind: Secret
metadata:
  name: linkaja-secrets
type: Opaque
data:
  GOOGLE_API_KEY: <base64-encoded-api-key>
Ingress.yaml (Optional)
yaml

Collapse

Wrap

Copy
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: linkaja-chatbot-ingress
spec:
  rules:
  - host: chatbot.linkaja.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: linkaja-chatbot-service
            port:
              number: 80
Steps to Deploy to Kubernetes
Build and Push Docker Image:
Build the image: docker build -t your-docker-repo/linkaja-chatbot:latest .
Push it to your repository: docker push your-docker-repo/linkaja-chatbot:latest
Prepare the Secret:
Encode your API key: echo -n 'your-api-key' | base64
Update Secret.yaml with the encoded value under GOOGLE_API_KEY.
Apply Kubernetes Manifests:
Apply the Secret: kubectl apply -f Secret.yaml
Apply the Deployment: kubectl apply -f Deployment.yaml
Apply the Service: kubectl apply -f Service.yaml
(Optional) Apply the Ingress: kubectl apply -f Ingress.yaml
Verify the Deployment:
Check pod status: kubectl get pods
Test the service internally (e.g., via kubectl port-forward) or externally (if using Ingress).
Project Structure
text

Collapse

Wrap

Copy
linkaja-qa-chatbot/
├── app.py                    # Main Streamlit application script
├── linkaja_pair_question_answer.json  # FAQ dataset in JSON format
├── .env                      # Environment variables (Google API key)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── kubernetes/               # Kubernetes manifests
│   ├── Deployment.yaml
│   ├── Service.yaml
│   ├── Secret.yaml
│   └── Ingress.yaml          # Optional
└── README.md                 # This file
Code Overview
The main script (app.py) includes:

Environment Setup: Loads the Google API key and FAQ data.
RAG Pipeline: Uses GoogleGenerativeAIEmbeddings for vector embeddings, Chroma for vector storage, and ChatGoogleGenerativeAI for response generation.
Streamlit UI: Implements a chat interface with:
Immediate question display using st.chat_message.
"Typing..." feedback via st.empty.
Typing effect for responses with a word-by-word animation.
Example Interaction
text

Collapse

Wrap

Copy
You: What is LinkAja?
Bot: Typing...
Bot: LinkAja is a digital payment platform in Indonesia. Thanks for asking!
Troubleshooting
API Key Error: Ensure GOOGLE_API_KEY is correctly set in .env or in the Kubernetes Secret.
JSON File Not Found: Verify linkaja_pair_question_answer.json exists and is valid JSON.
Slow Response: Check your internet connection (API calls) or reduce the k value in the retriever for faster FAQ retrieval.
Contributing
Feel free to submit issues or pull requests to improve the chatbot. Suggestions for enhancing the UI, optimizing performance, or expanding the FAQ dataset are welcome!

License
This project is licensed under the MIT License. See the  file for details (create one if needed).

Acknowledgments
Built with Streamlit, LangChain, and Google Generative AI.
Inspired by modern chatbot interfaces like ChatGPT.
Screenshots
Chatbot Interface: [Insert screenshot here]
Successful Container Build: [Insert screenshot here]
Video Demo
[Link to video or embedded file]
This README.md provides a comprehensive guide for setting up, running, and deploying the LinkAja Internal Q&A Chatbot. Enjoy using it!