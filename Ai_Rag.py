import os
import glob
from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI

# Load environment variables from .env
load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')

# Initialize OpenAI client
openai = OpenAI()

# Model to use (cheap and efficient)
MODEL = "gpt-4o-mini"

# Base system instruction
system_message = (
    "You are an expert in answering accurate questions about Insurellm, the Insurance Tech company. "
    "Give brief, accurate answers. If you don't know the answer, say so. "
    "Do not make anything up if you haven't been provided with relevant context."
)

# Load context from files
context = {}

# Load employee knowledge base
employees = glob.glob("knowledge-base/employees/*")
print(f"Loading employee files: {employees}")

for employee_path in employees:
    name = os.path.splitext(os.path.basename(employee_path))[0]
    with open(employee_path, "r", encoding="utf-8") as f:
        context[name] = f.read()

# Load product knowledge base
products = glob.glob("knowledge-base/products/*")
print(f"Loading product files: {products}")

for product_path in products:
    name = os.path.splitext(os.path.basename(product_path))[0]
    with open(product_path, "r", encoding="utf-8") as f:
        context[name] = f.read()

print(f"Context keys loaded: {list(context.keys())[:5]}...")

# Find relevant context
def get_relevant_context(message):
    relevant_context = []
    for title, content in context.items():
        if title.lower() in message.lower():
            relevant_context.append(content)
    return relevant_context

# Append context to message
def add_context(message):
    relevant = get_relevant_context(message)
    if relevant:
        message += "\n\nThe following additional context might be relevant in answering this question:\n\n"
        for item in relevant:
            message += item + "\n\n"
    return message

# Main chat function
def chat(message, history):
    full_history = [{"role": "system", "content": system_message}]
    for user, assistant in history:
        full_history.append({"role": "user", "content": user})
        full_history.append({"role": "assistant", "content": assistant})

    message_with_context = add_context(message)
    full_history.append({"role": "user", "content": message_with_context})

    print("Sending message to OpenAI:")
    print(message_with_context)

    try:
        completion = openai.chat.completions.create(
            model=MODEL,
            messages=full_history
        )
        reply = completion.choices[0].message.content
        return reply
    except Exception as e:
        print(f"Error from OpenAI: {e}")
        return "Sorry, something went wrong while contacting the model."

# Run the Gradio app
if __name__ == "__main__":
    gr.ChatInterface(chat, type="chat").launch()
