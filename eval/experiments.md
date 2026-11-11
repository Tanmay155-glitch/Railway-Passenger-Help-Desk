# Experiment Tracking

This file tracks all experiments and their impact on evaluation metrics.

## Evaluation Metrics

- **Hit@5**: Percentage of questions where correct document appears in top 5 chunks
- **MRR**: Mean Reciprocal Rank of first correct chunk
- **Accuracy**: Percentage of answers judged as correct
- **Source F1**: F1 score for source citation accuracy
- **Latency**: Average response time per question (seconds)

## Experiments

| Experiment | Hit@5 | MRR | Accuracy | Source F1 | Latency | Notes |
|------------|-------|-----|----------|-----------|---------|-------|
| Baseline (Not Run) | - | - | - | - | - | Initial system before optimization |
| Current System | TBD | TBD | TBD | TBD | TBD | Run evaluation to get baseline |

## Instructions

To run evaluation:
```bash
# Process test questions
python run_questions.py eval/test_set.json eval/results.json

# Compute metrics
python eval/evaluate.py eval/results.json eval/test_set.json
```

## Change Log

### [Current] - 2026-11-06
- Initial experiment tracking file created
- System has: Hybrid search (BM25 + Dense + RRF), exact-match boosting, SQL guard, router
- Ready for baseline evaluation

### Future Experiments to Try

1. **+Reranking**: Add cross-encoder reranking after RRF
   - Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
   - Expected: Higher MRR, slower latency

2. **+Better Embeddings**: Switch from `bge-small` to `bge-base` or `bge-large`
   - Expected: Higher Hit@5, slower latency

3. **+Query Expansion**: Expand query with synonyms before search
   - Expected: Higher recall, possible lower precision

4. **+Prompt Engineering**: Refine answer generation prompt
   - Expected: Higher accuracy, same latency

5. **+SQL Prompt Tuning**: Add more examples to SQL generation
   - Expected: Higher SQL correctness

6. **+Multi-turn Context**: Keep conversation history
   - Expected: Better follow-up questions

## Baseline Results (To Be Filled)

After running evaluation, fill in:

```
Total Questions: __
Answered: __ (__ %)
Don't Know: __ (__ %)

Answer Correctness: __ / __ (__ %)
Source Accuracy: __ / __ (__ %)
SQL Correctness: __ / __ (__ %)

Source Precision: __
Source Recall: __

False Refusals: __ (__ %)
False Answers: __ (__ %)

Estimated Score: __ / 50
```

## Keep Only Changes That Improve Metrics

Rule: A change is kept if it improves at least one primary metric (Hit@5, Accuracy, Source F1) without significantly degrading others. Latency increases up to 50% are acceptable if accuracy improves by >5%.
