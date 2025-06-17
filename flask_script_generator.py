
import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7
)

# Set up prompt template
template = """You are a tech content creator who writes punchy, engaging 60-second video scripts.

Topic: {topic}
Summary: {summary}

Write a short script for a YouTube Shorts video. Start with a hook, mention key facts, and close with an exciting or funny remark. Keep it under 130 words.
"""

prompt = PromptTemplate(
    input_variables=["topic", "summary"],
    template=template
)

# Flask app setup
app = Flask(__name__)

# Helper function to extract topic and summary from a URL
def extract_info_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else "Unnamed Tech"
        description_tag = soup.find("meta", attrs={"name": "description"})
        summary = description_tag["content"].strip() if description_tag and "content" in description_tag.attrs else "No summary available."

        return title, summary
    except Exception as e:
        return "Error", str(e)

# Route to generate script
@app.route("/generate", methods=["POST"])
def generate_script():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    topic, summary = extract_info_from_url(url)

    if topic == "Error":
        return jsonify({"error": summary}), 500

    chain = prompt | llm
    result = chain.invoke({"topic": topic, "summary": summary})
    return jsonify({
        "topic": topic,
        "summary": summary,
        "script": result.content
    })

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
