# Requirements Specification
## Railway Passenger Help Desk - GenAI Nexus Capstone

**Project**: Command-line railway passenger query system  
**Team**: GenAI Nexus, Cohort 1, Module 2  
**Deadline**: Friday, 6 November 2026, 12:00  
**Evaluation**: 50% of score based on accuracy on 30 hidden questions

---

## 1. System Overview

**WHILE** operating as a command-line Python application  
**IF** a passenger question is received  
**THEN** the system **SHALL** answer using only the provided data pack (refund rules, Railway Board circulars, PIB release, SQLite timetable)  
**AND** cite exact document sources with page numbers

---

## 2. Core Functional Requirements

### FR-1: Question Answering Interface

**FR-1.1**: Primary API Contract  
**WHILE** the system is operational  
**IF** `ask(question: str)` is called with any passenger question  
**THEN** the system **SHALL** return a dictionary with exactly these keys:
- `answer` (str): plain-language response
- `sources` (list): citations with `doc` (filename) and `page` (integer or null)
- `sql` (str or null): executed query if applicable
- `dont_know` (bool): true when declining to answer

**FR-1.2**: Error Resilience  
**WHILE** processing any question  
**IF** an internal error occurs  
**THEN** the system **SHALL NOT** raise an exception  
**AND** **SHALL** return `dont_know: true` with an honest explanation

**FR-1.3**: Command-Line Interface  
**WHILE** the CLI is invoked  
**IF** run as `python ask.py "question"`  
**THEN** the system **SHALL** print the answer in plain words, followed by Sources and SQL blocks  
**AND** **SHALL** complete startup in under 3 seconds  
**AND** **SHALL** return first answer in under 10 seconds

**FR-1.4**: Interactive Mode  
**WHILE** the CLI is invoked without arguments  
**IF** run as `python ask.py`  
**THEN** the system **SHALL** start an interactive prompt  
**AND** **SHALL** accept `:examples` to show demo questions  
**AND** **SHALL** exit on `exit` command

**FR-1.5**: Batch Processing  
**WHILE** batch mode is invoked  
**IF** run as `python run_questions.py <questions.json> <results.json>`  
**THEN** the system **SHALL** process all questions in order  
**AND** **SHALL** write results after each question (crash-safe)  
**AND** **SHALL** never stop on a single question failure

---

## 3. Data Source Requirements

### FR-2: Document Processing

**FR-2.1**: PDF Text Extraction  
**WHILE** ingesting PDF documents  
**IF** a page contains text with PyMuPDF  
**THEN** the system **SHALL** extract text directly  
**BUT IF** a page has fewer than 50 characters  
**THEN** the system **SHALL** apply OCR at 250-300 dpi

**FR-2.2**: OCR Engine Selection  
**WHILE** OCR is required  
**IF** `rapidocr-onnxruntime` is available  
**THEN** the system **SHALL** use it  
**ELSE IF** Tesseract binary exists  
**THEN** the system **SHALL** fall back to `pytesseract`

**FR-2.3**: HTML Processing  
**WHILE** ingesting HTML files  
**IF** processing the 2015 refund rules table  
**THEN** the system **SHALL** create one chunk per rule row  
**AND** **SHALL** repeat column headers ("Pre revised", "Revised") in each chunk

**FR-2.4**: Chunking Strategy  
**WHILE** creating document chunks  
**IF** splitting documents  
**THEN** the system **SHALL** target 150-400 words per chunk  
**AND** **SHALL** never split clauses or table rows  
**AND** **SHALL** prepend `[doc | page | issuer | date | clause]` headers  
**AND** **SHALL** extract identifiers (rule numbers, circular numbers, train numbers, amounts)

### FR-3: Database Access

**FR-3.1**: Read-Only Timetable Access  
**WHILE** accessing the SQLite database  
**IF** any query is executed  
**THEN** the system **SHALL** use only SELECT statements  
**AND** **SHALL** open database in read-only mode  
**AND** **SHALL** apply PRAGMA query_only = ON  
**AND** **SHALL** limit results to 50 rows maximum

**FR-3.2**: SQL Safety Guards  
**WHILE** generating SQL  
**IF** validating a query  
**THEN** the system **SHALL** reject INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, REPLACE, ATTACH, DETACH, PRAGMA, VACUUM  
**AND** **SHALL** strip comments  
**AND** **SHALL** allow exactly one statement starting with SELECT or WITH  
**AND** **SHALL** enforce execution time limits

**FR-3.3**: Database Schema Knowledge  
**WHILE** generating SQL  
**IF** the system needs schema information  
**THEN** the system **SHALL** read and use the live schema from `sqlite_master`  
**AND** **SHALL** understand the `stops` view (schedules WHERE is_halt = 1)  
**AND** **SHALL** handle overnight journeys: `(day_b - day_a) * 1440 + minutes(arrival_b) - minutes(departure_a)`

---

## 4. Information Retrieval Requirements

### FR-4: Hybrid Search

**FR-4.1**: Multi-Channel Retrieval  
**WHILE** searching for relevant content  
**IF** a question is received  
**THEN** the system **SHALL** use BM25 keyword search  
**AND** **SHALL** use dense embeddings (local via fastembed OR Gemini)  
**AND** **SHALL** merge results using Reciprocal Rank Fusion

**FR-4.2**: Embedding Failure Resilience  
**WHILE** performing search  
**IF** embedding generation fails at query time  
**THEN** the system **SHALL** fall back to BM25 alone  
**AND** **SHALL** still return answers

**FR-4.3**: Exact Match Boosting  
**WHILE** scoring chunks  
**IF** the question contains "Rule 25", circular numbers, G.S.R. numbers, train numbers, or rupee amounts  
**THEN** the system **SHALL** boost chunks containing the same tokens

**FR-4.4**: Date-Aware Retrieval  
**WHILE** returning search results  
**IF** top chunks come from different documents on the same topic  
**THEN** the system **SHALL** return all with their dates for precedence evaluation

---

## 5. Answer Generation Requirements

### FR-5: Grounded Generation

**FR-5.1**: Source-Only Answers  
**WHILE** generating answers  
**IF** responding to any question  
**THEN** the system **SHALL** answer only from supplied chunks  
**AND** **SHALL NOT** use facts from training data, code, or configuration

**FR-5.2**: Document Precedence  
**WHILE** generating answers  
**IF** two documents conflict  
**THEN** the system **SHALL** state the rule from the later-dated document  
**AND** **SHALL** mention it replaces the older document

**FR-5.3**: Train-Specific Overrides  
**WHILE** generating answers  
**IF** a rule exists for a named train type (Vande Bharat Sleeper, Amrit Bharat II)  
**THEN** the system **SHALL** apply that rule instead of the general rule

**FR-5.4**: Historical Data Handling  
**WHILE** processing the 2015 rules table  
**IF** "Pre revised" column data is encountered  
**THEN** the system **SHALL** treat it as historical, not current

**FR-5.5**: Future Announcements  
**WHILE** processing the PIB release  
**IF** statements are phrased as future ("soon")  
**THEN** the system **SHALL** report them as announced, not in force

**FR-5.6**: Source Citation Accuracy  
**WHILE** building source citations  
**IF** the answer references chunks  
**THEN** the system **SHALL** cite only the 2-4 pages that truly support the answer  
**AND** **SHALL** use chunk metadata, never free text from the model  
**AND** **SHALL** order sources with the best page first

**FR-5.7**: Arithmetic in Code  
**WHILE** computing time-to-departure buckets or percentages  
**IF** a question requires calculation  
**THEN** the system **SHALL** perform arithmetic in Python, not in the LLM  
**AND** **SHALL** verify numbers when possible

---

## 6. Query Routing Requirements

### FR-6: Intent Classification

**FR-6.1**: Route Classification  
**WHILE** receiving a question  
**IF** classifying intent  
**THEN** the system **SHALL** route to: `docs | db | both | refuse | out_of_scope`  
**AND** **SHALL** use cheap keyword rules first  
**AND** **SHALL** use Gemini classification with confidence for unclear cases

**FR-6.2**: Out-of-Scope Handling  
**WHILE** classifying a question  
**IF** the question asks about fares, seat availability, waitlist confirmation, PNR status, live running status, or any data not in the pack  
**THEN** the system **SHALL** return `dont_know: true`  
**AND** **SHALL** explain what is missing in one sentence

**FR-6.3**: Unsafe Request Handling  
**WHILE** classifying a question  
**IF** the question requests data changes ("change the departure time")  
**THEN** the system **SHALL** return `dont_know: true` and refuse politely  
**AND** **SHALL** not call the LLM if keyword rules catch it

**FR-6.4**: Mixed Query Handling  
**WHILE** processing a question  
**IF** the route is `both`  
**THEN** the system **SHALL** run document search and SQL generation  
**AND** **SHALL** merge into one answer with both source lists and SQL

---

## 7. Entity Resolution Requirements

### FR-7: Station Name Matching

**FR-7.1**: Station Resolution  
**WHILE** processing timetable questions  
**IF** station names are mentioned  
**THEN** the system **SHALL** match to `stations.code` via:
1. Exact code match
2. Case-insensitive name match
3. Fuzzy match using rapidfuzz

**FR-7.2**: Multi-Station Cities  
**WHILE** resolving station names  
**IF** a city has multiple stations (Chennai Central, Egmore, Beach)  
**THEN** the system **SHALL** allow all with `IN (...)`  
**AND** **SHALL** pass resolved codes to the SQL generator

---

## 8. Build and Index Requirements

### FR-8: Index Construction

**FR-8.1**: Build Process  
**WHILE** running `python build_index.py`  
**IF** the data pack is present  
**THEN** the system **SHALL** ingest all documents  
**AND** **SHALL** perform OCR where needed  
**AND** **SHALL** generate embeddings  
**AND** **SHALL** build BM25 index  
**AND** **SHALL** write to `index/` directory  
**AND** **SHALL** be idempotent

**FR-8.2**: Build Output  
**WHILE** completing the build  
**IF** indexing succeeds  
**THEN** the system **SHALL** print a table of pages per document  
**AND** **SHALL** indicate which pages were OCR'd  
**AND** **SHALL** fail loudly if any PDF page has no text

**FR-8.3**: Index Portability  
**WHILE** the index is built  
**IF** writing to `index/`  
**THEN** the system **SHALL** include OCR text (no OCR engine needed at runtime)  
**AND** **SHALL** commit `index/` to git  
**AND** **SHALL** include a manifest with pack hash and parameters

---

## 9. Data Pack Location Requirements

### FR-9: Flexible Path Resolution

**FR-9.1**: Pack Location Discovery  
**WHILE** locating data files  
**IF** the system needs to access the pack  
**THEN** the system **SHALL** search recursively under `data/`  
**AND** **SHALL** support both `data/rail_capstone_pack/...` and `data/...` layouts  
**AND** **SHALL NOT** hard-code one layout  
**AND** **SHALL** use `Path("data").rglob(pattern)` or equivalent

---

## 10. Non-Functional Requirements

### NFR-1: Security and Safety

**NFR-1.1**: API Key Protection  
**WHILE** handling the Gemini API key  
**IF** accessing credentials  
**THEN** the system **SHALL** read `GEMINI_API_KEY` from `.env` only  
**AND** **SHALL** never commit keys to git  
**AND** **SHALL** never print keys to logs or console  
**AND** **SHALL** never include keys in git history

**NFR-1.2**: Git Ignore Rules  
**WHILE** managing version control  
**IF** files are created  
**THEN** `.gitignore` **SHALL** include: `.env`, `.venv/`, `data/`  
**AND** `data/` **SHALL** never be committed  
**AND** `index/` **SHALL** be committed

### NFR-2: Compatibility

**NFR-2.1**: Python Version  
**WHILE** the system is developed  
**IF** using Python features  
**THEN** the system **SHALL** support Python 3.10+  
**AND** **SHALL NOT** use syntax or modules newer than Python 3.10

**NFR-2.2**: Free Tools Only  
**WHILE** selecting dependencies  
**IF** adding a new library or service  
**THEN** the system **SHALL** use only free tools  
**AND** **SHALL** require only a Gemini API key (free tier)  
**AND** **SHALL NOT** require any other paid API keys

**NFR-2.3**: Fresh Clone Compatibility  
**WHILE** the grading process occurs  
**IF** graders clone the repository  
**THEN** they **SHALL** be able to:
1. Unzip pack into `data/`
2. Add their Gemini key to `.env`
3. Run `python run_questions.py <questions.json> <results.json>` successfully

### NFR-3: Performance

**NFR-3.1**: Startup Time  
**WHILE** the CLI launches  
**IF** `python ask.py` is executed  
**THEN** startup **SHALL** complete in under 3 seconds

**NFR-3.2**: Response Time  
**WHILE** processing a question  
**IF** `ask()` is called  
**THEN** the first answer **SHALL** return in under 10 seconds

**NFR-3.3**: Rate Limiting  
**WHILE** calling the Gemini API  
**IF** the free tier limit is approached  
**THEN** the system **SHALL** implement rate limiting  
**AND** **SHALL** wait and retry on 429, 500, 503  
**AND** **SHALL** use exponential backoff with jitter  
**AND** **SHALL** respect `retry_delay` hints

### NFR-4: Code Quality

**NFR-4.1**: Type Safety  
**WHILE** writing Python code  
**IF** defining functions  
**THEN** the code **SHALL** include type hints on all public functions

**NFR-4.2**: Documentation  
**WHILE** writing Python code  
**IF** defining public functions  
**THEN** the code **SHALL** include docstrings

**NFR-4.3**: Cleanliness  
**WHILE** maintaining the codebase  
**IF** code is committed  
**THEN** the repository **SHALL** contain no dead code, no secrets, no notebooks

**NFR-4.4**: Determinism  
**WHILE** generating answers  
**IF** randomness is involved  
**THEN** the system **SHALL** use fixed seeds and temperature 0 where possible

### NFR-5: Testing

**NFR-5.1**: Unit Test Coverage  
**WHILE** delivering the project  
**IF** core safety features exist  
**THEN** `tests/` **SHALL** include tests for:
- SQL guard rejecting writes, multiple statements, comments, PRAGMA
- Station name resolution
- Chunking preserves table rows
- Source page numbers match chunk metadata
- `ask()` never raises exceptions
- Output contract has all required keys

**NFR-5.2**: Test Set Requirements  
**WHILE** building the evaluation set  
**IF** creating `eval/test_set.json`  
**THEN** it **SHALL** contain at least 20 questions, ideally 30-40  
**AND** **SHALL** include all 10 sample questions from the pack  
**AND** **SHALL** cover every document and every scanned page  
**AND** **SHALL** include questions for:
- Each known conflict between older and newer documents
- Train-specific override rules
- Exact codes (rules, circulars, train numbers with leading zeros, slip trains)
- Overnight timetable journeys
- Multi-station cities (Chennai to Bengaluru)
- At least 4 "I don't know" cases
- At least 2 unsafe requests

### NFR-6: Evaluation and Experimentation

**NFR-6.1**: Evaluation Metrics  
**WHILE** running `eval/evaluate.py`  
**IF** testing the system  
**THEN** the script **SHALL** report:
- Hit@1, Hit@5, MRR for retrieval
- Answer accuracy (Gemini as judge + key-fact string match)
- Source precision and recall
- Correct `dont_know` rate (false refusals and false answers)
- SQL execution match (result sets, not SQL text)
- Latency per question

**NFR-6.2**: Experiment Tracking  
**WHILE** tuning the system  
**IF** making changes  
**THEN** `eval/experiments.md` **SHALL** contain a before-and-after table  
**AND** **SHALL** have one row per change (baseline, +dense, +RRF, +exact boost, +OCR, +rerank, +router, +prompt)  
**AND** changes **SHALL** be kept only if metrics improve

### NFR-7: Documentation

**NFR-7.1**: README Content  
**WHILE** documenting the project  
**IF** writing README.md  
**THEN** it **SHALL** include:
- Install steps (virtualenv, pip, .env setup, unzip pack)
- Build index command: `python build_index.py`
- Query commands: `python ask.py "question"`
- Batch mode: `python run_questions.py <in> <out>`
- Eval mode: `python eval/evaluate.py`
- Architecture diagram (Mermaid)
- "Who did what" table with GitHub usernames
- Eval score table from experiments.md
- Known limits (2016 timetable, free-tier rate limits)
- OCR engine note

**NFR-7.2**: Fresh Clone Test  
**WHILE** delivering the project  
**IF** providing test scripts  
**THEN** `scripts/fresh_clone_test.sh` **SHALL** exist  
**AND** **SHALL** clone to temp folder, unzip pack, run `run_questions.py` on 10 samples, report pass/fail

**NFR-7.3**: Dependency Specification  
**WHILE** managing dependencies  
**IF** creating `requirements.txt`  
**THEN** it **SHALL** pin exact versions of every library  
**AND** **SHALL** keep the install small and CPU-only

**NFR-7.4**: Environment Template  
**WHILE** providing configuration templates  
**IF** creating `.env.example`  
**THEN** it **SHALL** contain only:
```
GEMINI_API_KEY=
GEMINI_MODEL=
```

---

## 11. Team Collaboration Requirements

### NFR-8: Team Deliverables

**NFR-8.1**: Individual Contributions  
**WHILE** the team works on the project  
**IF** commits are made  
**THEN** every member **SHALL** have commits from their own GitHub account  
**AND** every member **SHALL** be able to explain every line they wrote

**NFR-8.2**: Task Distribution  
**WHILE** planning work  
**IF** creating `tasks.md`  
**THEN** tasks **SHALL** be ordered and small  
**AND** **SHALL** be tagged with the module and team member slot

---

## 12. Definition of Done

### Acceptance Criteria for Project Completion

**WHILE** the project deadline approaches  
**IF** evaluating completion  
**THEN** the following **SHALL** all be true:

1. All 10 sample questions return the model answer, correct sources, and correct `dont_know`
2. `python run_questions.py` works from a fresh clone with only a key and the unzipped pack
3. `git log -p` shows no key, ever
4. `eval/experiments.md` has a before-and-after table
5. `eval/test_set.json` has 20+ questions
6. Every team member has commits from their own account
7. No commits after Friday 12:00 deadline

---

## Document Metadata

| Field | Value |
|-------|-------|
| **File** | `indianrail_refund_rules_2015.html` |
| **Format** | HTML |
| **Pages** | none (page = null) |
| **Issuer** | Indian Railways, 12 Nov 2015 |
| **Notes** | Table with "Pre revised" and "Revised" columns |

| Field | Value |
|-------|-------|
| **File** | `irctc_refund_rules_jan2026.pdf` |
| **Format** | PDF, text |
| **Pages** | 11 |
| **Issuer** | IRCTC, 19 Jan 2026 |
| **Notes** | Clauses 1-16, TDR table pages 8-10 |

| Field | Value |
|-------|-------|
| **File** | `rb_cc10_2024_advance_reservation.pdf` |
| **Format** | PDF, scanned |
| **Pages** | 2 |
| **Issuer** | Railway Board, 16 Oct 2024 |
| **Notes** | p1 English, p2 Hindi, no text layer |

| Field | Value |
|-------|-------|
| **File** | `rb_cc08_2025_tatkal.pdf` |
| **Format** | PDF, mixed |
| **Pages** | 6 |
| **Issuer** | Railway Board, 10 Jun 2025 |
| **Notes** | p1-2 English text, p3-6 Hindi scanned |

| Field | Value |
|-------|-------|
| **File** | `rb_cc10_2025_reservation_charts.pdf` |
| **Format** | PDF, scanned |
| **Pages** | 2 |
| **Issuer** | Railway Board, 2 Jul 2025 |
| **Notes** | p1 Hindi, p2 English, no text layer |

| Field | Value |
|-------|-------|
| **File** | `rb_cc08_2026_vande_bharat_sleeper_refund.pdf` |
| **Format** | PDF, text |
| **Pages** | 5 |
| **Issuer** | Railway Board, 19 Jan 2026, gazette G.S.R. 41(E) of 16 Jan 2026 |
| **Notes** | p1-2 circular, p3-4 gazette Hindi, p5 gazette English |

| Field | Value |
|-------|-------|
| **File** | `pib_2026-03-24_reform_express.html` |
| **Format** | HTML |
| **Pages** | none (page = null) |
| **Issuer** | PIB Delhi, 24 Mar 2026 |
| **Notes** | Only "Ticket cancellation and refund" and "Change of Train Boarding Point" sections matter to passengers |

---

**Database**: `rail_timetable.db` (SQLite, 2016 snapshot, ~28 MB)

- `stations`: 8,990 rows (code PK, name, state, zone, address, lat, lon)
- `train_types`: 16 rows (type_code PK, meaning)
- `trains`: 5,208 rows (number TEXT PK, name, type_code, zone, from/to station, departure/arrival, duration, distance, return_train, class availability flags)
- `schedules`: 417,080 rows (train_number, stop_sequence PK, station_code, day, arrival, departure, halt_min, is_halt)
- `stops` (view): schedules WHERE is_halt = 1, 104,151 rows

---

**End of Requirements**
