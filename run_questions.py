"""
Batch question processor for Railway Passenger Help Desk.
Processes multiple questions from JSON file and saves results.
"""

import json
import sys
import time
import logging
from pathlib import Path

from helpdesk.pipeline import ask
from helpdesk.config import validate_environment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_questions(input_file: Path) -> list:
    """
    Load questions from JSON file.
    
    Args:
        input_file: Path to input JSON
        
    Returns:
        List of question dictionaries
    """
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        logger.info(f"Loaded {len(questions)} questions from {input_file}")
        return questions
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {input_file}: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading {input_file}: {e}")
        sys.exit(1)


def save_results(output_file: Path, results: list):
    """
    Save results to JSON file.
    
    Args:
        output_file: Path to output JSON
        results: List of result dictionaries
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved {len(results)} results to {output_file}")
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")


def main():
    """Main batch processing function."""
    if len(sys.argv) != 3:
        print("Usage: python run_questions.py <input_questions.json> <output_results.json>")
        print()
        print("Example:")
        print("  python run_questions.py questions/sample_questions.json results.json")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    # Validate environment
    is_valid, errors = validate_environment()
    if not is_valid:
        logger.error("Environment validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    logger.info("Environment validated successfully")
    
    # Load questions
    questions = load_questions(input_file)
    
    # Process each question
    results = []
    start_time = time.time()
    
    for i, q_item in enumerate(questions, 1):
        q_id = q_item.get('id', f'Q{i:02d}')
        question = q_item.get('question', '')
        
        if not question:
            logger.warning(f"Skipping empty question: {q_id}")
            continue
        
        logger.info(f"[{i}/{len(questions)}] Processing {q_id}: {question[:60]}...")
        
        try:
            # Ask the question
            q_start = time.time()
            result = ask(question)
            q_duration = time.time() - q_start
            
            # Build result object
            result_obj = {
                "id": q_id,
                "question": question,
                "answer": result["answer"],
                "sources": result["sources"],
                "sql": result["sql"],
                "dont_know": result["dont_know"]
            }
            
            results.append(result_obj)
            
            # Log status
            status = "✗ don't know" if result["dont_know"] else "✓ answered"
            logger.info(f"  {status} ({q_duration:.2f}s)")
            
            # Save incrementally (crash-safe)
            save_results(output_file, results)
            
            # Rate limiting (small delay to respect API limits)
            time.sleep(0.2)
            
        except KeyboardInterrupt:
            logger.warning("Interrupted by user")
            save_results(output_file, results)
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error processing {q_id}: {e}", exc_info=True)
            
            # Add error result
            result_obj = {
                "id": q_id,
                "question": question,
                "answer": f"Error: {str(e)}",
                "sources": [],
                "sql": None,
                "dont_know": True
            }
            results.append(result_obj)
            
            # Save even on error
            save_results(output_file, results)
            
            # Continue with next question
            continue
    
    # Final save
    save_results(output_file, results)
    
    # Summary
    total_time = time.time() - start_time
    answered = sum(1 for r in results if not r["dont_know"])
    dont_know = len(results) - answered
    
    logger.info("")
    logger.info("="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    logger.info(f"Total questions: {len(results)}")
    logger.info(f"Answered: {answered} ({100*answered/len(results):.1f}%)")
    logger.info(f"Don't know: {dont_know} ({100*dont_know/len(results):.1f}%)")
    logger.info(f"Total time: {total_time:.1f}s")
    logger.info(f"Average time per question: {total_time/len(results):.2f}s")
    logger.info(f"Results saved to: {output_file}")
    logger.info("="*60)


if __name__ == "__main__":
    main()
