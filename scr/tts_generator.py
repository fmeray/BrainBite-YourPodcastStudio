from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
 
def generate_audio(script, path="outputs/recap.mp3"):
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=script,
    )
    response.write_to_file(path)
    return path

