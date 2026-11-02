# Experiments and Tuning Log

## Evaluation Metrics Tracking

| Experiment | Answer Acc | Source Acc | Don't Know Acc | Latency | Notes |
|------------|------------|------------|----------------|---------|-------|
| Baseline (Initial) | TBD | TBD | TBD | TBD | After first full run |
| + Tuned Prompts | TBD | TBD | TBD | TBD | Improved prompt clarity |
| + Better Routing | TBD | TBD | TBD | TBD | Enhanced keyword detection |
| Final | TBD | TBD | TBD | TBD | Ready for submission |

## Testing Log

### Date: Monday, 2 November 2026

**Status**: Initial implementation complete (80%)

**Components Implemented**:
- ✅ Search module (BM25 + embeddings + RRF)
- ✅ SQL modules (guards + generation + stations)
- ✅ Answer generation
- ✅ Router
- ✅ Pipeline
- ✅ Batch processor
- ✅ Build script

**Testing Status**:
- Unit tests: 3 files, 40+ test cases
- Integration tests: Created test_system.py
- Evaluation suite: test_set.json (21 questions), evaluate.py

**Next Steps**:
1. Run test_system.py to verify all modules load
2. Create .env with API key
3. Run build_index.py
4. Test with sample questions
5. Run full evaluation
6. Fix any bugs
7. Tune and optimize

---

## Design Decisions

### Hybrid Search
**Decision**: Use BM25 + dense embeddings with RRF  
**Rationale**: Combines keyword matching (good for exact codes) with semantic search  
**Alternative Considered**: BM25 only - rejected as insufficient for semantic queries

### SQL Safety
**Decision**: 6 layers of protection  
**Rationale**: Defense in depth for security  
**Layers**:
1. Keyword blacklist
2. Statement validation
3. Read-only mode
4. Authorizer callback
5. Timeout handler
6. Row limit

### Document Precedence
**Decision**: Sort by date, newer wins  
**Rationale**: Railway rules change over time, latest is authoritative  
**Implementation**: Compare dates in ISO format, mark precedence in chunks

### Router
**Decision**: Keyword rules first, then LLM  
**Rationale**: Fast path for clear cases, LLM for ambiguous  
**Threshold**: Confidence > 0.5 to trust LLM classification

---

## Known Issues

### To Fix:
- [ ] Test on real data
- [ ] Verify all imports work
- [ ] Check database path resolution
- [ ] Test OCR functionality
- [ ] Verify embedding generation
- [ ] Test end-to-end pipeline

### To Improve:
- [ ] Tune retrieval thresholds
- [ ] Improve prompts for accuracy
- [ ] Optimize latency
- [ ] Add more test cases

---

## Performance Targets

| Metric | Target | Stretch |
|--------|--------|---------|
| Answer Accuracy | > 70% | > 90% |
| Source Accuracy | > 70% | > 90% |
| Don't Know Accuracy | > 80% | > 95% |
| Latency per Question | < 10s | < 5s |
| Hidden Question Score | > 36/50 | > 45/50 |

---

## Changelog

### 2026-11-02 (Day 1)
- Initial implementation of all core modules
- 80% code complete
- Basic testing infrastructure in place
- Ready for integration testing
