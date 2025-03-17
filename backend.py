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
genai.configure(api_key="AIzaSyD4Q785-hi7YmshqlSj5rirR3220xL7QsE")

# Function to predict sentiment
def analyze_sentiment(text):
    text_vectorized = vectorizer.transform([text])
    return model.predict(text_vectorized)[0]

# Function to generate chatbot response using Gemini API
def get_gemini_response(user_message, sentiment_label):
    prompt = f"""
    You are a mental health chatbot. The user said: "{user_message}".
    The sentiment is detected as {sentiment_label}.

    Respond in a supportive and empathetic way. If the sentiment is negative, offer words of encouragement.
    Provide a **relevant** YouTube link from these categories:
    - Motivational videos for college students
    - Calming music for stress relief
    - Meditation or breathing exercises

    Format the response like this:
    - Message: [Chatbot's response]
    - Video: [YouTube link]

    Keep the response short and natural.
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

if __name__ == "__main__":
    app.run(port=5001, debug=True)
