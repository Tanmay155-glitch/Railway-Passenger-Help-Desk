# Indian Railways help desk: capstone data pack (version B)

Build a passenger help desk assistant for Indian Railways. Your team writes one function, `ask(question)`, that:

- answers rule questions (refunds, cancellation, Tatkal, booking limits, charts) from the documents, with the document name and page;
- answers timetable questions from the SQLite database, using read-only text-to-SQL;
- says "I don't know" when the answer is not in the pack, or when the request is unsafe.

**This is an unofficial learning project.** It is built on public documents from Indian Railways, IRCTC and PIB, and on a CC0 timetable snapshot from 2016. It is not an official railway service. Rules change often: the answers we expect follow the documents in this pack, which may not be the latest rules on the day you read this.

## What's in the pack

```
README.md                                            this file
SOURCES.md                                           where each document and the timetable came from
data/documents/indianrail_refund_rules_2015.html          refund rules from 12.11.2015: table of old vs revised charges
data/documents/irctc_refund_rules_jan2026.pdf             IRCTC refund and TDR rules (updated Jan 2026), 11 pages
data/documents/rb_cc10_2024_advance_reservation.pdf       Railway Board circular 10/2024: booking limit 120 to 60 days (scanned)
data/documents/rb_cc08_2025_tatkal.pdf                    Railway Board circular 08/2025: Aadhaar for Tatkal (Hindi pages scanned)
data/documents/rb_cc10_2025_reservation_charts.pdf        Railway Board circular 10/2025: when first charts are made (scanned)
data/documents/rb_cc08_2026_vande_bharat_sleeper_refund.pdf  circular 08/2026 + gazette G.S.R. 41(E): Vande Bharat Sleeper refunds
data/documents/pib_2026-03-24_reform_express.html         PIB press release of 24 Mar 2026: new cancellation windows and more
data/database/rail_timetable.db                           SQLite timetable (2016 snapshot): stations, trains, schedules
data/database/schema.md                                   every table and column, and the data's quirks
data/questions/sample_questions.json                      10 practice questions with model answers and sources
```

## The database in one minute

| Table | Rows | What it holds |
|---|---|---|
| `stations` | 8,990 | code, name, state, zone, location |
| `train_types` | 16 | what type codes like `Raj` or `Shtb` mean |
| `trains` | 5,208 | number, name, type, start and end station, times, distance, classes |
| `schedules` | 417,080 | every station on every route, in order, with day, arrival, departure, `is_halt` |
| `stops` (view) | 104,151 | only the rows where the train really stops (`is_halt = 1`) |

Read `database/schema.md` before writing prompts for text-to-SQL. Two things trip people up: `schedules` includes stations a train only passes through (use `stops`), and overnight journeys need the `day` column.

## Things to watch in the documents

- Two PDFs are scanned images with no text layer, and the Tatkal circular has scanned Hindi pages. You need OCR for some answers.
- Some documents disagree because the rules changed over time. When they do, the newer document wins: check the dates.
- Rules for specific trains (for example Vande Bharat Sleeper) override the general rules for those trains.
- Two documents are HTML, so they have no page numbers: cite them with `"page": null`.

## What your system returns

Every question goes through one function, `ask(question)`, which returns:

```json
{"answer": "the reply, in plain words", "sources": [{"doc": "irctc_refund_rules_jan2026.pdf", "page": 3}], "sql": null, "dont_know": false}
```

- `sources`: the documents used, by file name, with the page. The page is `null` for the HTML documents.
- `sql`: the query it ran, when it used the database; otherwise `null`.
- `dont_know`: `true` when it declines (not in the pack, out of scope, or unsafe).

## Sample questions

Each question in `questions/sample_questions.json` has `id`, `question`, the model `answer`, its `sources` (document and page), and, for timetable questions, the `sql` that finds the answer. The hidden test set has 30 questions of the same kinds, and it stays hidden: after the deadline we run `python run_questions.py <questions> <results>` from your repo, with a question file that has only `id` and `question`. The results file is a list with one object per question: the `id` and `question`, plus everything `ask()` returned:

```json
{"id": "H01", "question": "...", "answer": "...", "sources": [{"doc": "rb_cc10_2024_advance_reservation.pdf", "page": 1}], "sql": null, "dont_know": false}
```

## How to start

1. Open the database (`sqlite3 database/rail_timetable.db`, or Python's `sqlite3`) and run a few queries from `schema.md`.
2. Parse the documents page by page, keep the file name and page number with every chunk, and check which pages come out empty: those need OCR.
3. Get a simple version answering all 10 sample questions end to end first, and check it against the model answers. Then improve one part at a time, and keep a change only when the numbers go up.
4. Run all SQL on a read-only connection: `sqlite3.connect("file:database/rail_timetable.db?mode=ro", uri=True)`.

The class notebooks and your assignments are a starting point, not a limit: use any free library or model that makes the answers more accurate.

---

## Setup & Installation

### 1. Prerequisites
- Python 3.9 or higher
- Google Gemini API key ([Get one free here](https://makersuite.google.com/app/apikey))

### 2. Install Dependencies
```powershell
# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root (use `.env.example` as template):
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Build Search Index
```powershell
python build_index.py
```

This creates:
- `index/chunks.json` - document chunks with metadata
- `index/bm25.pkl` - BM25 search index
- `index/embeddings.npy` - semantic embeddings (optional)
- `index/manifest.json` - index metadata
- `index/schema.txt` - database schema for text-to-SQL

---

## Usage

### Interactive Mode (Terminal)
```powershell
python ask.py
```

Ask questions interactively. Type `exit` or `quit` to stop.

**Example:**
```
Question: What is the refund for AC 1st class if I cancel 2 days before departure?
Answer: If you cancel an AC 1st class ticket 48 hours or more before departure,
you will receive a 75% refund after deducting clerkage charges (₹60 for this class).
Sources: irctc_refund_rules_jan2026.pdf (page 3)
```

### Batch Mode (Multiple Questions)
```powershell
python run_questions.py eval/test_set.json results.json
```

Processes all questions from a JSON file and saves results.

### Python API
```python
from helpdesk.pipeline import ask

result = ask("Which trains run from Mumbai to Delhi?")
print(result["answer"])
print(result["sources"])
print(result["sql"])
```

---

## Testing

### Run Unit Tests
```powershell
pytest tests/ -v
```

### Run System Evaluation
```powershell
python run_questions.py eval/test_set.json eval/results.json
python eval/evaluate.py eval/test_set.json eval/results.json
```

**Current Test Results:**
- **80% accuracy** on 20 real passenger questions
- **100% SQL success rate** (6/6 queries)
- **100% refusal accuracy** (4/4 out-of-scope correctly refused)
- See `TEST_RESULTS_SUMMARY.md` for detailed results

---

## Project Structure

```
rail_capstone_pack/
├── helpdesk/              # Main package
│   ├── pipeline.py        # Main ask() function
│   ├── router.py          # Question routing logic
│   ├── search.py          # Document search (BM25 + semantic)
│   ├── sql.py             # Text-to-SQL generation
│   ├── sql_guard.py       # SQL security validation
│   ├── answer.py          # Answer generation with LLM
│   ├── entities.py        # Entity extraction (stations, trains)
│   ├── ingest.py          # Document ingestion (PDF/HTML/OCR)
│   ├── llm.py             # LLM interface (Gemini)
│   └── config.py          # Configuration management
├── data/
│   ├── documents/         # Railway rule documents (PDF/HTML)
│   ├── database/          # SQLite timetable database
│   └── questions/         # Sample questions
├── eval/
│   ├── test_set.json      # Evaluation questions
│   ├── evaluate.py        # Evaluation script
│   └── experiments.md     # Performance tracking
├── tests/                 # Unit tests (51 tests)
├── index/                 # Search indices (generated)
├── build_index.py         # Index builder
├── ask.py                 # Interactive CLI
├── run_questions.py       # Batch processor
├── README.md              # This file
├── design.md              # System architecture
├── requirements.md        # Detailed specifications
└── SOURCES.md             # Data provenance

```

---

## Documentation

- **README.md** (this file) - Setup, usage, and overview
- **design.md** - System architecture and design decisions
- **requirements.md** - Functional and non-functional requirements
- **SOURCES.md** - Data sources and provenance
- **TEST_RESULTS_SUMMARY.md** - Test results and metrics
- **data/database/schema.md** - Database schema reference
- **eval/experiments.md** - Performance tracking

---

## Key Features

✅ **Hybrid Search** - BM25 keyword + semantic embeddings  
✅ **Text-to-SQL** - Natural language to SQLite queries  
✅ **Multi-format Docs** - PDF, HTML, scanned images (OCR)  
✅ **Security** - SQL injection protection with guard system  
✅ **Refusal Logic** - Properly declines out-of-scope questions  
✅ **Time-aware Rules** - Newer documents override older ones  
✅ **Refund Calculator** - Python-based percentage computation  
✅ **Entity Recognition** - Station codes, train numbers  
✅ **Neighbor Context** - Expands context with surrounding chunks  
✅ **Comprehensive Testing** - 51 unit tests, 80% accuracy

---

## Performance

- **Response Time**: ~5 seconds average
- **Accuracy**: 80% on real passenger questions
- **SQL Success**: 100% (6/6 queries executed correctly)
- **Refusal Accuracy**: 100% (4/4 out-of-scope correctly refused)
- **Test Coverage**: 51 unit tests across 5 modules

---

## Notes

- This system uses Google Gemini 1.5 Flash for LLM tasks
- The timetable is a 2016 snapshot (8,990 stations, 5,208 trains)
- Documents are from 2015-2026 (check SOURCES.md for details)
- Rules are parsed from official Railway Board circulars and IRCTC documents
- This is an educational project, not an official railway service
