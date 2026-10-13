from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

load_dotenv()
client = OpenAI()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"

def generate_audio(script, path=OUTPUT_DIR / "recap.mp3"):
    OUTPUT_DIR.mkdir(exist_ok=True)
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=script,
    )
    response.write_to_file(path)
    return path


