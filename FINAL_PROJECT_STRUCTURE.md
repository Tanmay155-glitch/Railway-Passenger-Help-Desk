# 📁 Final Project Structure

## Core Files (Required by Assignment)

```
rail_capstone_pack/
├── README.md                          ✅ Installation & usage guide
├── requirements.txt                   ✅ All dependencies with versions
├── .env.example                       ✅ API key template
├── .gitignore                         ✅ Excludes .env, .venv/, data/
│
├── helpdesk/                          ✅ Core modules
│   ├── __init__.py
│   ├── config.py                      ✅ Configuration
│   ├── llm.py                         ✅ Gemini client with retry
│   ├── doc_meta.py                    ✅ Document metadata
│   ├── entities.py                    ✅ Entity extraction
│   ├── ingest.py                      ✅ Pack to chunks
│   ├── search.py                      ✅ search(question, k)
│   ├── sql_guard.py                   ✅ SQL safety
│   ├── stations.py                    ✅ Station resolution
│   ├── sql.py                         ✅ Read-only text-to-SQL
│   ├── answer.py                      ✅ Grounded answers
│   ├── router.py                      ✅ Intent routing
│   └── pipeline.py                    ✅ ask(question)
│
├── build_index.py                     ✅ python build_index.py
├── index/                             ✅ Built index (committed)
│   ├── bm25.pkl
│   ├── chunks.json
│   ├── manifest.json
│   └── schema.txt
│
├── ask.py                             ✅ python ask.py "question"
├── run_questions.py                   ✅ Batch processor
│
├── eval/                              ✅ Evaluation
│   ├── test_set.json                  ✅ 36 test questions
│   ├── evaluate.py                    ✅ Metrics computation
│   └── experiments.md                 ✅ Tracking table
│
└── tests/                             ✅ Unit tests (63 tests)
    ├── test_contract.py
    ├── test_entity_extraction.py
    ├── test_chunking.py
    ├── test_sources.py
    ├── test_sql_guard.py
    └── test_station_resolution.py
```

## Additional Files

### Web UI (Optional - Not Required by Assignment)
```
├── app.py                             🌐 Flask web application
├── templates/
│   └── index.html                     🌐 Web interface
└── WEB_UI_GUIDE.md                    🌐 Web UI documentation
```

### Documentation
```
├── SOURCES.md                         📚 Data pack source info
├── requirements.md                    📚 Detailed specifications
├── design.md                          📚 Architecture & design
├── tasks.md                           📚 Task breakdown
├── COMPLETE_TEST_REPORT.md            📊 Test results
└── COMPLIANCE_REPORT.md               📊 Compliance verification
```

### Data Directories (Not Committed)
```
├── data/                              🚫 Gitignored (unzip pack here)
│   ├── database/
│   │   └── rail_timetable.db
│   └── documents/
│       ├── irctc_refund_rules_jan2026.pdf
│       └── ... (7 documents)
│
├── database/                          🚫 Duplicate (can remove)
├── documents/                         🚫 Duplicate (can remove)
└── questions/                         🚫 Duplicate (can remove)
```

---

## Files for Submission

### Essential (15 files/directories):
1. ✅ README.md
2. ✅ requirements.txt
3. ✅ .env.example
4. ✅ .gitignore
5. ✅ helpdesk/ (12 modules)
6. ✅ build_index.py
7. ✅ index/
8. ✅ ask.py
9. ✅ run_questions.py
10. ✅ eval/
11. ✅ tests/

### Optional but Recommended:
12. ✅ SOURCES.md (data pack info)
13. ✅ requirements.md (specifications)
14. ✅ design.md (architecture)
15. ✅ COMPLETE_TEST_REPORT.md (test results)
16. ✅ COMPLIANCE_REPORT.md (verification)

### Web UI (Bonus):
17. 🌐 app.py
18. 🌐 templates/
19. 🌐 WEB_UI_GUIDE.md

---

## Clean vs Dirty State

### ✅ CLEAN (Current)
- Only essential files
- No temporary/status files
- No duplicate data directories
- Clear structure

### ❌ DIRTY (Before Cleanup)
- 20+ status/tracking files
- Multiple test scripts
- Temporary API test files
- Cluttered root directory

---

## Git Commands for Final Cleanup

```bash
# Stage all changes
git add -A

# Commit
git commit -m "Final cleanup: Remove temporary files, add web UI"

# Review what's tracked
git ls-files

# Push to remote
git push origin main
```

---

## Files to Keep

### Must Have:
- All helpdesk/ modules
- ask.py, run_questions.py, build_index.py
- index/ directory
- eval/ directory  
- tests/ directory
- README.md, requirements.txt, .env.example, .gitignore

### Nice to Have:
- SOURCES.md (explains data pack)
- requirements.md, design.md, tasks.md (documentation)
- COMPLETE_TEST_REPORT.md, COMPLIANCE_REPORT.md (verification)
- app.py, templates/ (web UI)

### Can Remove:
- Old database/, documents/, questions/ (duplicates of data/)
- Any *.md files starting with STATUS, PROGRESS, etc.
- Test scripts (test_*.py in root)

---

## Verification

Run this to verify structure:
```bash
# Check required files exist
ls helpdesk/*.py ask.py run_questions.py build_index.py

# Check index committed
ls index/

# Check tests exist
ls tests/test_*.py

# Check eval exists
ls eval/test_set.json eval/evaluate.py
```

All should exist without errors.

---

**Last Updated:** November 4, 2026  
**Status:** Clean and Ready for Submission ✅
