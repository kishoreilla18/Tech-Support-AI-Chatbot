from google import genai
import os

# Better practice: Use an environment variable or paste your key here
client = genai.Client(api_key="AIzaSyAkCkd2b2XvbHJ-fb32qkc6umiXn8LziBs")

def detect_issue(text):
    prompt = f"""
    Classify this laptop issue into ONLY ONE WORD:
    GREETING - Hi, Hello, How are you etc...
    NETWORK
    BATTERY
    DISPLAY
    KEYBOARD
    TOUCHPAD
    AUDIO
    BLUETOOTH
    PERFORMANCE
    STORAGE
    LOGIN
    SOFTWARE
    UPDATE
    DRIVER
    POWER
    OVERHEATING
    CAMERA
    USB
    PRINTER
    OK
    THANKS or THANK YOU
    OTHER

    
    Issue: {text}
    
    Return ONLY the category name.
    """

    try:
        # We use gemini-1.5-flash. If 404 persists, try "gemini-1.5-flash-latest"
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
        )
        
        # Clean the output to ensure it matches your DB categories
        category = response.text.strip().upper()
        print(f"output from api: {category}")
        return category
    
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "UNKNOWN"