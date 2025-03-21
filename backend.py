from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from textblob import TextBlob
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os


app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://localhost:3000"}}) 

# Path  dataset 
dataset_path = r"C:\Users\vardh\OneDrive\Desktop\palak ki chize\try\chatbot_data.csv"
model_path = "sentiment_model.pkl"
vectorizer_path = "vectorizer.pkl"

# Train Sentiment Model
if os.path.exists(model_path) and os.path.exists(vectorizer_path):
    print("✅ Loading existing sentiment model...")
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
else:
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"❌ Dataset not found at {dataset_path}. Please check the file path.")

    print("🔄 Training new sentiment model...")
    df = pd.read_csv(dataset_path)

    # Assign sentiment scores using TextBlob
    df["sentiment"] = df["text"].apply(lambda x: TextBlob(str(x)).sentiment.polarity if isinstance(x, str) else 0)

    # Train  Sentiment Model
    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(df["text"])
    y = ["positive" if score > 0 else "negative" if score < 0 else "neutral" for score in df["sentiment"]]

    model = LogisticRegression()
    model.fit(X, y)

    # Save trained model and vectorizer
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

# Configure Gemini API
genai.configure(api_key="AIzaSyDqwDRZoLeaKog1R4oqMKYg8e42W0Blrjc")

# Function to predict sentiment
def analyze_sentiment(text):
    text_vectorized = vectorizer.transform([text])
    return model.predict(text_vectorized)[0]

# Function to generate chatbot response using Gemini API
def get_gemini_response(user_message, sentiment_label):
    prompt = f"""
    You are a mental health chatbot. The user said: "{user_message}".
    The sentiment is detected as {sentiment_label}.

    - If the sentiment is negative, respond in a supportive and empathetic way, offering words of encouragement.
    - If the user asks for a joke, provide a short and funny joke.
    - If the user asks for a video, suggest a relevant YouTube link (e.g., motivational videos, relaxing music, or study tips).
    - Keep your responses short and conversational, like a human being.
    - Always maintain a friendly and empathetic tone.

    Respond appropriately based on the user's input.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)

        print("✅ Gemini Response:", response.text)

        return response.text if hasattr(response, 'text') else "I'm here for you. Stay strong! 😊"

    except Exception as e:
        print("❌ Error with Gemini API:", str(e))
        return "I'm here for you. Stay strong! 😊"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data or not data["message"].strip():
        return jsonify({"error": "Message cannot be empty"}), 400

    user_message = data["message"].strip()

    # Analyze sentiment
    sentiment_label = analyze_sentiment(user_message)

    # Get chatbot response
    bot_response = get_gemini_response(user_message, sentiment_label)

    return jsonify({"response": bot_response})

import sqlite3

def get_chat_history():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    # Fetch distinct chat IDs with their latest message timestamp
    cursor.execute("""
    SELECT chat_id, MAX(timestamp) as last_updated
    FROM conversations
    GROUP BY chat_id
    ORDER BY last_updated DESC
    """)
    chats = cursor.fetchall()

    conn.close()
    return chats

if __name__ == "__main__":
    app.run(port=5001, debug=True)
