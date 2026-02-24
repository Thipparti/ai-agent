import os
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not set.")

client = Groq(api_key=api_key)

print("Autonomous Research Agent (type 'exit' to quit)")

while True:
    query = input("You: ")
    if query.lower() == "exit":
        break

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": query}]
    )

    print("AI:", response.choices[0].message.content)