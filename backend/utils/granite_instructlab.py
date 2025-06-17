import requests

def query_granite(prompt: str) -> str:
    url = "http://localhost:8000/v1/completions"
    payload = {
        "prompt": prompt,
        "max_tokens": 512,        # or whatever limit you need
        "temperature": 0.8        # optional
    }
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()
        # The llama.cpp API returns an array of choices
        text = data["choices"][0].get("text", "")
        return text.strip()
    except Exception as e:
        print(f"Exception querying Granite: {e}\nResponse was: {getattr(e, 'response', None)}")
        return "print('Granite connection failed')"
