from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
 
def generate_audio(script, path="outputs/recap.mp3"):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=script,
    )
    response.write_to_file(path)
    return path


# Read the script you generated earlier
with open("outputs/script.txt", "r", encoding="utf-8") as f:
    
    script = f.read()
    
path = generate_audio(script)
print("Saved:", path)
# Optional: play it
audio = AudioSegment.from_mp3(path)
play(audio)