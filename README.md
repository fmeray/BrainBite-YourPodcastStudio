# Lesson Recapper: Research Papers to Kid-Friendly Podcasts

Upload a research paper (PDF) and get back a short, spoken explanation written for children aged 8 to 12: a script you can read and an audio file you can play or download.

---

## 1. Business Case

### The problem
Research is written for other researchers. Teachers, parents, museums, science communicators, and curious students struggle to turn a dense paper into something a young audience can understand. Doing it by hand means reading the paper, rewriting it in simple language, then recording it. That takes hours per paper and requires both subject knowledge and communication skill.

### Who it is for
| Audience | Need |
|---|---|
| Teachers and tutors | Bring current science into class without hours of prep |
| Parents and homeschoolers | Make research understandable at bedtime or in the car |
| Science communicators and outreach teams | Produce kid-friendly content from new publications quickly |
| Research institutions | Show the public why their work matters |

### The solution
A pipeline that automates the full path: **PDF → clean text → child-friendly script → narrated audio**, wrapped in a simple web interface that needs no technical knowledge.

### Value proposition
- **Time:** minutes instead of hours per paper (to be measured, see [Evaluation](#7-evaluation-plan)).
- **Accessibility:** audio works for young children, early readers, and children with reading difficulties.
- **Consistency:** the same prompt and voice produce a recognizable series format.
- **Low barrier:** one upload, one click, no recording equipment.

### Success metrics (to track in a pilot)
| Metric | How to measure |
|---|---|
| Time per recap | Compare against manual preparation time |
| Factual accuracy | Reviewer checks script claims against the paper |
| Readability | Reading-level score of the script, plus teacher rating |
| Audience comprehension | Short quiz or feedback after listening |
| Cost per recap | Sum of API usage per run (see [Cost](#8-cost-and-scalability)) |

---

## 2. How It Works

```
PDF upload
   │
   ▼
data_processor.py   → extract text (pypdf), clean it (regex)
   │
   ▼
llm_processor.py    → LLM rewrites the paper as a kid-friendly spoken script
   │
   ▼
tts_generator.py    → text-to-speech, split into chunks and joined into one mp3
   │
   ▼
Gradio UI           → script in a textbox + audio player
```

---

## 3. Technical Overview

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3 | Strong ecosystem for documents and AI APIs |
| PDF extraction | `pypdf` | Simple, reliable for text-based PDFs |
| Text cleaning | `re` (regular expressions) | Fixes hyphenation, page numbers, line breaks, special characters for better speech |
| Script generation | OpenAI Chat Completions (`gpt-4o-mini`) | Good quality-to-cost ratio for summarization and rewriting |
| Speech synthesis | OpenAI TTS (`tts-1`, voice `alloy`) | Natural voice, one API for the whole pipeline |
| Audio joining | `pydub` + ffmpeg | Merges chunked audio into one file |
| Interface | Gradio | Web UI with file upload and audio player in a few lines |
| Config | `python-dotenv` | API key kept out of the code |

### Project structure
```
podcast-repo/
├── src/
│   ├── data_processor.py   # read_transcript(), clean_text()
│   ├── llm_processor.py    # create_script() + SYSTEM_PROMPT
│   ├── tts_generator.py    # split_script(), generate_audio()
│   └── main.py             # pipeline + Gradio interface
├── outputs/.gitkeep        # generated files land here (git-ignored)
├── requirements.txt
├── .gitignore              # contains: .env
├── .env.example
└── README.md
```

Each stage is its own module, so any step can be tested, swapped, or improved without touching the others (for example, replacing the TTS provider or the model).

---

## 4. Key Design Decisions

**Modular pipeline.** Reading, language processing, and audio are separate files with plain functions. This makes debugging easy: each stage writes its output (`transcript_clean.txt`, `script.txt`) so a failure can be traced to one step.

**Text cleaning before the LLM.** Raw PDF text contains broken lines, split words, and page numbers. Cleaning first improves both the quality of the summary and the cost, since fewer junk tokens are sent.

**Prompt engineering for the audience.** The system prompt defines the age range (8 to 12), requires everyday words and one or two comparisons from a child's world, forbids markdown and stage directions (the voice would read them aloud), and limits length. It also instructs the model to cover only what the paper says, to reduce invented facts.

**Chunked audio generation.** The TTS API rejects input over 4,096 characters. The pipeline splits scripts at paragraph and sentence boundaries, generates each part, and joins them, so the voice never stops mid-sentence. This came from a real failure during development: a script of 4,187 characters broke the original version.

**Prevention plus safety net.** The prompt asks for a script under 3,500 characters (prevention), and the splitting logic handles any overrun (safety net), because LLM output length varies from run to run.

**Secrets management.** The API key lives in `.env`, which is git-ignored. `.env.example` documents what is needed.

---

## 5. Getting Started

### Prerequisites
- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) installed (`brew install ffmpeg`, `sudo apt install ffmpeg`, or `winget install ffmpeg`)
- An OpenAI API key with credits

### Install
```bash
git clone <your-repo-url>
cd podcast-repo
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure
```bash
cp .env.example .env
# then edit .env and set your key:
# OPENAI_API_KEY=your-key-here
```

### Run
```bash
python src/main.py
```
Open the local address printed in the terminal (usually `http://127.0.0.1:7860`), upload a PDF, and click Submit.

### Output
Each run saves to `outputs/`: `transcript_clean.txt`, `script.txt`, and `recap.mp3`.

---

## 6. Limitations and Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **Hallucination or oversimplification** | A child could learn something inaccurate | Prompt constrains the model to the paper's content; add human review before publishing |
| **Scanned PDFs** | No text layer means an empty transcript | Add OCR (Tesseract) as a fallback |
| **Very long papers** | May exceed the model's context window | Chunk, summarize per section, then combine |
| **Figures, tables, equations** | Not captured as text | Add table extraction or vision model input |
| **Shared output files** | Concurrent users overwrite each other's results | Use a unique file name per run |
| **Cost and abuse on public deployment** | Open link can spend API credits | Add authentication, rate limits, and usage caps |
| **Content safety and copyright** | Papers may be copyrighted; output reaches children | Use open-access papers, and keep a review step for educational publishing |
| **Data privacy** | Uploaded text is sent to a third-party API | Check data handling terms; avoid confidential documents |

---

## 7. Evaluation Plan

This prototype has not yet been formally evaluated. A pilot would include:

1. **Accuracy review:** 10 to 20 open-access papers across fields; a subject reviewer flags any claim not supported by the paper.
2. **Readability check:** reading-level score on each script, plus rating by teachers.
3. **Listener test:** short comprehension questions with a small group of children.
4. **Time and cost comparison:** minutes per recap and API cost per recap versus manual preparation.

Results and lessons learned would be added here.

---

## 8. Cost and Scalability

**Cost drivers:** input tokens (the full cleaned paper), output tokens (the script), and TTS characters (the script length). Longer papers cost more in the first item only, since the script length is capped.

**Measuring it:** log token usage and character counts per run, then compute the average cost per recap. Check the provider's current pricing, as rates change.

**Path to production:**
- Run the pipeline as a backend service with a job queue, since a run takes a minute or more
- Unique output files and cloud storage for audio
- User authentication and per-user usage limits
- Logging and monitoring of failures and cost
- Caching so the same paper is not processed twice

---

## 9. Roadmap

- [ ] OCR fallback for scanned PDFs
- [ ] Chunked summarization for very long papers
- [ ] Selectable age level (5 to 7, 8 to 12, teens) and language
- [ ] Voice selection in the UI
- [ ] Automatic fact-check pass comparing the script to the source
- [ ] Unique file names and multi-user support
- [ ] Downloadable transcript and show notes
- [ ] Evaluation results and demo hosted online

---

## 10. What This Project Demonstrates

- Framing a real problem and defining the audience and success metrics
- Designing an end-to-end AI pipeline from unstructured documents to a usable product
- Prompt engineering with constraints for tone, safety, length, and speech-friendly output
- Handling real API limits and failures (the 4,096-character TTS cap)
- Identifying risks (accuracy, privacy, cost, safety) and proposing mitigations
- Shipping a usable interface and documenting it for others

---
