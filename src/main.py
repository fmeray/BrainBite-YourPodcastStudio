from pathlib import Path
import gradio as gr 
from data_processor import read_transcript, clean_text
from llm_processor import create_script
from tts_generator import generate_audio


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
PDF_PATH = BASE_DIR / "src/From-adoption-to-impact.pdf"


def main(pdf_path):
    if pdf_path is None:
        raise gr.Error("Please upload a PDF first.")
    
    
    OUTPUT_DIR.mkdir(exist_ok=True)

    text = clean_text(read_transcript(pdf_path))
    (OUTPUT_DIR / "transcript_clean.txt").write_text(text, encoding="utf-8")

    script = create_script(text)
    (OUTPUT_DIR / "script.txt").write_text(script, encoding="utf-8")
    print("Script length:", len(script))

    
    audio_path = generate_audio(script)

    # Gradio expects one return value per output component
    return script, str(audio_path)


demo = gr.Interface(
    fn=main,
    inputs=gr.File(label="Upload Research paper (.pdf)", type="filepath"),
    outputs=[
        gr.Textbox(label="Recap script"),
        gr.Audio(label="Recap podcast"),
    ],
    title="Research Paper Recapper",
)

if __name__ == "__main__":
    demo.launch(allowed_paths=[str(OUTPUT_DIR)])
   