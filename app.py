from groq import Groq
import os

client = Groq(# This is the default and can be omitted

    api_key=os.environ.get("GROQ_API_KEY"),)
    
completion = client.chat.completions.create(
    model="deepseek-r1-distill-llama-70b",
    messages=[],
    temperature=0.6,
    max_completion_tokens=4096,
    top_p=0.95,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
