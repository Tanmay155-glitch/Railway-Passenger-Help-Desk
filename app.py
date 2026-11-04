#!/usr/bin/env python3
"""
Railway Help Desk - Web Application
A simple web interface for the Railway Passenger Help Desk system.
"""

from flask import Flask, render_template, request, jsonify
from helpdesk.pipeline import ask
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Handle question submission and return answer.
    
    Expected JSON input:
    {
        "question": "What is Rule 25?"
    }
    
    Returns JSON:
    {
        "success": true,
        "data": {
            "answer": "...",
            "sources": [...],
            "sql": "..." or null,
            "dont_know": false
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': 'No question provided'
            }), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question cannot be empty'
            }), 400
        
        logger.info(f"Processing question: {question}")
        
        # Get answer from the system
        result = ask(question)
        
        logger.info(f"Answer generated successfully")
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Railway Help Desk'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Railway Help Desk - Web Interface")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
