from pypdf import PdfReader
import re

reader = PdfReader("From-adoption-to-impact.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

#with open("transcript.txt", "w", encoding="utf-8") as f:
#   f.write(text)



def clean_text(text): 
    
    # remove timestamps (12:05), filler words, extra spaces
    text = re.sub(r"\d{1,2}:\d{2}(:\d{2})?", "", text)
    text = re.sub(r"\b(um|uh)\b", "", text, flags=re.I)
    text = re.sub(r"\s+", " ", text)
    
    # Fix words split across lines with a hyphen (e.g. "inter-\nnational")
    text = re.sub(r"-\n(\w)", r"\1", text)

    # Remove standalone page numbers (a line with only digits)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Replace single line breaks with a space (keeps paragraph breaks)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Collapse multiple spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse 3+ newlines into a paragraph break
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()


cleaned = clean_text(text)
with open("transcript_clean.txt", "w", encoding="utf-8") as f:
    f.write(cleaned)
