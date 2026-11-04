"""
Command-line interface for Railway Passenger Help Desk.
"""

import sys
import argparse
import json
import logging
from helpdesk.pipeline import ask
from helpdesk.config import validate_environment

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)


DEMO_QUESTIONS = [
    "What is the cancellation charge for a Tatkal ticket?",
    "Which trains go from Delhi to Mumbai?",
    "What is the advance reservation period?",
    "What is the refund policy for Vande Bharat Sleeper trains?",
    "How many stops does train 12002 make?"
]


def print_answer(result: dict, use_json: bool = False):
    """Print answer in human-readable or JSON format."""
    if use_json:
        print(json.dumps(result, indent=2))
        return
    
    # Human-readable format
    print("\n" + "="*60)
    print("ANSWER")
    print("="*60)
    print(result["answer"])
    
    # Sources
    if result["sources"]:
        print("\n" + "-"*60)
        print("SOURCES")
        print("-"*60)
        for source in result["sources"]:
            page_str = f", page {source['page']}" if source['page'] is not None else " (web page)"
            print(f"  • {source['doc']}{page_str}")
    
    # SQL
    if result["sql"]:
        print("\n" + "-"*60)
        print("SQL QUERY")
        print("-"*60)
        print(result["sql"])
    
    # Status
    print("\n" + "-"*60)
    has_sources = len(result["sources"]) > 0
    has_sql = result["sql"] is not None
    
    if result["dont_know"]:
        status = "I don't know"
    elif has_sources and has_sql:
        status = "answered from both documents and timetable"
    elif has_sources:
        status = "answered from documents"
    elif has_sql:
        status = "answered from timetable"
    else:
        status = "processing"
    
    print(f"Status: {status}")
    print("="*60 + "\n")


def interactive_mode():
    """Run in interactive mode with command prompt."""
    print("\n" + "="*60)
    print("Railway Passenger Help Desk - Interactive Mode")
    print("="*60)
    print("Type your question and press Enter.")
    print("Commands:")
    print("  :examples  - Show demo questions")
    print("  :exit      - Exit")
    print("  exit       - Exit")
    print("="*60 + "\n")
    
    while True:
        try:
            question = input("\n❓ Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', ':exit', 'quit', ':quit']:
                print("\nGoodbye!")
                break
            
            if question.lower() == ':examples':
                print("\nDemo Questions:")
                for i, q in enumerate(DEMO_QUESTIONS, 1):
                    print(f"  {i}. {q}")
                continue
            
            # Ask the question
            result = ask(question)
            print_answer(result)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Railway Passenger Help Desk - Ask questions about railway rules and timetables"
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to ask (if not provided, starts interactive mode)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information (route, chunks, scores, timings)"
    )
    
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate environment
    is_valid, errors = validate_environment()
    if not is_valid:
        print("Error: Environment not properly configured:", file=sys.stderr)
        for error in errors:
            print(f"  • {error}", file=sys.stderr)
        print("\nPlease fix these issues and try again.", file=sys.stderr)
        sys.exit(1)
    
    # Interactive mode if no question provided
    if not args.question:
        interactive_mode()
        return
    
    # Single question mode
    result = ask(args.question)
    print_answer(result, use_json=args.json)


if __name__ == "__main__":
    main()
