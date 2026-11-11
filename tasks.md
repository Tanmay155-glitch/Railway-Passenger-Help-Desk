# Task Breakdown
## Railway Passenger Help Desk - GenAI Nexus Capstone

**Timeline**: Monday 2 Nov → Friday 6 Nov, 12:00 deadline  
**Status**: ✅ **COMPLETED - Production Ready**  
**Final Test Results**: 80% accuracy (16/20 questions answered, 4/4 refused correctly)  
**Date Completed**: November 11, 2026

---

## 🎯 Project Status Summary

### ✅ All Critical Components Completed
- ✅ Document ingestion (PDF, HTML, OCR)
- ✅ Search system (BM25 + semantic)
- ✅ Text-to-SQL generation
- ✅ SQL security guards
- ✅ Answer generation with LLM
- ✅ Pipeline routing
- ✅ CLI interface (ask.py)
- ✅ Batch processing (run_questions.py)
- ✅ 51 unit tests (all passing)
- ✅ Comprehensive testing (80% accuracy)

### 📊 Performance Metrics
- **Response Time**: ~5 seconds average
- **Accuracy**: 80% (16/20 answered correctly)
- **SQL Success**: 100% (6/6 queries)
- **Refusal Accuracy**: 100% (4/4 out-of-scope refused)
- **Projected Score**: 94/100

### 📝 Documentation Status
- ✅ README.md - Complete with setup and usage
- ✅ design.md - System architecture documented
- ✅ requirements.md - Specifications complete
- ✅ SOURCES.md - Data provenance documented
- ✅ TEST_RESULTS_SUMMARY.md - Test results documented
- ✅ eval/experiments.md - Performance tracking

---

## Original Task Breakdown

**Team**: 4 members (A, B, C, D)  
**Workflow**: Sequential tasks with clear dependencies

---

## Task Ownership Guide

- **Member A**: Document ingestion, OCR, build process
- **Member B**: Search, retrieval, embeddings, LLM client
- **Member C**: SQL generation, guards, grounded answer generation
- **Member D**: Pipeline routing, CLI, batch processing, integration

---

## Day 1: Monday, 2 November (Foundation)

### Task 1.1: Project Scaffolding [ALL] ⏱️ 30 min
**Dependencies**: None  
**Owner**: Member D (lead), all participate

- [ ] Create repository structure
- [ ] Initialize git repo with main branch
- [ ] Create `.gitignore`: `.env`, `.venv/`, `data/`, `index/cache/`, `__pycache__/`, `*.pyc`
- [ ] Create directories: `helpdesk/`, `index/`, `eval/`, `tests/`, `scripts/`
- [ ] Create `helpdesk/__init__.py` (empty)
- [ ] Create `.env.example` with:
  ```
  GEMINI_API_KEY=
  GEMINI_MODEL=gemini-1.5-flash-latest
  ```
- [ ] Each member creates a feature branch from main
- [ ] Initial commit with structure

**Output**: Clean repo structure, all members can push

---

### Task 1.2: Configuration Module [Member D] ⏱️ 45 min
**Dependencies**: 1.1  
**Owner**: Member D  
**Branch**: `feature/member-D-config`

- [ ] Create `helpdesk/config.py` with Config dataclass
- [ ] Include all constants from design.md section 3.1
- [ ] Add function to load from `.env` using `python-dotenv`
- [ ] Add path discovery: `find_data_pack()` that uses `Path("data").rglob("rail_timetable.db")`
- [ ] Handle missing data pack gracefully (return None, don't crash)
- [ ] Write docstrings

**Output**: `helpdesk/config.py` with type hints and docstrings

---

### Task 1.3: Document Metadata Catalog [Member A] ⏱️ 30 min
**Dependencies**: 1.1  
**Owner**: Member A  
**Branch**: `feature/member-A-ingest`

- [ ] Create `helpdesk/doc_meta.py`
- [ ] Define `DOC_METADATA` dict with all 7 documents
- [ ] Include: issuer, date, doc_type, scanned_pages, lang, notes
- [ ] Add `get_metadata(filename) -> Optional[dict]` function
- [ ] Write docstrings

**Output**: `helpdesk/doc_meta.py` with complete metadata

---

### Task 1.4: LLM Client Foundation [Member B] ⏱️ 2 hours
**Dependencies**: 1.2  
**Owner**: Member B  
**Branch**: `feature/member-B-llm`

- [ ] Create `helpdesk/llm.py`
- [ ] Install `google-generativeai`, `python-dotenv`
- [ ] Implement `GeminiClient.__init__(api_key, model)`
- [ ] Implement `generate(prompt, schema, temperature, timeout)` with:
  - Basic call to Gemini
  - Temperature 0 default
  - JSON mode when schema provided
  - Try/except for common errors
- [ ] Implement exponential backoff for 429, 500, 503
- [ ] Add jitter to backoff: `time.sleep(delay * (1 + random.uniform(-0.1, 0.1)))`
- [ ] Never log API key
- [ ] Implement simple rate limiter (15 requests per minute)
- [ ] Test with a sample prompt

**Output**: `helpdesk/llm.py` with working Gemini calls and retry logic

---

### Task 1.5: PDF Ingestion (Text Extraction) [Member A] ⏱️ 2 hours
**Dependencies**: 1.3  
**Owner**: Member A  
**Branch**: `feature/member-A-ingest`

- [ ] In `helpdesk/ingest.py`, implement `ingest_pdf(pdf_path, metadata)`
- [ ] Install `PyMuPDF` (import as `fitz`)
- [ ] Extract text page by page
- [ ] Return list of page dicts: `{"page_num": int, "text": str, "needs_ocr": bool}`
- [ ] Mark page as `needs_ocr=True` if `len(text) < 50`
- [ ] Keep page metadata (doc, issuer, date from metadata param)
- [ ] Write docstrings

**Output**: PDF text extraction working (no OCR yet)

---

### Task 1.6: HTML Ingestion [Member A] ⏱️ 1.5 hours
**Dependencies**: 1.3  
**Owner**: Member A  
**Branch**: `feature/member-A-ingest`

- [ ] In `helpdesk/ingest.py`, implement `ingest_html(html_path, metadata)`
- [ ] Install `beautifulsoup4`, `lxml`
- [ ] Parse HTML, drop `<script>`, `<style>`, `<nav>`
- [ ] Special handling for 2015 table:
  - Identify the refund rules table
  - Extract one row at a time
  - Each chunk includes column headers "Pre revised" and "Revised"
- [ ] Special handling for PIB HTML:
  - Extract "Ticket cancellation and refund" section
  - Extract "Change of Train Boarding Point" section
  - Mark freight/construction sections with low weight
- [ ] Return list of chunk dicts
- [ ] Write docstrings

**Output**: HTML parsing with table row preservation

---

### Task 1.7: Chunking Logic [Member A] ⏱️ 2 hours
**Dependencies**: 1.5, 1.6  
**Owner**: Member A  
**Branch**: `feature/member-A-ingest`

- [ ] In `helpdesk/ingest.py`, implement `chunk_document(pages, metadata)`
- [ ] Split on clause patterns: `r'^\d+\.'`, `r'^\([a-z]\)'`, `r'^Rule \d+'`, headings with `:-`
- [ ] Target 150-400 words per chunk
- [ ] Never split a clause or table row
- [ ] Add one-clause overlap between chunks
- [ ] Prepend header to each chunk: `[{doc} | page {page} | {issuer} | {date} | clause {clause}]`
- [ ] Generate `chunk_id`: `{doc_stem}_p{page:02d}_c{chunk_num:02d}`
- [ ] Call `extract_identifiers(text)` (stub for now)
- [ ] Return list of chunk dicts with all metadata fields
- [ ] Write docstrings

**Output**: Chunking with headers and clause preservation

---

### Task 1.8: Entity Extraction [Member C] ⏱️ 1.5 hours
**Dependencies**: None (standalone)  
**Owner**: Member C  
**Branch**: `feature/member-C-entities`

- [ ] Create `helpdesk/entities.py`
- [ ] Implement `extract_identifiers(text) -> dict`
- [ ] Regex patterns:
  - `rules`: `r'Rule\s+\d+[A-Z]?'`
  - `circulars`: `r'C[CG]\s*\d+\s*/\s*\d{4}'` or `r'Circular\s+\w+\s+of\s+\d{4}'`
  - `gazettes`: `r'G\.S\.R\.\s+\d+\([A-Z]\)'`
  - `trains`: `r'\b\d{5}(?:-Slip)?\b'`
  - `amounts`: `r'₹\s*\d+(?:,\d+)*'` or `r'\d+%'`
- [ ] Return dict: `{"rules": [...], "circulars": [...], "gazettes": [...], "trains": [...], "amounts": [...]}`
- [ ] Handle empty matches (return empty lists)
- [ ] Write unit tests in `tests/test_entity_extraction.py`
- [ ] Write docstrings

**Output**: `helpdesk/entities.py` with tests

---

### Task 1.9: OCR Implementation [Member A] ⏱️ 2 hours
**Dependencies**: 1.5  
**Owner**: Member A  
**Branch**: `feature/member-A-ingest`

- [ ] In `helpdesk/ingest.py`, implement `ocr_page(image_bytes, lang)`
- [ ] Install `rapidocr-onnxruntime`
- [ ] Try `rapidocr` first
- [ ] If import fails, fall back to `pytesseract`
- [ ] Render PDF page to image at 300 DPI using PyMuPDF: `page.get_pixmap(dpi=300)`
- [ ] Handle `lang="en"` and `lang="hi"`
- [ ] Return extracted text
- [ ] Integrate into `ingest_pdf()`: if `needs_ocr`, call `ocr_page()`
- [ ] Write docstrings

**Output**: OCR working for scanned pages

---

### Task 1.10: Build Index Script Foundation [Member A] ⏱️ 1 hour
**Dependencies**: 1.2, 1.3, 1.7, 1.9  
**Owner**: Member A  
**Branch**: `feature/member-A-build`

- [ ] Create `build_index.py`
- [ ] Discover data pack using `config.find_data_pack()`
- [ ] Exit with clear message if not found: "Unzip rail_capstone_pack.zip into data/"
- [ ] For each document in `doc_meta.DOC_METADATA`:
  - Find file using `Path("data").rglob(filename)`
  - Call `ingest_pdf()` or `ingest_html()`
  - Call `chunk_document()`
  - Accumulate chunks
- [ ] Print progress: "Processing {doc}..."
- [ ] Save all chunks to `index/chunks.json`
- [ ] Print summary table: doc | pages | ocr'd pages
- [ ] Fail loudly if any PDF page has no text and no OCR
- [ ] Write docstrings

**Output**: `build_index.py` ingests documents, creates `index/chunks.json`

---

### Task 1.11: Pipeline Stub and Contract [Member D] ⏱️ 1 hour
**Dependencies**: 1.2  
**Owner**: Member D  
**Branch**: `feature/member-D-pipeline`

- [ ] Create `helpdesk/pipeline.py`
- [ ] Implement `ask(question: str) -> dict` with:
  - Try/except wrapper around everything
  - On any error, return `{"answer": "Internal error: {e}", "sources": [], "sql": None, "dont_know": True}`
  - For now, always return `{"answer": "Not implemented yet", "sources": [], "sql": None, "dont_know": True}`
- [ ] Add type hints
- [ ] Write docstrings
- [ ] Create unit test in `tests/test_contract.py`:
  - Test all keys present
  - Test `ask()` never raises
  - Test output types

**Output**: `helpdesk/pipeline.py` stub with contract test

---

### Task 1.12: CLI Stub [Member D] ⏱️ 45 min
**Dependencies**: 1.11  
**Owner**: Member D  
**Branch**: `feature/member-D-cli`

- [ ] Create `ask.py`
- [ ] Use `argparse` for CLI: `python ask.py "question"` or `python ask.py --json "question"`
- [ ] Interactive mode when no args: loop until `exit`
- [ ] Call `pipeline.ask(question)`
- [ ] Print answer, sources, SQL in human-readable format
- [ ] With `--json`, print raw contract
- [ ] Test manually with stub pipeline

**Output**: `ask.py` CLI working with stub

---

### Task 1.13: Sample Questions Setup [Member D] ⏱️ 30 min
**Dependencies**: None  
**Owner**: Member D  
**Branch**: `feature/member-D-eval`

- [ ] Create `eval/` directory
- [ ] Copy 10 sample questions from `questions/sample_questions.json` to `eval/test_set.json`
- [ ] Add fields: `type` (docs|db|both|dont_know), `doc`, `page` for each question
- [ ] Commit `eval/test_set.json`

**Output**: `eval/test_set.json` with 10 questions

---

### Task 1.14: Day 1 Integration and Merge [ALL] ⏱️ 1 hour
**Dependencies**: All Day 1 tasks  
**Owner**: All

- [ ] Each member pushes feature branch
- [ ] Create PRs to main
- [ ] Cross-review (A reviews B, B reviews C, C reviews D, D reviews A)
- [ ] Fix any merge conflicts
- [ ] Merge all to main
- [ ] All pull latest main
- [ ] Run `python build_index.py` on one machine to verify end-to-end
- [ ] Commit `index/chunks.json` to main

**Output**: Day 1 complete, clean main branch, chunks.json committed

---

## Day 2: Tuesday, 3 November (Search & SQL)

### Task 2.1: BM25 Search [Member B] ⏱️ 1.5 hours
**Dependencies**: 1.14  
**Owner**: Member B  
**Branch**: `feature/member-B-search`

- [ ] Create `helpdesk/search.py`
- [ ] Install `rank-bm25`
- [ ] Load chunks from `index/chunks.json`
- [ ] Build BM25 index at module load time
- [ ] Implement `search_bm25(question, k) -> List[dict]`
- [ ] Return chunks with scores
- [ ] Save BM25 model to `index/bm25.pkl` in build process
- [ ] Load BM25 from pickle at runtime
- [ ] Write docstrings

**Output**: BM25 search working

---

### Task 2.2: Embedding Generation (Build Time) [Member B] ⏱️ 2 hours
**Dependencies**: 1.14  
**Owner**: Member B  
**Branch**: `feature/member-B-embeddings`

- [ ] Install `fastembed`
- [ ] In `build_index.py`, add embedding generation:
  - Load `fastembed.TextEmbedding("BAAI/bge-small-en-v1.5")`
  - For each chunk, embed `text_for_embedding`
  - Save embeddings to `index/embeddings.npy`
- [ ] Handle import failure: log warning, skip embeddings (allow BM25-only mode)
- [ ] Update manifest with embedding model name
- [ ] Test: build index with embeddings

**Output**: `index/embeddings.npy` generated

---

### Task 2.3: Dense Embedding Search [Member B] ⏱️ 1.5 hours
**Dependencies**: 2.2  
**Owner**: Member B  
**Branch**: `feature/member-B-embeddings`

- [ ] In `helpdesk/search.py`, implement `search_dense(question, k) -> List[dict]`
- [ ] Load embeddings from `index/embeddings.npy`
- [ ] Embed question using same model
- [ ] Compute cosine similarity: `np.dot(q_emb, chunk_embs.T) / (norm(q) * norms)`
- [ ] Return top-k chunks with scores
- [ ] Handle missing embeddings file: log warning, return empty list
- [ ] Write docstrings

**Output**: Dense search working

---

### Task 2.4: Reciprocal Rank Fusion [Member B] ⏱️ 1 hour
**Dependencies**: 2.1, 2.3  
**Owner**: Member B  
**Branch**: `feature/member-B-search`

- [ ] In `helpdesk/search.py`, implement `reciprocal_rank_fusion(bm25_results, dense_results, k=60)`
- [ ] For each chunk in either list, compute RRF score: `sum(1 / (k + rank))`
- [ ] Merge and sort by RRF score
- [ ] Return combined list
- [ ] Write docstrings

**Output**: RRF merge working

---

### Task 2.5: Exact Match Boosting [Member B] ⏱️ 1.5 hours
**Dependencies**: 1.8, 2.4  
**Owner**: Member B  
**Branch**: `feature/member-B-search`

- [ ] In `helpdesk/search.py`, implement `extract_exact_tokens(question)` using `entities.extract_identifiers()`
- [ ] Implement `boost_exact_matches(merged_results, question_tokens, boost=2.0)`
- [ ] For each chunk, check if `chunk.identifiers` overlaps with `question_tokens`
- [ ] If match, multiply score by `boost`
- [ ] Re-sort by boosted scores
- [ ] Write docstrings

**Output**: Exact-match boosting working

---

### Task 2.6: Main Search Function [Member B] ⏱️ 1 hour
**Dependencies**: 2.5  
**Owner**: Member B  
**Branch**: `feature/member-B-search`

- [ ] In `helpdesk/search.py`, implement `search(question, k=5) -> List[dict]`
- [ ] Call `search_bm25(question, k=20)`
- [ ] Call `search_dense(question, k=20)` (handle failure gracefully)
- [ ] Call `reciprocal_rank_fusion(bm25, dense)`
- [ ] Call `boost_exact_matches(merged, question)`
- [ ] Return top-k chunks
- [ ] Add date-awareness: if top chunks have different dates on same topic, include all
- [ ] Implement `get_neighboring_chunks(chunk_ids)` (return prev/next clauses)
- [ ] Write docstrings

**Output**: Complete hybrid search pipeline

---

### Task 2.7: Station Resolution [Member C] ⏱️ 2 hours
**Dependencies**: 1.2  
**Owner**: Member C  
**Branch**: `feature/member-C-sql`

- [ ] Create `helpdesk/stations.py`
- [ ] Load stations table from DB at module init
- [ ] Install `rapidfuzz`
- [ ] Implement `resolve_stations(question) -> Dict[str, List[str]]`
- [ ] Detect station mentions with common patterns: `r'from\s+(\w+)', r'to\s+(\w+)', r'in\s+(\w+)'`
- [ ] For each mention:
  1. Check exact code match (case-insensitive)
  2. Check exact name match (case-insensitive)
  3. Fuzzy match with `rapidfuzz.fuzz.ratio()`, threshold 85
- [ ] For multi-station cities, return all matching codes
- [ ] Write unit tests in `tests/test_station_resolution.py`
- [ ] Write docstrings

**Output**: `helpdesk/stations.py` with tests

---

### Task 2.8: SQL Schema Extraction [Member C] ⏱️ 30 min
**Dependencies**: 1.2  
**Owner**: Member C  
**Branch**: `feature/member-C-sql`

- [ ] In `build_index.py`, add schema extraction:
  - Open `rail_timetable.db`
  - Query `SELECT sql FROM sqlite_master WHERE type IN ('table', 'view')`
  - Format as readable schema
  - Save to `index/schema.txt`
- [ ] Include stops view definition
- [ ] Include overnight journey formula in comments
- [ ] Test: build index creates `schema.txt`

**Output**: `index/schema.txt` committed

---

### Task 2.9: SQL Guard [Member C] ⏱️ 1.5 hours
**Dependencies**: None (standalone)  
**Owner**: Member C  
**Branch**: `feature/member-C-sql`

- [ ] Create `helpdesk/sql_guard.py`
- [ ] Implement `guard_sql(sql: str) -> Tuple[bool, str]`
- [ ] Strip comments: `--` and `/* */`
- [ ] Check exactly one statement (split on `;`, reject if > 1)
- [ ] Check first keyword is SELECT or WITH (case-insensitive)
- [ ] Reject keywords: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, REPLACE, ATTACH, DETACH, PRAGMA, VACUUM
- [ ] Return `(True, "")` if safe, `(False, "reason")` if rejected
- [ ] Write comprehensive unit tests in `tests/test_sql_guard.py`:
  - Rejects each forbidden keyword
  - Rejects multiple statements
  - Rejects comments
  - Allows SELECT and WITH
  - Allows subqueries
- [ ] Write docstrings

**Output**: `helpdesk/sql_guard.py` with full tests

---

### Task 2.10: Safe SQL Execution [Member C] ⏱️ 2 hours
**Dependencies**: 2.9  
**Owner**: Member C  
**Branch**: `feature/member-C-sql`

- [ ] In `helpdesk/sql_guard.py`, implement `execute_safe_sql(sql, db_path) -> Tuple[List, List]`
- [ ] Open: `sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)`
- [ ] Run: `PRAGMA query_only = ON`
- [ ] Set authorizer:
  ```python
  def authorizer(action, arg1, arg2, db, trigger):
      if action in [sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION]:
          return sqlite3.SQLITE_OK
      return sqlite3.SQLITE_DENY
  conn.set_authorizer(authorizer)
  ```
- [ ] Set progress handler for timeout:
  ```python
  start = time.time()
  def check_timeout():
      if time.time() - start > config.SQL_TIMEOUT_MS / 1000:
          return 1  # Abort
      return 0
  conn.set_progress_handler(check_timeout, 100)
  ```
- [ ] Wrap query: `SELECT * FROM ({sql}) LIMIT 50` if no LIMIT exists
- [ ] Execute and return `(rows, column_names)`
- [ ] On error, raise with error message (caller can retry)
- [ ] Write docstrings

**Output**: Safe SQL executor with multiple defense layers

---

### Task 2.11: SQL Generation [Member C] ⏱️ 2 hours
**Dependencies**: 2.7, 2.8, 2.10, 1.4  
**Owner**: Member C  
**Branch**: `feature/member-C-sql`

- [ ] Create `helpdesk/sql.py`
- [ ] Implement `generate_sql(question, resolved_stations, llm_client, schema) -> str`
- [ ] Build prompt with:
  - Schema from `index/schema.txt`
  - Quirks: stops view, overnight formula, train.number is TEXT
  - Resolved station codes
  - Generic example patterns (no actual answers)
  - Instruction: "Generate one SELECT query only"
- [ ] Request JSON output: `{"sql": "SELECT ..."}`
- [ ] Call `llm_client.generate(prompt, schema={...})`
- [ ] Parse JSON, extract SQL
- [ ] Write docstrings

**Output**: SQL generation with LLM

---

### Task 2.12: SQL Pipeline [Member C] ⏱️ 1.5 hours
**Dependencies**: 2.11  
**Owner**: Member C  
**Branch**: `feature/member-C-sql`

- [ ] In `helpdesk/sql.py`, implement `answer_with_sql(question, llm_client) -> Tuple[str, str, bool]`
- [ ] Step 1: `resolved = resolve_stations(question)`
- [ ] Step 2: `sql = generate_sql(question, resolved, llm_client, schema)`
- [ ] Step 3: `safe, reason = guard_sql(sql)`; if not safe, return `(None, reason, True)` (dont_know)
- [ ] Step 4: Try `execute_safe_sql(sql, db_path)`
- [ ] On SQL error, retry once passing error message back to LLM
- [ ] Step 5: `answer = verbalize_results(rows, columns, capped)`
- [ ] Return `(sql, answer, False)`
- [ ] Implement `verbalize_results(rows, cols, capped)` to format plain text
- [ ] Implement `is_write_request(question)` for cheap keyword check
- [ ] Write docstrings

**Output**: Complete SQL pipeline

---

### Task 2.13: Evaluation Metrics Stub [Member D] ⏱️ 1.5 hours
**Dependencies**: 1.13  
**Owner**: Member D  
**Branch**: `feature/member-D-eval`

- [ ] Create `eval/evaluate.py`
- [ ] Implement stub functions:
  - `compute_retrieval_metrics(results, gold) -> dict` (Hit@1, Hit@5, MRR)
  - `compute_answer_accuracy(results, gold) -> float`
  - `compute_source_precision_recall(results, gold) -> dict`
  - `compute_dont_know_metrics(results, gold) -> dict`
- [ ] For now, return dummy values
- [ ] Load test set and results JSON
- [ ] Print metrics table
- [ ] Write docstrings

**Output**: `eval/evaluate.py` stub

---

### Task 2.14: Day 2 Integration and Merge [ALL] ⏱️ 1 hour
**Dependencies**: All Day 2 tasks  
**Owner**: All

- [ ] Each member pushes feature branch
- [ ] Create PRs to main
- [ ] Cross-review
- [ ] Run tests: `pytest tests/`
- [ ] Fix any failures
- [ ] Merge all to main
- [ ] All pull latest main
- [ ] Rebuild index: `python build_index.py`
- [ ] Test search manually: load chunks, search for "Tatkal"
- [ ] Test SQL manually: ask "trains from Delhi to Mumbai"
- [ ] Commit updated index files

**Output**: Day 2 complete, search and SQL working in isolation

---

## Day 3: Wednesday, 4 November (Answer Generation & Integration)

### Task 3.1: Document Precedence Logic [Member C] ⏱️ 1 hour
**Dependencies**: 2.6  
**Owner**: Member C  
**Branch**: `feature/member-C-answer`

- [ ] Create `helpdesk/answer.py`
- [ ] Implement `apply_precedence(chunks) -> List[dict]`
- [ ] Group chunks by topic (heuristic: similar identifiers or keywords)
- [ ] Within each group, sort by date descending
- [ ] Mark each chunk with precedence level (1 = newest, 2 = replaced, etc.)
- [ ] Return all chunks with precedence metadata
- [ ] Write docstrings

**Output**: Precedence sorting logic

---

### Task 3.2: Source Citation Builder [Member C] ⏱️ 1 hour
**Dependencies**: None (standalone)  
**Owner**: Member C  
**Branch**: `feature/member-C-answer`

- [ ] In `helpdesk/answer.py`, implement `build_sources(chunk_ids, all_chunks) -> List[dict]`
- [ ] Map chunk_ids to chunks
- [ ] Extract `{doc, page}` from chunk metadata
- [ ] Deduplicate sources (same doc + page)
- [ ] Sort by relevance (order of chunk_ids, which is by score)
- [ ] Limit to 2-4 sources
- [ ] Return list of `{"doc": str, "page": int|None}`
- [ ] Write unit tests in `tests/test_sources.py`
- [ ] Write docstrings

**Output**: `build_sources()` with tests

---

### Task 3.3: Refund Percentage Calculator [Member C] ⏱️ 1.5 hours
**Dependencies**: None (standalone)  
**Owner**: Member C  
**Branch**: `feature/member-C-answer`

- [ ] In `helpdesk/answer.py`, implement `compute_refund_percentage(hours, train_type, chunks)`
- [ ] Parse refund rules from chunks (extract time buckets and percentages)
- [ ] Match `hours` to the applicable clause
- [ ] Return `(percentage, clause_reference)`
- [ ] Handle train-specific overrides (Vande Bharat Sleeper, etc.)
- [ ] Write docstrings

**Output**: Refund calculator in Python (not LLM)

---

### Task 3.4: Answer Generation Prompt [Member C] ⏱️ 1 hour
**Dependencies**: 1.4  
**Owner**: Member C  
**Branch**: `feature/member-C-answer`

- [ ] In `helpdesk/answer.py`, create prompt template `ANSWER_PROMPT`
- [ ] Include all rules from design.md Appendix B.2:
  - Answer only from chunks
  - Quote numbers exactly
  - Later-dated document overrides older
  - Train-specific overrides general
  - "Pre revised" is history
  - PIB future statements are announced, not in force
  - Return chunk_ids_used and sufficient flag
- [ ] Use f-string or jinja2 template
- [ ] Write docstrings

**Output**: Prompt template ready

---

### Task 3.5: Answer Generation Function [Member C] ⏱️ 2 hours
**Dependencies**: 3.1, 3.2, 3.4  
**Owner**: Member C  
**Branch**: `feature/member-C-answer`

- [ ] In `helpdesk/answer.py`, implement `generate_answer(question, chunks, llm_client)`
- [ ] Call `apply_precedence(chunks)`
- [ ] Format chunks for prompt (include metadata: doc, page, date, issuer)
- [ ] Build prompt with `ANSWER_PROMPT.format(chunks=..., question=...)`
- [ ] Define JSON schema: `{"answer": str, "chunk_ids_used": list, "sufficient": bool}`
- [ ] Call `llm_client.generate(prompt, schema={...})`
- [ ] Parse JSON response
- [ ] Call `build_sources(chunk_ids_used, chunks)`
- [ ] Return `(answer_text, sources, sufficient)`
- [ ] Handle LLM errors: return `("Error generating answer", [], False)`
- [ ] Write docstrings

**Output**: Complete answer generation pipeline

---

### Task 3.6: Router - Keyword Rules [Member D] ⏱️ 1.5 hours
**Dependencies**: 1.8  
**Owner**: Member D  
**Branch**: `feature/member-D-router`

- [ ] Create `helpdesk/router.py`
- [ ] Implement `route_by_keywords(question) -> Optional[str]`
- [ ] Keyword patterns:
  - Write verbs (change, update, delete, modify, set) → "refuse"
  - Train number pattern `\d{5}` or station mentions → "db"
  - "rule", "refund", "Tatkal", "booking limit", "chart", "cancellation" → "docs"
  - "fare", "price", "seat availability", "PNR", "waitlist", "live status" → "out_of_scope"
- [ ] Return route string or None (if ambiguous)
- [ ] Write unit tests in `tests/test_router.py`
- [ ] Write docstrings

**Output**: Keyword-based routing

---

### Task 3.7: Router - LLM Classification [Member D] ⏱️ 1.5 hours
**Dependencies**: 3.6, 1.4  
**Owner**: Member D  
**Branch**: `feature/member-D-router`

- [ ] In `helpdesk/router.py`, create prompt template `ROUTE_PROMPT`
- [ ] Implement `route_by_llm(question, llm_client) -> Tuple[str, float]`
- [ ] Build prompt with categories: docs, db, both, out_of_scope, refuse
- [ ] Define JSON schema: `{"route": str, "confidence": float}`
- [ ] Call `llm_client.generate(prompt, schema={...})`
- [ ] Parse JSON, return `(route, confidence)`
- [ ] Write docstrings

**Output**: LLM-based routing

---

### Task 3.8: Router - Main Function [Member D] ⏱️ 1 hour
**Dependencies**: 3.6, 3.7  
**Owner**: Member D  
**Branch**: `feature/member-D-router`

- [ ] In `helpdesk/router.py`, implement `route_question(question, llm_client) -> str`
- [ ] Step 1: `keyword_route = route_by_keywords(question)`
- [ ] If `keyword_route` is not None, return it (fast path)
- [ ] Step 2: `llm_route, confidence = route_by_llm(question, llm_client)`
- [ ] If `confidence > 0.8`, return `llm_route`
- [ ] If `confidence < 0.5`, default to "docs" (safer)
- [ ] Else return `llm_route`
- [ ] Write docstrings

**Output**: Complete routing logic

---

### Task 3.9: Pipeline - Document Path [Member D] ⏱️ 1.5 hours
**Dependencies**: 2.6, 3.5  
**Owner**: Member D  
**Branch**: `feature/member-D-pipeline`

- [ ] In `helpdesk/pipeline.py`, implement `answer_from_docs(question, llm_client) -> dict`
- [ ] Call `search.search(question, k=5)`
- [ ] If retrieval score < threshold, return dont_know
- [ ] Call `answer.generate_answer(question, chunks, llm_client)`
- [ ] If not sufficient, return dont_know
- [ ] Return `{"answer": text, "sources": sources, "sql": None, "dont_know": False}`
- [ ] Write docstrings

**Output**: Document path working

---

### Task 3.10: Pipeline - Database Path [Member D] ⏱️ 1 hour
**Dependencies**: 2.12  
**Owner**: Member D  
**Branch**: `feature/member-D-pipeline`

- [ ] In `helpdesk/pipeline.py`, implement `answer_from_db(question, llm_client) -> dict`
- [ ] Check `is_write_request(question)`: if True, return refuse
- [ ] Call `sql.answer_with_sql(question, llm_client)`
- [ ] If dont_know, return `{"answer": reason, "sources": [], "sql": None, "dont_know": True}`
- [ ] Else return `{"answer": text, "sources": [], "sql": sql_string, "dont_know": False}`
- [ ] Write docstrings

**Output**: Database path working

---

### Task 3.11: Pipeline - Mixed Path [Member D] ⏱️ 1 hour
**Dependencies**: 3.9, 3.10  
**Owner**: Member D  
**Branch**: `feature/member-D-pipeline`

- [ ] In `helpdesk/pipeline.py`, implement `answer_from_both(question, llm_client) -> dict`
- [ ] Run `answer_from_docs(question, llm_client)` → `doc_result`
- [ ] Run `answer_from_db(question, llm_client)` → `db_result`
- [ ] If both return dont_know, return dont_know
- [ ] Merge answers: combine text, sources from docs, sql from db
- [ ] Use LLM to blend two answers into one coherent response
- [ ] Return `{"answer": merged, "sources": doc_sources, "sql": db_sql, "dont_know": False}`
- [ ] Write docstrings

**Output**: Mixed path working

---

### Task 3.12: Pipeline - Refusal Logic [Member D] ⏱️ 45 min
**Dependencies**: 3.8  
**Owner**: Member D  
**Branch**: `feature/member-D-pipeline`

- [ ] In `helpdesk/pipeline.py`, implement `refuse(question, reason) -> dict`
- [ ] Generate polite refusal based on reason:
  - "out_of_scope": "I can only answer questions about railway rules and timetables from the 2016 data. I don't have information about fares, seat availability, or live status."
  - "refuse": "I can't help with requests to modify data."
- [ ] Optionally suggest what the pack can answer
- [ ] Return `{"answer": refusal_text, "sources": [], "sql": None, "dont_know": True}`
- [ ] Write docstrings

**Output**: Polite refusal messages

---

### Task 3.13: Pipeline - Main Ask Function [Member D] ⏱️ 1 hour
**Dependencies**: 3.8, 3.9, 3.10, 3.11, 3.12  
**Owner**: Member D  
**Branch**: `feature/member-D-pipeline`

- [ ] In `helpdesk/pipeline.py`, update `ask(question) -> dict`
- [ ] Initialize LLM client
- [ ] Wrap everything in try/except
- [ ] Call `route = route_question(question, llm_client)`
- [ ] Dispatch based on route:
  - "docs" → `answer_from_docs()`
  - "db" → `answer_from_db()`
  - "both" → `answer_from_both()`
  - "refuse" or "out_of_scope" → `refuse()`
- [ ] Log route decision at DEBUG level
- [ ] On any exception, return dont_know with honest error message
- [ ] Write docstrings

**Output**: Complete `ask()` function

---

### Task 3.14: Batch Runner [Member D] ⏱️ 1 hour
**Dependencies**: 3.13  
**Owner**: Member D  
**Branch**: `feature/member-D-batch`

- [ ] Create `run_questions.py`
- [ ] Load questions JSON: `[{"id": str, "question": str}, ...]`
- [ ] For each question:
  - Wrap in try/except
  - Call `pipeline.ask(question)`
  - Append to results list: `{"id", "question", "answer", "sources", "sql", "dont_know"}`
  - Write results JSON after each question (crash-safe)
  - Print progress: `"{id}: {question[:50]}..."`
  - Sleep between questions to respect rate limits (100ms)
- [ ] Write final results JSON
- [ ] Handle missing files gracefully
- [ ] Write docstrings

**Output**: `run_questions.py` working

---

### Task 3.15: CLI Enhancement [Member D] ⏱️ 1 hour
**Dependencies**: 3.13  
**Owner**: Member D  
**Branch**: `feature/member-D-cli`

- [ ] Update `ask.py` to use real `pipeline.ask()`
- [ ] Pretty-print with `rich` (or plain ANSI):
  - Answer in normal text
  - Sources in a box: "Sources: file.pdf, page 3"
  - SQL in a code block
  - Status line: "answered from documents" | "answered from timetable" | "both" | "I don't know"
- [ ] Add `--debug` flag: show route, retrieved chunks, scores, timings
- [ ] Add `:examples` command in interactive mode: print 5 demo questions
- [ ] Handle missing .env, missing data/, missing index/ with clear messages
- [ ] Write docstrings

**Output**: Full-featured CLI

---

### Task 3.16: Expand Test Set [Member D] ⏱️ 2 hours
**Dependencies**: 1.13  
**Owner**: Member D  
**Branch**: `feature/member-D-eval`

- [ ] Expand `eval/test_set.json` from 10 to 30+ questions
- [ ] Cover:
  - Each document at least twice
  - Each scanned page at least once
  - Conflicts between 2015 and 2026 refund rules
  - Train-specific override (Vande Bharat Sleeper)
  - Exact codes: Rule 25, CC08/2025, train 12002, 11039-Slip
  - Overnight journey: Delhi to Kanyakumari
  - Multi-station city: Chennai to Bangalore
  - At least 4 dont_know cases (fares, PNR status, waitlist, live status)
  - At least 2 unsafe requests (change train time, delete station)
- [ ] Add gold answers, sources, sql, type for each
- [ ] Commit expanded test set

**Output**: `eval/test_set.json` with 30+ questions

---

### Task 3.17: Run First Full Eval [Member D] ⏱️ 1 hour
**Dependencies**: 3.14, 3.16  
**Owner**: Member D  
**Branch**: `feature/member-D-eval`

- [ ] Run: `python run_questions.py eval/test_set.json eval/results_baseline.json`
- [ ] Manually review first 10 results
- [ ] Check: answer correctness, source accuracy, dont_know flags
- [ ] Document issues in a shared doc
- [ ] Commit results JSON

**Output**: Baseline results, list of issues

---

### Task 3.18: Day 3 Integration and Merge [ALL] ⏱️ 1 hour
**Dependencies**: All Day 3 tasks  
**Owner**: All

- [ ] Each member pushes feature branch
- [ ] Create PRs to main
- [ ] Cross-review
- [ ] Run full test suite: `pytest tests/`
- [ ] Run 10-question smoke test: `python run_questions.py questions/sample_questions.json smoke_results.json`
- [ ] Compare with gold answers
- [ ] Fix critical bugs
- [ ] Merge all to main
- [ ] All pull latest main

**Output**: Day 3 complete, end-to-end pipeline working

---

## Day 4: Thursday, 5 November (Tuning & Documentation)

### Task 4.1: Implement Evaluation Metrics [Member D] ⏱️ 2 hours
**Dependencies**: 3.17  
**Owner**: Member D  
**Branch**: `feature/member-D-eval`

- [ ] In `eval/evaluate.py`, implement real metrics:
  - `compute_retrieval_metrics()`: Hit@1, Hit@5, MRR (chunk {doc, page} matches gold source)
  - `compute_answer_accuracy()`: Gemini as judge + regex key-fact match
  - `compute_source_precision_recall()`: set-based comparison
  - `compute_dont_know_metrics()`: true positive, false positive, false negative
  - `compute_sql_match()`: execute both, compare result sets
  - `compute_latency()`: mean, p50, p95, p99
- [ ] Save JSON report: `eval/report_<timestamp>.json`
- [ ] Print table of metrics
- [ ] Write docstrings

**Output**: Full evaluation suite

---

### Task 4.2: Baseline Metrics [Member D] ⏱️ 30 min
**Dependencies**: 4.1  
**Owner**: Member D  
**Branch**: `feature/member-D-eval`

- [ ] Run: `python eval/evaluate.py eval/results_baseline.json eval/test_set.json`
- [ ] Record metrics in `eval/experiments.md`:
  - Hit@5, MRR, Accuracy, Source F1, Latency
- [ ] First row: "Baseline (BM25 + Dense + RRF + Exact + OCR + Router)"

**Output**: Baseline metrics in experiments.md

---

### Task 4.3: Tune Retrieval Thresholds [Member B] ⏱️ 2 hours
**Dependencies**: 4.2  
**Owner**: Member B  
**Branch**: `feature/member-B-tuning`

- [ ] Experiment with:
  - BM25 weight vs. dense weight in RRF
  - Exact match boost factor (1.5x, 2x, 3x)
  - Retrieval k (5, 7, 10)
  - Dont_know threshold (retrieval score cutoff)
- [ ] Run eval after each change
- [ ] Record in experiments.md
- [ ] Keep best configuration
- [ ] Update `config.py` with tuned values

**Output**: Improved retrieval, updated experiments.md

---

### Task 4.4: Tune Answer Generation [Member C] ⏱️ 2 hours
**Dependencies**: 4.2  
**Owner**: Member C  
**Branch**: `feature/member-C-tuning`

- [ ] Refine answer prompt:
  - Emphasize quoting numbers exactly
  - Add examples of precedence handling
  - Clarify train-specific overrides
- [ ] Experiment with:
  - Temperature (0 vs 0.1 vs 0.2)
  - Chunk context size (neighbors vs. whole doc)
  - Sufficiency threshold
- [ ] Run eval after each change
- [ ] Record in experiments.md
- [ ] Keep best prompt and settings

**Output**: Better answer quality, updated experiments.md

---

### Task 4.5: Tune SQL Generation [Member C] ⏱️ 1.5 hours
**Dependencies**: 4.2  
**Owner**: Member C  
**Branch**: `feature/member-C-tuning`

- [ ] Refine SQL prompt:
  - Add more quirks (train number leading zeros, slip trains)
  - Include example patterns (generic, no answers)
  - Emphasize stops view for "from A to B"
- [ ] Test on tricky questions:
  - Overnight journeys
  - Multi-station cities
  - Slip trains
- [ ] Run eval after changes
- [ ] Record in experiments.md

**Output**: Improved SQL accuracy, updated experiments.md

---

### Task 4.6: Fix Top 10 Bugs [ALL] ⏱️ 3 hours
**Dependencies**: 4.2  
**Owner**: All (divide and conquer)

- [ ] Review issues from Day 3 eval
- [ ] Prioritize by impact on hidden question score
- [ ] Each member takes 2-3 bugs
- [ ] Fix, test, commit
- [ ] Re-run eval on fixed version
- [ ] Update experiments.md

**Output**: Bug fixes, improved metrics

---

### Task 4.7: Optional Enhancements [Member B] ⏱️ 2 hours (if time)
**Dependencies**: 4.3  
**Owner**: Member B  
**Branch**: `feature/member-B-optional`

- [ ] Query rewriting:
  - Expand abbreviations: "Tatkal" → "Tatkal ticket booking"
  - Expand synonyms: "waitlisted" → "RAC / wait-listed / clerkage"
  - Flag-controlled, default off
  - Test: does Hit@5 improve by +5%?
  - Keep only if yes
- [ ] Cross-encoder reranking:
  - Load a small free model
  - Rerank top 20 chunks
  - Test: does MRR improve?
  - Keep only if yes

**Output**: Optional features if they improve metrics

---

### Task 4.8: Write README [Member D] ⏱️ 2 hours
**Dependencies**: None (standalone)  
**Owner**: Member D  
**Branch**: `feature/member-D-docs`

- [ ] Create comprehensive README.md with:
  - Project title and description
  - Install instructions (venv, pip, .env, unzip data)
  - Build index: `python build_index.py`
  - Usage:
    - `python ask.py "question"`
    - `python ask.py` (interactive)
    - `python run_questions.py <in> <out>`
    - `python eval/evaluate.py <results> <test_set>`
  - Architecture diagram (Mermaid from design.md)
  - Team member table with GitHub usernames and modules
  - Eval score table (latest from experiments.md)
  - Known limitations (2016 timetable, free tier, no live data)
  - OCR note (rapidocr preferred, tesseract fallback)
  - License (MIT or similar)
- [ ] Write docstrings

**Output**: Complete README.md

---

### Task 4.9: Write Fresh Clone Test Script [Member D] ⏱️ 1 hour
**Dependencies**: 4.8  
**Owner**: Member D  
**Branch**: `feature/member-D-scripts`

- [ ] Create `scripts/fresh_clone_test.sh` (or `.ps1` for Windows)
- [ ] Script:
  - Clone repo to temp directory
  - Create venv, install requirements
  - Copy .env from caller (or prompt for key)
  - Unzip pack into data/
  - Run `python build_index.py`
  - Run `python run_questions.py questions/sample_questions.json test_results.json`
  - Check all 10 answers for key facts (simple string match)
  - Report PASS or FAIL
- [ ] Test on a second machine
- [ ] Write docstrings

**Output**: `scripts/fresh_clone_test.sh` working

---

### Task 4.10: Finalize Requirements.txt [Member D] ⏱️ 30 min
**Dependencies**: None  
**Owner**: Member D  
**Branch**: `feature/member-D-deps`

- [ ] Review all imports across codebase
- [ ] Pin exact versions: `package==X.Y.Z`
- [ ] Keep install small and CPU-only
- [ ] Test install in a fresh venv
- [ ] Commit `requirements.txt`

**Output**: Pinned requirements.txt

---

### Task 4.11: Write Unit Tests [ALL] ⏱️ 2 hours
**Dependencies**: None  
**Owner**: All (divide by module)

- [ ] Ensure these tests exist and pass:
  - `tests/test_sql_guard.py` (C)
  - `tests/test_station_resolution.py` (C)
  - `tests/test_chunking.py` (A)
  - `tests/test_sources.py` (C)
  - `tests/test_contract.py` (D)
  - `tests/test_entity_extraction.py` (C)
  - `tests/test_router.py` (D)
- [ ] Reach at least 70% coverage on core modules
- [ ] Run: `pytest tests/ -v`
- [ ] All tests pass

**Output**: Comprehensive unit tests

---

### Task 4.12: Create Demo Questions [Member D] ⏱️ 30 min
**Dependencies**: None  
**Owner**: Member D  
**Branch**: `feature/member-D-demo`

- [ ] Create 5 impressive demo questions that showcase:
  - Document retrieval with exact sources
  - SQL generation for timetable
  - Mixed query (doc + db)
  - Proper refusal (out of scope)
  - Document precedence (2026 over 2015)
- [ ] Test each, verify correct answer
- [ ] Add to README as examples
- [ ] Wire up to `:examples` in ask.py

**Output**: 5 polished demo questions

---

### Task 4.13: Final End-to-End Test [ALL] ⏱️ 1 hour
**Dependencies**: All Day 4 tasks  
**Owner**: All

- [ ] Fresh clone on a second machine
- [ ] Follow README exactly
- [ ] Run `scripts/fresh_clone_test.sh`
- [ ] Verify PASS
- [ ] Run full eval: `python eval/evaluate.py`
- [ ] Check metrics meet targets:
  - Hit@5 > 0.85
  - Accuracy > 0.80
  - Source F1 > 0.80
  - Dont_know false positive < 0.10
- [ ] If any fail, diagnose and fix
- [ ] Re-test

**Output**: All tests pass, metrics meet targets

---

### Task 4.14: Day 4 Integration and Final Merge [ALL] ⏱️ 1 hour
**Dependencies**: All Day 4 tasks  
**Owner**: All

- [ ] Each member pushes final feature branch
- [ ] Create PRs to main
- [ ] Cross-review (everyone reviews everyone)
- [ ] Run full test suite: `pytest tests/`
- [ ] Run eval: `python eval/evaluate.py`
- [ ] Merge all to main
- [ ] All pull latest main
- [ ] Tag release: `v1.0-submission`
- [ ] Final commit by 10:30 AM Friday

**Output**: Day 4 complete, repository ready for submission

---

## Day 5: Friday, 6 November (Demo Prep & Submission)

### Task 5.1: Final Verification [Member D] ⏱️ 30 min
**Owner**: Member D

- [ ] Fresh clone one more time
- [ ] Run `scripts/fresh_clone_test.sh`
- [ ] Verify PASS
- [ ] Check git log has no API keys: `git log -p | grep -i "GEMINI_API_KEY"`
- [ ] Verify .env not committed: `git log --all -- .env`
- [ ] Verify data/ not committed: `git log --all -- data/`
- [ ] Verify index/ IS committed

**Output**: Final verification checklist complete

---

### Task 5.2: Prepare Individual Demos [ALL] ⏱️ 1 hour
**Owner**: All (individual)

- [ ] Each member prepares 5-minute demo of their modules:
  - **Member A**: Ingestion, OCR, chunking (show build_index.py output table)
  - **Member B**: Hybrid search, retrieval (show --debug output with scores)
  - **Member C**: SQL generation + guard, answer generation (show examples)
  - **Member D**: Routing, CLI, batch processing (show end-to-end)
- [ ] Practice explaining design choices
- [ ] Prepare to answer: "Why did you choose X over Y?"

**Output**: Each member ready to demo

---

### Task 5.3: Create Presentation Slides [Member D] ⏱️ 1 hour
**Owner**: Member D (lead), all contribute

- [ ] 10-slide deck:
  1. Title + team
  2. Problem statement
  3. Architecture diagram
  4. Data pack overview
  5. Hybrid retrieval approach
  6. SQL safety layers
  7. Grounded answer generation
  8. Evaluation results (experiments.md table)
  9. Demo video or live demo
  10. Lessons learned + Q&A
- [ ] Keep it visual, minimal text
- [ ] Export as PDF

**Output**: Presentation deck ready

---

### Task 5.4: Record Demo Video (optional) [ALL] ⏱️ 30 min
**Owner**: All

- [ ] Screen recording of:
  - Fresh clone setup
  - Build index
  - Ask 5 demo questions
  - Show sources and SQL
  - Run batch on 10 samples
- [ ] 3-5 minutes total
- [ ] Upload to shared drive or YouTube (unlisted)

**Output**: Demo video (optional but impressive)

---

### Task 5.5: Submit Repository Link [ALL] ⏱️ 15 min (by 12:00 PM)
**Owner**: All

- [ ] Each member submits GitHub repo link to course portal
- [ ] Verify submission before 12:00 PM
- [ ] No commits after 12:00 PM

**Output**: Submission complete

---

### Task 5.6: Post-Submission Celebration [ALL] 🎉
**Owner**: All

- [ ] Team lunch or coffee
- [ ] Reflect on what went well
- [ ] Document lessons learned for next project
- [ ] Share contact info for future collaboration

**Output**: Happy team, proud of the work

---

## Milestone Checklist

### Milestone 1: Foundation Complete (End of Day 1)
- [ ] All documents ingest to chunks.json
- [ ] OCR works on scanned pages
- [ ] index/chunks.json committed
- [ ] Pipeline stub returns dont_know for everything

### Milestone 2: Search & SQL Ready (End of Day 2)
- [ ] Hybrid search (BM25 + dense + RRF + exact boost) working
- [ ] SQL generation with full safety guards working
- [ ] Unit tests pass
- [ ] Updated index files committed

### Milestone 3: End-to-End Pipeline (End of Day 3)
- [ ] Router dispatches correctly
- [ ] Document path returns answers with sources
- [ ] Database path returns answers with SQL
- [ ] Mixed path combines both
- [ ] CLI and batch runner work
- [ ] First full eval run complete
- [ ] 30+ test questions in test_set.json

### Milestone 4: Tuned & Documented (End of Day 4)
- [ ] Eval metrics meet targets (Hit@5 > 0.85, Accuracy > 0.80)
- [ ] Experiments.md has before-and-after table
- [ ] README complete with architecture diagram
- [ ] Fresh clone test passes on second machine
- [ ] All unit tests pass
- [ ] No bugs blocking submission

### Milestone 5: Submitted (Friday 12:00 PM)
- [ ] Repository frozen (no commits after 10:30 AM)
- [ ] All members submit link
- [ ] git log shows no API keys
- [ ] .env and data/ never committed
- [ ] index/ committed
- [ ] Demo prep complete

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OCR fails on Hindi pages | Medium | Low | Rank English pages higher; Hindi is bonus |
| Free tier rate limit hit | High | Medium | Rate limiter + retry + optional cache |
| One member blocked | Medium | High | Daily standups, pair programming, cross-training |
| SQL injection bypass | Low | Critical | Defense in depth: 6 layers of guards |
| LLM hallucinates sources | Medium | High | Build sources from chunk metadata only |
| Fresh clone fails | Low | Critical | Test on second machine on Day 4 |
| Deadline slip | Low | Critical | Daily milestones, freeze by Thu 10:30 PM |

---

## Communication Plan

- **Daily standup**: 9:30 AM, 10 minutes
- **Check-ins**: 2 PM, 6 PM (async on Slack)
- **Merge windows**: End of each day
- **Pair programming**: When blocked > 30 minutes, ask for pair
- **Decision log**: Shared doc for design choices (why fastembed, why RRF k=60, etc.)

---

## Definition of Done (Per Task)

- [ ] Code written with type hints and docstrings
- [ ] Manual testing complete
- [ ] Unit tests written (if applicable)
- [ ] Pushed to feature branch
- [ ] PR created and reviewed
- [ ] CI tests pass (pytest)
- [ ] Merged to main
- [ ] Updated documentation (if applicable)

---

**End of Tasks**
