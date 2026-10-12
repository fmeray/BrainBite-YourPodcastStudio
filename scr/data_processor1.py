import json
import re
from pypdf import PdfReader

# clean_text() is the same function from the previous step

def extract_pages(path):
    reader = PdfReader(path)
    meta = reader.metadata
    doc_info = {
        "source": path,
        "title": meta.title if meta else None,
        "author": meta.author if meta else None,
        "total_pages": len(reader.pages),
    }
    pages = [
        {"page": i, "text": page.extract_text() or ""}
        for i, page in enumerate(reader.pages, start=1)
    ]
    return doc_info, pages


def split_long(paragraph, max_chars):
    """Split a paragraph that is too long into sentence-based pieces."""
    if len(paragraph) <= max_chars:
        return [paragraph]
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    pieces, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 > max_chars and current:
            pieces.append(current.strip())
            current = ""
        current += s + " "
    if current.strip():
        pieces.append(current.strip())
    return pieces


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



def chunk_pages(pages, doc_info, max_chars=3000):
    chunks = []
    current, current_pages = "", []

    def flush():
        nonlocal current, current_pages
        if current.strip():
            text = current.strip()
            chunks.append({
                "chunk_id": len(chunks),
                "text": text,
                "pages": sorted(set(current_pages)),
                "char_count": len(text),
                **doc_info,
            })
        current, current_pages = "", []

    for p in pages:
        cleaned = clean_text(p["text"])
        for para in cleaned.split("\n\n"):
            if not para.strip():
                continue
            for piece in split_long(para, max_chars):
                if len(current) + len(piece) > max_chars:
                    flush()
                current += piece + "\n\n"
                current_pages.append(p["page"])
    flush()
    return chunks


doc_info, pages = extract_pages("From-adoption-to-impact.pdf")
chunks = chunk_pages(pages, doc_info)

with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print("Chunks created:", len(chunks))
print(json.dumps({k: v for k, v in chunks[0].items() if k != "text"}, indent=2))