import requests

response = requests.post(
    "http://127.0.0.1:8000/claude_streaming/streaming",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "AI-IE*0496@#."
    },
    json={"message": "Count slowly from 1 to 15, one number per line. After each number, write one sentence about what is required to become a top AI integration engineer."},
    stream=True
)

print("--- Streaming starting ---\n")
for chunk in response.iter_content(chunk_size=None):
    if chunk:
        print(chunk.decode(), end="", flush=True)
print("\n\n--- Streaming complete ---")

