# backend/update_models.py
import re

def update_file(file_path, pattern, replacement):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if replacement is needed
    if pattern in content:
        content = content.replace(pattern, replacement)
        print(f"Updated {file_path}")
    else:
        print(f"Pattern not found in {file_path}")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

print("Updating model references...")

# Update llm_client.py
update_file(
    "app/utils/llm_client.py",
    "model_name='gemini-pro'",
    "model_name='models/gemini-2.0-flash'"
)

update_file(
    "app/utils/llm_client.py", 
    'model_name="gemini-pro"',
    'model_name="models/gemini-2.0-flash"'
)

update_file(
    "app/utils/llm_client.py",
    "model_name='gemini-1.0-pro'",
    "model_name='models/gemini-2.0-flash'"
)

# Update chat_agent.py
update_file(
    "app/services/chat_agent.py",
    "genai.GenerativeModel('gemini-pro')",
    "genai.GenerativeModel('models/gemini-2.0-flash')"
)

update_file(
    "app/services/chat_agent.py",
    'genai.GenerativeModel("gemini-pro")',
    'genai.GenerativeModel("models/gemini-2.0-flash")'
)

print("Done!")