# Experiments Log

## Goal
Track system improvements through controlled experiments. Keep changes only if metrics improve.

---

## Experiment Tracking Table

| ID | Change | Date | Answer Acc | Source Acc | DK Acc | Hit@5 | MRR | Notes |
|----|--------|------|------------|------------|--------|-------|-----|-------|
| E00 | Baseline (before testing) | 2026-11-02 | - | - | - | - | - | Initial code complete, not tested |
| E01 | First integration test | 2026-11-03 | TBD | TBD | TBD | TBD | TBD | Run after build_index.py |
| E02 | Bug fixes from testing | 2026-11-03 | TBD | TBD | TBD | TBD | TBD | After fixing crashes |
| E03 | + Dense embeddings | 2026-11-03 | TBD | TBD | TBD | TBD | TBD | If baseline was BM25 only |
| E04 | + RRF merging | 2026-11-03 | TBD | TBD | TBD | TBD | TBD | Combine BM25 + dense |
| E05 | + Exact match boost | 2026-11-03 | TBD | TBD | TBD | TBD | TBD | Boost Rule/train/circular codes |
| E06 | + Improved prompts | 2026-11-04 | TBD | TBD | TBD | TBD | TBD | Tune answer generation |
| E07 | + Router tuning | 2026-11-04 | TBD | TBD | TBD | TBD | TBD | Reduce false refusals |
| E08 | + SQL prompt improvements | 2026-11-04 | TBD | TBD | TBD | TBD | TBD | Better query generation |
| E09 | + Retrieval k tuning | 2026-11-04 | TBD | TBD | TBD | TBD | TBD | Optimize top-k values |
| E10 | Final optimizations | 2026-11-05 | TBD | TBD | TBD | TBD | TBD | Pre-submission polish |

---

## Metric Definitions

- **Answer Acc**: Percentage of correct answers (0-100%)
- **Source Acc**: Percentage of correct source citations (0-100%)
- **DK Acc**: Correct "don't know" responses (0-100%)
- **Hit@5**: Retrieved chunk contains answer in top 5 (0-1.0)
- **MRR**: Mean Reciprocal Rank of first relevant chunk (0-1.0)

---

## Target Metrics

### Minimum Acceptable (Pass)
- Answer Accuracy: > 70%
- Source Accuracy: > 70%
- Don't Know Accuracy: > 80%

### Target (Good Score)
- Answer Accuracy: > 85%
- Source Accuracy: > 85%
- Don't Know Accuracy: > 90%

### Stretch (Excellent)
- Answer Accuracy: > 95%
- Source Accuracy: > 95%
- Don't Know Accuracy: > 95%

---

## Experiment Protocol

### For Each Change:

1. **Make ONE change** (don't bundle multiple improvements)
2. **Run evaluation**: `python eval/evaluate.py results.json eval/test_set.json`
3. **Record metrics** in table above
4. **Keep change** if metrics improve OR stay same with lower cost/latency
5. **Revert change** if metrics drop
6. **Commit** if keeping: `git commit -m "E0X: description - improved Y by Z%"`

### What to Tune:

**Retrieval:**
- BM25 k value (how many results)
- Dense k value
- RRF constant (default 60)
- Exact match boost factor (default 2.0)
- Chunk size (150-400 words)

**Prompts:**
- Answer generation system prompt
- SQL generation examples
- Router classification instructions
- Temperature (0 vs 0.1 vs 0.3)

**Router:**
- Keyword patterns
- Confidence thresholds
- Route priority order

**SQL:**
- Schema description clarity
- Example query patterns
- Error retry strategy

---

## Detailed Experiment Notes

### E00: Baseline
**Status**: Code complete, not tested yet  
**What**: All 12 modules implemented, 3 test files passing  
**Expected**: System should work but may have bugs  
**Next**: Run integration test

---

### E01: First Integration Test
**Status**: Pending  
**What**: Build index + run test set  
**Commands**:
```bash
python build_index.py
python run_questions.py eval/test_set.json results_e01.json
python eval/evaluate.py results_e01.json eval/test_set.json
```
**Expected Issues**:
- Import errors
- Missing dependencies
- Path issues
- API rate limits
- OCR failures

**Next**: Fix critical bugs

---

### E02: Bug Fixes
**Status**: Pending  
**What**: Fix whatever broke in E01  
**Focus**:
- System crashes
- Import errors
- Missing index files
- API connection issues
**Goal**: All 36 questions run without crashes

---

### E03: Dense Embeddings
**Status**: Pending  
**What**: Ensure fastembed is working  
**Check**: `index/embeddings.npy` exists  
**Hypothesis**: Dense + BM25 better than BM25 alone  
**If fails**: Fall back to BM25 only

---

### E04: RRF Merging
**Status**: Pending  
**What**: Combine BM25 + dense with RRF  
**Baseline**: BM25 alone or dense alone  
**Hypothesis**: Fusion improves Hit@5 and MRR  
**Tune**: RRF k constant (try 40, 60, 80)

---

### E05: Exact Match Boost
**Status**: Pending  
**What**: Boost chunks with exact code matches  
**Examples**: "Rule 25", "train 12002", "CC08/2025"  
**Hypothesis**: Improves exact-code questions (C01, C02)  
**Tune**: Boost factor (try 1.5, 2.0, 3.0)

---

### E06: Prompt Improvements
**Status**: Pending  
**What**: Tune answer generation prompt  
**Focus**:
- Clearer precedence rules
- Better citation instructions
- Arithmetic in Python emphasis
**Hypothesis**: Reduces hallucinations, improves accuracy

---

### E07: Router Tuning
**Status**: Pending  
**What**: Reduce false "don't know" responses  
**Check**: D01-D06 should refuse, others shouldn't  
**Hypothesis**: Better routing improves DK accuracy  
**Tune**: Confidence thresholds, keyword patterns

---

### E08: SQL Improvements
**Status**: Pending  
**What**: Better SQL generation prompts  
**Focus**:
- Clearer schema descriptions
- Better overnight journey examples
- Station resolution examples
**Hypothesis**: More queries execute successfully

---

### E09: Retrieval K Tuning
**Status**: Pending  
**What**: Optimize top-k values  
**Current**: BM25 k=20, dense k=20, final k=5  
**Try**: Various combinations  
**Trade-off**: Higher k = more context but slower

---

### E10: Final Polish
**Status**: Pending  
**What**: Last-minute fixes before submission  
**Focus**:
- Edge cases found in testing
- Performance optimization
- Error message clarity

---

## Commands Reference

### Run Single Experiment
```bash
# Make your change
python build_index.py  # if needed
python run_questions.py eval/test_set.json results_eXX.json
python eval/evaluate.py results_eXX.json eval/test_set.json
```

### Compare Two Experiments
```bash
python eval/evaluate.py results_e05.json eval/test_set.json > e05_metrics.txt
python eval/evaluate.py results_e06.json eval/test_set.json > e06_metrics.txt
diff e05_metrics.txt e06_metrics.txt
```

### Quick Test (3 questions)
```bash
python ask.py "What is the Tatkal cancellation charge?"
python ask.py "Which trains run from Delhi to Mumbai?"
python ask.py "What is my PNR status?"  # Should refuse
```

---

## Observations & Insights

### What Worked:
- TBD after testing

### What Didn't Work:
- TBD after testing

### Surprising Findings:
- TBD after testing

### Known Limitations:
- 2016 timetable data (outdated)
- Free-tier Gemini rate limits
- OCR quality on poor scans
- No fare/availability data

---

## Final Results

**Best Configuration**: TBD  
**Final Score**: TBD / 100  
**Submission Time**: TBD

---

**Last Updated**: November 3, 2026  
**Status**: Awaiting first test run
