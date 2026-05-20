from groq import Groq
from dotenv import load_dotenv
import os

# LOAD ENV VARIABLES
load_dotenv()

# GET API KEY
api_key = os.getenv("GROQ_API_KEY")

# CREATE CLIENT
client = Groq(
    api_key=api_key
)

print("AI Chat Started (type 'exit' to stop)")

while True:

    question = input("You: ")

    if question.lower() == "exit":
        break

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    print(
        "AI:",
        response.choices[0].message.content
    )