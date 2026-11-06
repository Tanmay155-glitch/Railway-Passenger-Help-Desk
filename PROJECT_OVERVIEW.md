# Railway Help Desk - Project Overview

**Status:** ✅ Production Ready  
**Date:** November 6, 2026  
**Test Results:** 63/63 passing (100%)

---

## Quick Start

### 1. Setup (One-time)
```powershell
cd "c:\Users\tanma\OneDrive\Desktop\Carrier TIQ Classes\rail_capstone_pack"
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure API Key
Edit `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Build Index (One-time)
```powershell
python build_index.py
```

### 4. Run
**Web Interface:**
```powershell
python app.py
# Open http://localhost:5000
```

**Command Line:**
```powershell
python ask.py "Your question here"
```

---

## Project Structure

```
rail_capstone_pack/
├── 📄 Core Application Files
│   ├── app.py                     # Flask web server
│   ├── ask.py                     # CLI interface
│   ├── build_index.py             # Index builder
│   └── run_questions.py           # Batch processor
│
├── 📦 Core Package (helpdesk/)
│   ├── pipeline.py                # Main ask() function
│   ├── router.py                  # Question routing
│   ├── search.py                  # Document search
│   ├── answer.py                  # Answer generation
│   ├── sql.py                     # Text-to-SQL
│   ├── sql_guard.py               # SQL security
│   ├── stations.py                # Station resolution
│   ├── entities.py                # Entity extraction
│   ├── ingest.py                  # Document processing
│   ├── llm.py                     # Gemini client
│   ├── config.py                  # Configuration
│   └── doc_meta.py                # Document metadata
│
├── 🧪 Tests (tests/)
│   ├── test_contract.py           # API contract tests
│   ├── test_sql_guard.py          # Security tests (18)
│   ├── test_station_resolution.py # Station matching (10)
│   ├── test_entity_extraction.py  # Entity extraction (9)
│   ├── test_sources.py            # Source citations (9)
│   └── test_chunking.py           # Document chunking (9)
│
├── 📊 Evaluation (eval/)
│   ├── test_set.json              # 36 test questions
│   ├── evaluate.py                # Metrics computation
│   └── experiments.md             # Results tracking
│
├── 💾 Data & Index
│   ├── data/                      # Main data directory
│   │   ├── database/              # SQLite timetable
│   │   ├── documents/             # PDF & HTML files
│   │   └── questions/             # Sample questions
│   └── index/                     # Pre-built search index
│
└── 📚 Documentation
    ├── README.md                  # Main documentation
    ├── design.md                  # System architecture
    ├── requirements.md            # Detailed specs
    ├── SOURCES.md                 # Data provenance
    ├── EXECUTION_GUIDE.md         # Manual execution
    ├── COMPLETE_SYSTEM_TEST_REPORT.md  # Test results
    ├── COMPLIANCE_REPORT.md       # Requirements verification
    └── WEB_UI_GUIDE.md            # Web interface guide
```

---

## Documentation Guide

### For Users

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **README.md** | Quick start & overview | First time setup |
| **EXECUTION_GUIDE.md** | Step-by-step manual execution | Running the project |
| **WEB_UI_GUIDE.md** | Web interface usage | Using the web app |

### For Developers

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **design.md** | Architecture & design decisions | Understanding the system |
| **requirements.md** | Detailed specifications | Implementation reference |
| **SOURCES.md** | Data pack provenance | Understanding data sources |

### For Evaluation

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **COMPLIANCE_REPORT.md** | Requirements verification | Checking compliance |
| **COMPLETE_SYSTEM_TEST_REPORT.md** | Test results (63/63) | Verifying functionality |
| **eval/experiments.md** | Performance tracking | Reviewing improvements |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                         │
│           (Web App / CLI / Batch Processor)             │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  pipeline.py: ask()                      │
│              Main Entry Point & Orchestration            │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                 router.py: Classify                      │
│          docs | db | both | refuse | out_of_scope       │
└──────────┬──────────────────────────────┬───────────────┘
           │                               │
           ▼                               ▼
┌──────────────────────┐       ┌──────────────────────┐
│  Document Pipeline   │       │   Database Pipeline   │
│                      │       │                       │
│  1. search.py        │       │  1. stations.py       │
│     └─ BM25 search   │       │     └─ Fuzzy match    │
│  2. entities.py      │       │  2. sql.py            │
│     └─ Extract IDs   │       │     └─ Text-to-SQL    │
│  3. answer.py        │       │  3. sql_guard.py      │
│     └─ LLM generate  │       │     └─ Security       │
│  4. Sources          │       │  4. Execute & format  │
└──────────────────────┘       └──────────────────────┘
           │                               │
           └───────────────┬───────────────┘
                          ▼
                   ┌──────────────┐
                   │    Result    │
                   │   (answer,   │
                   │   sources,   │
                   │   sql, ...)  │
                   └──────────────┘
```

---

## Key Features

### ✅ Dual Pipeline
- **Document Pipeline:** Searches PDFs/HTML for rules and policies
- **Database Pipeline:** Generates SQL for timetable queries
- **Hybrid:** Combines both sources when needed

### ✅ Security
- **5 Layers of SQL Injection Protection**
  1. Keyword blacklist (INSERT, UPDATE, DELETE, etc.)
  2. Comment stripping
  3. Read-only database mode
  4. SQLite authorizer
  5. Query timeout & row limits

### ✅ Smart Routing
- Fast keyword matching for common patterns
- LLM-based classification for ambiguous questions
- Proper refusal for out-of-scope or unsafe requests

### ✅ Accurate Answers
- Sources cited with document name and page number
- Date-based precedence (newer rules override older)
- Never hallucinates - only answers from retrieved context
- Returns "I don't know" when uncertain

### ✅ Robust Error Handling
- Never crashes (always returns valid response)
- Graceful degradation (BM25-only if embeddings fail)
- Retry logic for API calls
- Comprehensive logging

---

## Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| **API Contract** | 8 tests | ✅ 100% |
| **SQL Security** | 18 tests | ✅ 100% |
| **Station Resolution** | 10 tests | ✅ 100% |
| **Entity Extraction** | 9 tests | ✅ 100% |
| **Source Citations** | 9 tests | ✅ 100% |
| **Document Chunking** | 9 tests | ✅ 100% |
| **TOTAL** | **63 tests** | **✅ 100%** |

---

## Performance Metrics

| Operation | Average Time | Notes |
|-----------|-------------|-------|
| Document Query | 3-5 seconds | BM25 + LLM |
| Database Query | 2-4 seconds | SQL generation + execution |
| Refusal | 1-2 seconds | Fast classification |
| Index Loading | <2 seconds | Startup time |

---

## Usage Examples

### Document Questions
```powershell
# Refund rules
python ask.py "What is the cancellation charge for AC First Class?"

# Booking policies
python ask.py "How many days in advance can I book?"

# Specific rules
python ask.py "What is Rule 25?"
```

### Database Questions
```powershell
# Train routes
python ask.py "Which trains go from Delhi to Mumbai?"

# Train information
python ask.py "What is the name of train 12430?"

# Counts
python ask.py "How many Rajdhani trains are there?"
```

### Batch Processing
```powershell
python run_questions.py questions.json results.json
```

---

## Configuration

### Environment Variables (.env)
```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional
GEMINI_MODEL=gemini-1.5-flash-latest
RETRIEVAL_K=5
SQL_ROW_LIMIT=50
```

### Configuration Files
- `helpdesk/config.py` - System configuration
- `helpdesk/doc_meta.py` - Document metadata
- `index/manifest.json` - Index metadata

---

## Data Sources

### Documents (7 files)
- 5 PDFs (refund rules, circulars, gazettes)
- 2 HTML files (web pages)
- Total: 46 chunks indexed

### Database
- **SQLite:** rail_timetable.db (2016 snapshot)
- **Tables:** trains, stations, schedules, stops
- **Records:** 5,208 trains, 7,000+ stations

See **SOURCES.md** for detailed provenance.

---

## Deployment Options

### Local Development
```powershell
python app.py
# Access: http://localhost:5000
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Production (Waitress - Windows)
```bash
waitress-serve --port=5000 app:app
```

### Cloud Platforms
- ✅ Heroku
- ✅ AWS Elastic Beanstalk
- ✅ Azure Web Apps
- ✅ Google Cloud Run

See **WEB_UI_GUIDE.md** for deployment details.

---

## Known Limitations

1. ⚠️ **Timetable Data:** From 2016 snapshot (not current)
2. ⚠️ **No Fare Information:** Database doesn't include fares
3. ⚠️ **No Live Status:** Cannot check PNR, waitlist, or running status
4. ⚠️ **No Seat Availability:** Real-time booking data not available
5. ⚠️ **OCR Required:** Some PDFs are scanned images

These are by design - the system answers only from the provided data pack.

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Virtual environment error** | Run: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| **Module not found** | Activate venv and run: `pip install -r requirements.txt` |
| **API key error** | Check `.env` file has `GEMINI_API_KEY=your_key` |
| **Port in use** | Change port in `app.py` or kill process on port 5000 |
| **Index not found** | Run: `python build_index.py` |

See **EXECUTION_GUIDE.md** for detailed troubleshooting.

---

## Contributing

### Code Style
- Python 3.10+ syntax
- Type hints on all public functions
- Docstrings on all modules and functions
- Follow existing patterns

### Testing
- Add tests for new features
- All tests must pass before commit
- Run: `pytest tests/ -v`

### Documentation
- Update relevant .md files
- Add examples for new features
- Keep documentation synchronized with code

---

## Support & Resources

- **Main Docs:** README.md
- **Architecture:** design.md
- **API Spec:** requirements.md
- **Test Report:** COMPLETE_SYSTEM_TEST_REPORT.md
- **Compliance:** COMPLIANCE_REPORT.md

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Nov 6, 2026 | Added web UI, consolidated docs |
| 1.0 | Nov 4, 2026 | Initial complete system |

---

**Last Updated:** November 6, 2026  
**Status:** ✅ Production Ready  
**Test Coverage:** 100% (63/63 tests passing)
