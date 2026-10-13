# BrainBite: Turn Research Papers into Podcasts Anyone Can Follow

Upload a research paper (PDF) and get back a short podcast: a spoken script that explains the paper's five key insights in plain language, plus an audio file you can play or download. It is written for curious adults with zero background in the topic.



---

## 1. Business Case

### The problem
Scientific research is written for specialists. Everyone else, including executives, policymakers, journalists, investors, and curious professionals, either skips it or relies on second-hand summaries that may be shallow or wrong. Reading a dense paper takes hours and background knowledge. Turning it into something a general audience can follow takes a skilled science communicator and more hours on top.

### Who it is for
| Audience | Need |
|---|---|
| Business leaders and strategists | Understand new research that affects their field without reading the paper |
| Journalists and content creators | Get a clear first pass on a paper before writing or interviewing |
| Policy, investment, and consulting teams | Brief decision-makers quickly on technical developments |
| Universities and research organizations | Make their work understandable to the public and to funders |
| Lifelong learners | Follow current science during a commute or a walk |

### The solution
An automated pipeline: **PDF → clean text → plain-language podcast script → narrated audio**, wrapped in a simple web interface that needs no technical skills.

The script is built to a defined editorial standard: find the five most important insights, open with a relatable hook, explain every technical term the moment it appears, use everyday analogies, tell it as one flowing story, and end with a single memorable takeaway.

### Value proposition
- **Time:** a first-pass briefing in minutes instead of hours (to be measured, see [Evaluation](#7-evaluation-plan)).
- **Accessibility:** no background knowledge needed, and audio fits into time when people cannot read.
- **Honesty about certainty:** the prompt requires the script to separate established findings from hypotheses and open questions.
- **Low barrier:** one upload, one click, no recording equipment or editing.


## 2. How It Works

```
PDF upload
   │
   ▼
data_processor.py   → extract text (pypdf), clean it (regex)
   │
   ▼
llm_processor.py    → LLM writes a plain-language podcast script
   │                  (five key insights, analogies, one takeaway)
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

**Modular pipeline.** Reading, language processing, and audio are separate files with plain functions. Each stage saves its output (`transcript_clean.txt`, `script.txt`), so a failure can be traced to one step.

**Text cleaning before the LLM.** Raw PDF text contains broken lines, split words, and page numbers. Cleaning first improves the quality of the script and lowers cost, since fewer junk tokens are sent.

**The prompt is the product.** Most of the value comes from the system prompt, which works as an editorial brief:
- **Defined audience:** intelligent adults with no background, which avoids both jargon and a childish tone.
- **Structured thinking:** the model first identifies five key insights, then weaves them into one story rather than a list.
- **Term discipline:** every technical term is explained immediately, with why it matters and, where helpful, an example.
- **Scientific honesty:** established findings are distinguished from hypotheses and open questions, the model must not invent findings or applications, and it must not pretend an analogy is scientifically exact.
- **Written for the ear:** short sentences, conversational tone, no headings, lists, or formatting symbols (the voice would read them aloud).
- **Built-in quality check:** the model reviews its own draft against four questions before answering.

**Chunked audio generation.** The TTS API rejects input over 4,096 characters. The pipeline splits scripts at paragraph and sentence boundaries, generates each part, and joins them, so the voice never stops mid-sentence. This came from a real failure during development: a 4,187-character script broke the first version.

**Prevention plus safety net.** The prompt caps the script at 3,500 characters (prevention), and the splitting logic handles any overrun (safety net), because LLM output length varies from run to run.

**Secrets management.** The API key lives in `.env`, which is git-ignored. `.env.example` documents what is needed.

### The system prompt (summary)
| Element | Requirement |
|---|---|
| Role | Expert science communicator and podcast storyteller |
| Audience | Curious adults with zero subject knowledge |
| Content | Five most important insights, what was found, why it matters, how to understand it |
| Opening | Engaging question or everyday situation |
| Technical terms | Explain meaning, why it matters, simple example |
| Analogies | Everyday life (cooking, movies, technology, relationships, nature), flagged as approximate when needed |
| Accuracy | Separate findings from hypotheses; never invent |
| Format | One flowing spoken story, no lists or headings |
| Ending | One memorable takeaway |
| Length | Under 3,500 characters |

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
| **Hallucination or oversimplification** | Listeners may come away with an inaccurate picture of the research | Prompt forbids invented findings and requires flagging uncertainty; add expert review before publishing |
| **Analogies that mislead** | An everyday comparison can imply something the science does not say | Prompt requires acknowledging that analogies are not exact; spot-check scripts |
| **Five insights in a short script** | Depth is limited; nuance and caveats may be dropped | Allow longer scripts with chunked generation, or offer a "deep dive" mode |
| **Self-review inside one prompt** | The model's own quality check is not independent verification | Add a separate fact-check pass that compares script claims to the source |
| **Scanned PDFs** | No text layer means an empty transcript | Add OCR (Tesseract) as a fallback |
| **Very long papers** | May exceed the model's context window | Chunk, summarize per section, then combine |
| **Figures, tables, equations** | Not captured as text, yet often central to the findings | Add table extraction or vision model input |
| **Shared output files** | Concurrent users overwrite each other's results | Use a unique file name per run |
| **Cost and abuse on public deployment** | Open link can spend API credits | Add authentication, rate limits, and usage caps |
| **Copyright and attribution** | Papers may be copyrighted; a podcast could be shared widely | Use open-access papers, cite the source in published episodes |
| **Data privacy** | Uploaded text is sent to a third-party API | Check data handling terms; avoid confidential documents |

---

## 7. Evaluation Plan

This prototype has not yet been formally evaluated. A pilot would include:

1. **Accuracy review:** 10 to 20 open-access papers across different fields; a subject reviewer flags any claim not supported by the paper and any hypothesis stated as fact.
2. **Comprehension test:** non-expert listeners hear the podcast and answer short questions on the main ideas.
3. **Terminology check:** confirm that every technical term used in the script is explained.
4. **Listener feedback:** clarity and engagement ratings, plus whether the audio "sounds like a natural podcast".
5. **Time and cost comparison:** minutes and API cost per briefing versus reading the paper or writing a summary by hand.

Results and lessons learned would be added here.

---

## 8. Cost and Scalability

**Cost drivers:** input tokens (the full cleaned paper), output tokens (the script), and TTS characters (the script length). Longer papers raise input cost only, since the script length is capped.

**Measuring it:** log token usage and character counts per run, then compute the average cost per briefing. Check the provider's current pricing, as rates change.

**Path to production:**
- Run the pipeline as a backend service with a job queue, since a run takes a minute or more
- Unique output files and cloud storage for audio
- User authentication and per-user usage limits
- Logging and monitoring of failures and cost
- Caching so the same paper is not processed twice

---

## 9. Roadmap

- [ ] Independent fact-check pass comparing the script to the source paper
- [ ] OCR fallback for scanned PDFs
- [ ] Chunked summarization for very long papers
- [ ] Adjustable length (quick 2-minute brief, full 5-minute episode)
- [ ] Selectable audience level and language
- [ ] Voice selection in the UI
- [ ] Unique file names and multi-user support
- [ ] Downloadable transcript and show notes with source citation
- [ ] Evaluation results and a hosted demo

---

## 10. What This Project Demonstrates

- Framing a real problem and defining the audience and success metrics
- Designing an end-to-end AI pipeline from unstructured documents to a usable product
- Prompt engineering as editorial design: audience, structure, accuracy rules, and a self-check
- Handling real API limits and failures (the 4,096-character TTS cap)
- Identifying risks (accuracy, misleading analogies, privacy, cost) and proposing mitigations
- Shipping a usable interface and documenting it for others

---
