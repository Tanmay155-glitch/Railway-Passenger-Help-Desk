# Capstone Evaluation Checklist

## 📋 Official Requirements Compliance

### Deadline: Friday, 6 November 2026, 12:00 PM

---

## ✅ Repository Structure (10 points)

### Required Files
- [x] `README.md` - Installation, usage, diagram, team, scores
- [x] `requirements.txt` - All libraries with versions (pinned)
- [x] `.env.example` - Template with `GEMINI_API_KEY=`
- [x] `.gitignore` - Includes `.env`, `.venv/`, `data/`
- [x] `helpdesk/ingest.py` - Pack to chunks
- [ ] `helpdesk/search.py` - search(question, k) **[Day 2]**
- [x] `helpdesk/llm.py` - Gemini client with retry
- [ ] `helpdesk/answer.py` - Grounded answers with sources **[Day 3]**
- [ ] `helpdesk/sql.py` - Read-only text-to-SQL **[Day 2]**
- [x] `helpdesk/pipeline.py` - ask(question) **[Stub - complete Day 3]**
- [x] `build_index.py` - One-time index builder
- [ ] `index/` - Built index (to be committed) **[Day 2]**
- [x] `ask.py` - CLI interface
- [ ] `run_questions.py` - Batch processor **[Day 3]**
- [ ] `eval/` - test_set.json, evaluate.py, experiments.md **[Days 3-4]**

### Security Checks
- [x] `.env` in `.gitignore`
- [x] `.env.example` has no real keys
- [ ] Run: `git log -p | grep -i "GEMINI_API_KEY"` → No keys in history
- [x] No hard-coded answers in code or prompts
- [x] No document content typed into code

---

## 🎯 Hidden Questions Score (50 points)

### Answer Correctness (30 points)
- [ ] All 10 sample questions return correct answers
- [ ] Handles scanned PDFs with OCR
- [ ] Handles HTML documents correctly
- [ ] Respects document precedence (newer over older)
- [ ] Train-specific rules override general rules
- [ ] Exact codes work (Rule 25, train numbers, circulars)
- [ ] Arithmetic computed in Python, not LLM
- [ ] Numbers quoted exactly from documents

### Source Accuracy (10 points)
- [ ] Sources cite correct document names
- [ ] Page numbers are correct (1-indexed)
- [ ] HTML docs use `page: null`
- [ ] Only 2-4 most relevant sources returned
- [ ] Sources ordered by relevance
- [ ] No hallucinated sources

### "Don't Know" Handling (10 points)
- [ ] Refuses fare questions
- [ ] Refuses seat availability questions
- [ ] Refuses PNR status questions
- [ ] Refuses live running status
- [ ] Refuses waitlist confirmation predictions
- [ ] Refuses data modification requests
- [ ] Refuses questions not in pack
- [ ] False refusal rate < 10%

---

## 🎤 Live Demo (20 points)

### Demo Preparation
- [ ] System runs from terminal
- [ ] Demo questions prepared (5-6 impressive examples)
- [ ] Shows document retrieval with sources
- [ ] Shows SQL generation for timetable
- [ ] Shows proper refusal ("I don't know")
- [ ] Shows different question types:
  - [ ] Document-only question
  - [ ] Database-only question
  - [ ] Mixed question (doc + db)
  - [ ] Out-of-scope refusal
  - [ ] Exact code match (Rule 25, train number)
- [ ] Response time < 10 seconds per question
- [ ] Handles panel questions sensibly

### Technical Readiness
- [ ] Fresh clone tested on second machine
- [ ] `python run_questions.py` works
- [ ] No crashes or errors during demo
- [ ] Clear error messages if something fails
- [ ] Backup plan if network/API fails

---

## 📊 Presentation (20 points)

### Content Requirements
- [ ] Clear explanation of system architecture
- [ ] Explain how accuracy was improved
- [ ] Show before-and-after metrics (experiments.md)
- [ ] Diagram showing data flow
- [ ] Every member explains their module:
  - [ ] Member A: Ingestion, OCR, chunking
  - [ ] Member B: Search, retrieval, embeddings
  - [ ] Member C: SQL, answer generation
  - [ ] Member D: Pipeline, routing, eval
- [ ] Design decisions and trade-offs explained
- [ ] Challenges faced and solutions

### Time Management
- [ ] 10 minutes total (strict)
- [ ] ~5 minutes presentation
- [ ] ~5 minutes Q&A
- [ ] Each member speaks
- [ ] Slides optional but recommended

---

## 🔒 Security & Rules Compliance

### API Key Safety
- [x] Keys stored in `.env` only
- [x] `.env` in `.gitignore`
- [ ] Check: `git log --all -- .env` → Empty
- [ ] Check: `git log -p | grep -i "key"` → No keys visible
- [x] No keys in logs/console
- [x] No keys in code or prompts

### Data Source Rules
- [x] No web search
- [x] No hard-coded answers in prompts
- [x] No document content manually typed
- [x] Only metadata in doc_meta.py (no answers)
- [ ] All answers traceable to chunks or SQL results

### Git Practices
- [ ] Every team member has commits
- [ ] Commits from own GitHub accounts
- [ ] Commit messages clear and descriptive
- [ ] No large files committed (except database ~28MB)
- [ ] `data/` never committed

---

## 🧪 Testing Requirements

### Unit Tests
- [x] `tests/test_contract.py` - Output contract
- [x] `tests/test_entity_extraction.py` - Entity extraction
- [ ] `tests/test_sql_guard.py` - SQL safety **[Day 2]**
- [ ] `tests/test_station_resolution.py` - Station matching **[Day 2]**
- [ ] `tests/test_chunking.py` - Chunk integrity **[Day 2]**
- [ ] `tests/test_sources.py` - Source citation **[Day 3]**
- [ ] All tests pass: `pytest tests/ -v`

### Test Set (eval/test_set.json)
- [ ] At least 20 questions (ideally 30-40)
- [ ] Includes all 10 sample questions
- [ ] Covers every document
- [ ] Covers every scanned page
- [ ] Includes conflict cases (2015 vs 2026 rules)
- [ ] Includes train-specific overrides
- [ ] Includes exact code questions
- [ ] Includes overnight journeys
- [ ] Includes multi-station cities
- [ ] At least 4 "don't know" cases
- [ ] At least 2 unsafe requests

### Evaluation Metrics
- [ ] `eval/evaluate.py` implemented
- [ ] Reports Hit@1, Hit@5, MRR
- [ ] Reports answer accuracy
- [ ] Reports source precision/recall
- [ ] Reports don't_know correctness
- [ ] Reports SQL execution match
- [ ] Reports latency (mean, p50, p95, p99)
- [ ] Saves JSON report per run

### Experiments Table (eval/experiments.md)
- [ ] Before-and-after table
- [ ] One row per change
- [ ] Metrics for each row
- [ ] Shows progression:
  - [ ] Baseline
  - [ ] +Dense embeddings
  - [ ] +RRF
  - [ ] +Exact boost
  - [ ] +OCR
  - [ ] +Router
  - [ ] +Prompt improvements
- [ ] Changes kept only if metrics improved

---

## 📦 Fresh Clone Test

### Pre-Submission Checklist
- [ ] Clone to clean directory
- [ ] Unzip rail_capstone_pack.zip into `data/`
- [ ] Create `.env` with GEMINI_API_KEY
- [ ] Create venv: `python -m venv .venv`
- [ ] Activate: `.venv\Scripts\activate`
- [ ] Install: `pip install -r requirements.txt`
- [ ] Build: `python build_index.py` → Success
- [ ] Test: `python ask.py "test question"` → Works
- [ ] Batch: `python run_questions.py questions/sample_questions.json results.json` → Success
- [ ] Compare results with model answers → Match
- [ ] Check runtime: < 3 seconds startup, < 10 seconds per answer
- [ ] Check `index/` committed in repo

---

## 🎯 Target Metrics (for 50-point hidden questions)

### Minimum Acceptable
- Answer correctness: > 70% (21/30 points)
- Source accuracy: > 70% (7/10 points)
- Don't know correctness: > 80% (8/10 points)
- **Total**: > 36/50 points

### Target Goals
- Answer correctness: > 90% (27/30 points)
- Source accuracy: > 90% (9/10 points)
- Don't know correctness: > 90% (9/10 points)
- **Total**: > 45/50 points

### Stretch Goals
- Answer correctness: 100% (30/30 points)
- Source accuracy: 100% (10/10 points)
- Don't know correctness: 100% (10/10 points)
- **Total**: 50/50 points

---

## 📅 Daily Goals

### Day 1 (Monday) - ✅ COMPLETED
- [x] Project scaffolding
- [x] Config, LLM client, doc_meta, entities
- [x] PDF/HTML ingestion with OCR
- [x] Chunking
- [x] build_index.py
- [x] CLI stub
- [x] Basic tests

### Day 2 (Tuesday)
- [ ] BM25 + dense embeddings + RRF
- [ ] Exact-match boosting
- [ ] Station resolution
- [ ] SQL generation + guards
- [ ] Safe SQL execution
- [ ] Update build_index.py (embeddings, BM25)
- [ ] SQL tests

### Day 3 (Wednesday)
- [ ] Answer generation with precedence
- [ ] Router (keyword + LLM)
- [ ] Complete pipeline
- [ ] run_questions.py
- [ ] Expand test set to 30+
- [ ] First full eval
- [ ] Answer tests

### Day 4 (Thursday)
- [ ] Implement evaluate.py
- [ ] Tuning loop (retrieval, prompts, SQL)
- [ ] experiments.md table
- [ ] Bug fixes
- [ ] README completion
- [ ] Fresh clone test
- [ ] Demo prep

### Day 5 (Friday Morning)
- [ ] Final verification
- [ ] Practice demo
- [ ] Prepare presentation
- [ ] Each member practices their part
- [ ] Submit by 12:00 PM
- [ ] No commits after deadline!

---

## ⚠️ Red Flags to Avoid

### Automatic Failure Scenarios
- ❌ API key in git history
- ❌ Hard-coded answers
- ❌ Cannot run from fresh clone
- ❌ Crashes during demo
- ❌ Team member can't explain their code

### Major Point Deductions
- ⚠️ Missing required files
- ⚠️ Tests don't pass
- ⚠️ No test set or experiments.md
- ⚠️ No individual commits from members
- ⚠️ Poor accuracy on hidden questions
- ⚠️ Slow performance (>10s per question)

---

## ✅ Final Pre-Submission Checklist

### Thursday Night (Before Freeze)
- [ ] All code complete and tested
- [ ] All team members have commits
- [ ] Fresh clone test passes
- [ ] 10 sample questions all correct
- [ ] README complete and accurate
- [ ] No sensitive data in repo
- [ ] experiments.md shows improvements
- [ ] Demo questions selected
- [ ] Presentation slides ready

### Friday Morning (Before 12:00 PM)
- [ ] Final commit by 10:30 AM
- [ ] Tag release: `git tag v1.0-submission`
- [ ] Push tags: `git push --tags`
- [ ] Every team member submits repo link to LMS
- [ ] Verify submission received
- [ ] **NO COMMITS AFTER 12:00 PM**

### Friday Evening (Demo at 7-9 PM)
- [ ] Laptop charged and ready
- [ ] Internet connection tested
- [ ] Fresh clone on demo machine
- [ ] API key ready
- [ ] Demo questions tested
- [ ] Backup plan prepared
- [ ] Team present and ready

---

## 📊 Current Status

**Overall Progress**: 25% (Day 1 complete)

**Points Secured**: ~2/100
- Repository structure: 2/10 (basic structure in place)

**Points In Progress**: 0/100

**Points At Risk**: 98/100
- Everything else needs completion

**Days Remaining**: 4 days

**Critical Path**: Day 2 (search + SQL) → Day 3 (answer + pipeline) → Day 4 (tuning)

---

## 🎯 Focus Areas for Maximum Points

### High Impact, High Effort (Must Complete)
1. **Accurate answers** (30 points) - Core pipeline, precedence, arithmetic
2. **Source accuracy** (10 points) - Correct page numbers, no hallucination
3. **Search quality** (enables #1) - Hybrid retrieval, exact matching
4. **SQL safety** (enables #1) - Guards, read-only, entity resolution

### High Impact, Medium Effort
5. **Don't know handling** (10 points) - Router, refusal logic
6. **Working demo** (20 points) - Reliability, clear examples

### Medium Impact, Must Have
7. **Presentation** (20 points) - Practice, slides, clear explanations
8. **Test set & metrics** (part of 10) - Drive improvements

---

**Last Updated**: Day 1 (Monday, 2 November 2026)
**Next Review**: End of Day 2
