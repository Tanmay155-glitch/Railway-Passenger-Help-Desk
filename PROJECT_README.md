# Railway Passenger Help Desk

**GenAI Nexus Capstone - Module 2**

A Python command-line application that answers passenger questions about Indian Railways using official documents and timetable data.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Architecture](#architecture)
- [Project Status](#project-status)
- [Team](#team)

---

## 🎯 Overview

This system answers passenger queries using:
- **Official Railway Documents**: Refund rules, Railway Board circulars, PIB press releases
- **Timetable Database**: SQLite database with train schedules (2016 snapshot, 8,990 stations, 5,208 trains)

**Key Constraint**: All answers must come from the data pack. No web search, no hard-coded facts.

---

## ✨ Features

- **Hybrid Search**: BM25 + dense embeddings with exact-match boosting
- **Safe SQL**: Read-only database access with 6 layers of protection
- **Grounded Answers**: Citations with exact document and page numbers
- **Document Precedence**: Newer rules automatically override older ones
- **OCR Support**: Extracts text from scanned PDF pages
- **Interactive CLI**: User-friendly command-line interface

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Gemini API key (free tier) from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tanmay155-glitch/Railway-Passenger-Help-Desk.git
   cd Railway-Passenger-Help-Desk
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   # GEMINI_API_KEY=your_key_here
   ```

5. **Build the index** (one-time setup)
   ```bash
   python build_index.py
   ```
   
   This will:
   - Ingest all documents
   - Apply OCR to scanned pages
   - Create searchable index
   - Takes ~2-3 minutes

---

## ⚡ Quick Start

### Ask a single question
```bash
python ask.py "What is the refund for a Tatkal ticket cancelled 12 hours before departure?"
```

### Interactive mode
```bash
python ask.py

# Then type your questions at the prompt
# Type :examples to see demo questions
# Type exit to quit
```

### JSON output
```bash
python ask.py --json "What is Rule 25?"
```

### Debug mode
```bash
python ask.py --debug "Which trains go from Delhi to Mumbai?"
```

---

## 📖 Usage

### Command-Line Interface

**Basic usage:**
```bash
python ask.py "your question here"
```

**Options:**
- `--json` : Output in JSON format
- `--debug` : Show route, retrieved chunks, scores, timings

**Interactive commands:**
- `:examples` : Show 5 demo questions
- `exit` or `:exit` : Quit

### Batch Processing

Process multiple questions from a JSON file:

```bash
python run_questions.py questions/sample_questions.json results.json
```

Input format:
```json
[
  {"id": "Q01", "question": "What is the cancellation charge?"},
  {"id": "Q02", "question": "Which trains go to Mumbai?"}
]
```

Output format:
```json
[
  {
    "id": "Q01",
    "question": "What is the cancellation charge?",
    "answer": "...",
    "sources": [{"doc": "file.pdf", "page": 3}],
    "sql": null,
    "dont_know": false
  }
]
```

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "User Interface"
        CLI[ask.py CLI]
        Batch[run_questions.py]
    end

    subgraph "Core Pipeline"
        Pipeline[pipeline.py<br/>ask function]
        Router[Intent Router<br/>docs|db|both|refuse]
    end

    subgraph "Document Path"
        Search[search.py<br/>Hybrid Retrieval<br/>BM25 + Embeddings]
        Answer[answer.py<br/>Grounded Generation]
    end

    subgraph "Database Path"
        SQL[sql.py<br/>Text-to-SQL + Guard]
    end

    subgraph "Data Layer"
        Index[(index/<br/>Chunks + Embeddings)]
        DB[(rail_timetable.db<br/>SQLite)]
    end

    CLI --> Pipeline
    Batch --> Pipeline
    Pipeline --> Router
    Router --> Search
    Router --> SQL
    Search --> Answer
    Answer --> Index
    SQL --> DB
```

### Key Components

| Module | Purpose |
|--------|---------|
| `config.py` | Configuration and environment validation |
| `llm.py` | Gemini API client with retry logic |
| `ingest.py` | PDF/HTML parsing, OCR, chunking |
| `entities.py` | Extract identifiers (rules, trains, amounts) |
| `search.py` | Hybrid retrieval (BM25 + embeddings) |
| `sql.py` | Safe text-to-SQL generation |
| `answer.py` | Grounded answer generation |
| `pipeline.py` | Orchestration and routing |

---

## 📊 Project Status

### ✅ Completed (Day 1)

- [x] Project scaffolding
- [x] Configuration module with environment validation
- [x] Gemini LLM client with retry logic
- [x] Document metadata catalog
- [x] Entity extraction (rules, circulars, trains, amounts)
- [x] PDF ingestion with OCR support
- [x] HTML parsing with table handling
- [x] Document chunking (150-400 words, clause-aware)
- [x] Build index script
- [x] CLI with interactive mode
- [x] Pipeline stub with error handling
- [x] Unit tests for contract and entity extraction

### 🚧 In Progress (Day 2)

- [ ] BM25 search implementation
- [ ] Dense embedding generation
- [ ] Reciprocal Rank Fusion
- [ ] Exact-match boosting
- [ ] Station name resolution
- [ ] SQL generation with guards
- [ ] Safe SQL execution

### 📅 Upcoming (Days 3-4)

- [ ] Answer generation with precedence rules
- [ ] Router implementation
- [ ] Complete pipeline integration
- [ ] Expand test set to 30+ questions
- [ ] Full evaluation suite
- [ ] Performance tuning
- [ ] Documentation

---

## 👥 Team

**GenAI Nexus - Cohort 1, Module 2**

| Member | Role | Modules | GitHub |
|--------|------|---------|--------|
| Member A | Document Processing | `ingest.py`, `build_index.py` | [@username-A](https://github.com/username-A) |
| Member B | Search & Retrieval | `search.py`, `llm.py` | [@username-B](https://github.com/username-B) |
| Member C | SQL & Answers | `sql.py`, `answer.py` | [@username-C](https://github.com/username-C) |
| Member D | Pipeline & Integration | `pipeline.py`, `ask.py`, eval | [@Tanmay155-glitch](https://github.com/Tanmay155-glitch) |

---

## 📄 Data Pack Contents

### Documents (7 files)

| File | Issuer | Date | Type | Notes |
|------|--------|------|------|-------|
| `indianrail_refund_rules_2015.html` | Indian Railways | 2015-11-12 | HTML | Refund rules table |
| `irctc_refund_rules_jan2026.pdf` | IRCTC | 2026-01-19 | PDF | 16 clauses + TDR table |
| `rb_cc10_2024_advance_reservation.pdf` | Railway Board | 2024-10-16 | PDF | Scanned (EN/HI) |
| `rb_cc08_2025_tatkal.pdf` | Railway Board | 2025-06-10 | PDF | Mixed text/scan |
| `rb_cc10_2025_reservation_charts.pdf` | Railway Board | 2025-07-02 | PDF | Scanned (HI/EN) |
| `rb_cc08_2026_vande_bharat_sleeper_refund.pdf` | Railway Board | 2026-01-19 | PDF | Gazette notification |
| `pib_2026-03-24_reform_express.html` | PIB Delhi | 2026-03-24 | HTML | Policy announcements |

### Database

- **File**: `database/rail_timetable.db` (SQLite, ~28 MB)
- **Tables**: stations (8,990), trains (5,208), schedules (417,080), stops (view)
- **Snapshot**: 2016 data

---

## ⚠️ Known Limitations

1. **2016 Timetable**: No recent trains (Vande Bharat, recent routes)
2. **No Live Data**: Cannot answer PNR status, seat availability, current running status
3. **No Fares**: Fare information not in the data pack
4. **Free Tier Limits**: Gemini API rate limits apply (~15 requests/minute)
5. **OCR Accuracy**: Hindi pages may have lower accuracy

---

## 🔒 Security

- API keys stored in `.env` (git-ignored)
- SQL injection prevention with 6 layers of guards
- Read-only database access
- No data modification allowed

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

This is a capstone project. For the duration of the course, contributions are limited to team members. After submission, we welcome feedback and suggestions via issues.

---

## 📚 Documentation

- [README.md](README.md) - Data pack documentation (original from course)
- [Requirements](requirements.md) - Detailed functional requirements (EARS style)
- [Design](design.md) - Architecture, data model, module interfaces
- [Tasks](tasks.md) - Day-by-day task breakdown with ownership

---

## 🎓 Academic Integrity

This project is part of GenAI Nexus Programme, Cohort 1, Module 2. All code is original work by the team, with proper attribution for libraries and tools used.

**Deadline**: Friday, 6 November 2026, 12:00 PM

---

**Built with ❤️ by the GenAI Nexus Team**
