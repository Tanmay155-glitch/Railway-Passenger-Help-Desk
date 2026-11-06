# Railway Help Desk - Manual Execution Guide

This guide provides step-by-step instructions to manually set up and run the Railway Help Desk project.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Building the Index](#building-the-index)
- [Running the Application](#running-the-application)
- [Testing the System](#testing-the-system)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you start, ensure you have the following installed:

1. **Python 3.9 or higher**
   ```powershell
   python --version
   ```

2. **pip (Python package manager)**
   ```powershell
   pip --version
   ```

3. **Virtual environment support** (usually included with Python)

---

## Initial Setup

### Step 1: Navigate to Project Directory

Open PowerShell and navigate to the project folder:

```powershell
cd "c:\Users\tanma\OneDrive\Desktop\Carrier TIQ Classes\rail_capstone_pack"
```

### Step 2: Create Virtual Environment

If not already created, create a virtual environment:

```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**On Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**On Windows Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

You should see `(.venv)` prefix in your terminal prompt, indicating the virtual environment is active.

### Step 4: Install Dependencies

Install all required Python packages:

```powershell
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- google-generativeai (Gemini API)
- fastembed (embeddings)
- rank-bm25 (BM25 search)
- PyMuPDF/fitz (PDF processing)
- beautifulsoup4 (HTML parsing)
- python-dotenv (environment variables)
- Other dependencies

### Step 5: Configure Environment Variables

1. Create a `.env` file in the project root (if not exists):
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit the `.env` file and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

   To get a Gemini API key:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Create a new API key
   - Copy and paste it into the `.env` file

---

## Building the Index

The system requires a document index to answer questions. Build it once before first use.

### Step 6: Run the Index Builder

```powershell
python build_index.py
```

**What this does:**
- Parses all PDF and HTML documents in the `documents/` folder
- Extracts text from each page (with OCR for scanned PDFs)
- Creates text chunks with metadata (document name, page number)
- Builds a BM25 index for keyword search
- Generates embeddings for semantic search
- Saves everything to the `index/` folder

**Expected output:**
```
Building document index...
Processing: indianrail_refund_rules_2015.html
Processing: irctc_refund_rules_jan2026.pdf
...
Index built successfully!
Chunks: 234
Files saved to: index/
```

**Time estimate:** 2-5 minutes depending on your system

**Files created:**
- `index/chunks.json` - All text chunks with metadata
- `index/bm25.pkl` - BM25 index for keyword search
- `index/manifest.json` - Index metadata
- `index/schema.txt` - Database schema for SQL generation

---

## Running the Application

You can run the application in two ways:

### Option A: Web Interface (Recommended)

**Step 7a: Start the Flask Server**

```powershell
python app.py
```

**Expected output:**
```
============================================================
Railway Help Desk - Web Interface
============================================================

Starting server...
Open your browser and go to: http://localhost:5000

Press CTRL+C to stop the server
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**Step 8a: Open Your Browser**

Navigate to: **http://localhost:5000**

You'll see a user-friendly web interface where you can:
- Type questions in natural language
- View answers with source citations
- See SQL queries for database questions
- Get formatted responses

**Step 9a: Stop the Server**

Press `CTRL+C` in the terminal to stop the server.

---

### Option B: Command-Line Interface

**Step 7b: Run Questions via CLI**

For quick testing or automation, use the command-line interface:

```powershell
python ask.py "What is the refund for RAC ticket?"
```

**Output format:**
```json
{
  "answer": "For RAC (Reservation Against Cancellation) tickets...",
  "sources": [
    {"doc": "irctc_refund_rules_jan2026.pdf", "page": 3}
  ],
  "sql": null,
  "dont_know": false
}
```

**Example questions to try:**

```powershell
# Refund policy question
python ask.py "What is the cancellation charge for AC First Class?"

# Timetable question
python ask.py "Which trains go from Mumbai to Delhi?"

# Booking rules question
python ask.py "How many days in advance can I book a train ticket?"

# Tatkal rules
python ask.py "What documents are required for Tatkal booking?"
```

---

## Testing the System

### Step 8: Test with Sample Questions

The project includes sample questions with expected answers:

```powershell
python -m pytest tests/ -v
```

Or test individual questions:

```powershell
# Test with evaluation script
python eval/evaluate.py
```

### Step 9: Test the Web API

If running the web server, you can test the API using PowerShell:

```powershell
$body = @{
    question = "What is the refund for confirmed ticket?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/ask" -Method POST -Body $body -ContentType "application/json"
```

Or use curl:

```powershell
curl -X POST http://localhost:5000/ask `
  -H "Content-Type: application/json" `
  -d '{"question":"What is the refund for confirmed ticket?"}'
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. **Virtual Environment Activation Error**

**Error:** "Execution of scripts is disabled on this system"

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

---

#### 2. **Module Not Found Error**

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
Ensure virtual environment is activated and reinstall dependencies:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

#### 3. **API Key Error**

**Error:** "GEMINI_API_KEY not found in environment"

**Solution:**
1. Check `.env` file exists in project root
2. Verify it contains: `GEMINI_API_KEY=your_key_here`
3. Restart the application

---

#### 4. **Port Already in Use**

**Error:** `Address already in use`

**Solution:**
Either:
- Stop the existing server (CTRL+C)
- Use a different port:
  ```powershell
  $env:FLASK_RUN_PORT=5001; python app.py
  ```
- Find and kill the process using port 5000:
  ```powershell
  Get-NetTCPConnection -LocalPort 5000 | Select-Object -ExpandProperty OwningProcess | Stop-Process
  ```

---

#### 5. **Database Not Found**

**Error:** "Unable to open database file"

**Solution:**
Verify the database exists:
```powershell
Test-Path "database\rail_timetable.db"
```

The database should be in the `database/` folder (or `data/database/`).

---

#### 6. **Index Not Built**

**Error:** "Index files not found"

**Solution:**
Build the index first:
```powershell
python build_index.py
```

---

#### 7. **SSL Certificate Error (Windows)**

**Error:** `ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**Solution:**
The project is configured to use REST transport for Windows. If you still get SSL errors, check your `.env` file or add:
```python
# In your code or config
import os
os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = ''
```

---

## Quick Reference

### Essential Commands

| Action | Command |
|--------|---------|
| Activate virtual environment | `.\.venv\Scripts\Activate.ps1` |
| Deactivate virtual environment | `deactivate` |
| Install dependencies | `pip install -r requirements.txt` |
| Build index | `python build_index.py` |
| Start web server | `python app.py` |
| Ask a question (CLI) | `python ask.py "your question"` |
| Run tests | `python -m pytest tests/ -v` |
| Stop server | Press `CTRL+C` |

### Project Structure

```
rail_capstone_pack/
├── app.py                 # Web server entry point
├── ask.py                 # CLI entry point
├── build_index.py         # Index builder script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── helpdesk/             # Core system modules
│   ├── pipeline.py       # Main ask() function
│   ├── router.py         # Question routing
│   ├── search.py         # Document search
│   ├── sql.py            # Text-to-SQL
│   ├── answer.py         # Answer generation
│   └── ...
├── data/                 # Documents + database
│   ├── documents/        # Source PDFs and HTML
│   ├── database/         # SQLite timetable
│   └── questions/        # Sample questions
├── index/                # Built search index
├── templates/            # HTML templates
└── static/               # CSS, JavaScript
```

---

## Next Steps

After successfully running the application:

1. **Try the sample questions** in `questions/sample_questions.json`
2. **Review the design document** in `design.md`
3. **Experiment with different question types**:
   - Refund rules
   - Booking policies
   - Train schedules
   - Station information
4. **Check the evaluation results** in the `eval/` folder
5. **Read the compliance report** in `COMPLIANCE_REPORT.md`

---

## Support

For more information:
- See `README.md` for project overview
- See `design.md` for system architecture
- See `database/schema.md` for database structure
- See `SOURCES.md` for document sources

---

**Happy querying! 🚂**
