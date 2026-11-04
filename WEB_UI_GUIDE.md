# 🌐 Railway Help Desk - Web UI Guide

## Quick Start

### 1. Install Flask
```bash
pip install Flask==3.0.0
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the Web Server
```bash
python app.py
```

### 3. Open in Browser
Go to: **http://localhost:5000**

---

## Features

### 🎨 Beautiful Web Interface
- Modern, responsive design
- Works on desktop and mobile
- Gradient background with smooth animations

### 💬 Easy Question Input
- Large text input field
- Enter key support
- Example questions to try

### 📊 Comprehensive Results
- Clear answer display
- Source citations with document and page
- SQL query display (when applicable)
- Status indicators (✅ Answered / ⚠️ I don't know)

### 🚀 Fast & Reliable
- Real-time processing
- Loading indicator
- Error handling

---

## Usage

### Ask a Question
1. Type your question in the input box
2. Press **Enter** or click **Ask Question**
3. Wait for the answer (3-8 seconds)
4. View the answer with sources

### Try Example Questions
Click any of the example buttons:
- "What is Rule 25?"
- "Tatkal cancellation"
- "Delhi to Mumbai trains"
- "Advance reservation"

---

## API Endpoints

### POST /ask
Submit a question and get an answer.

**Request:**
```json
{
  "question": "What is Rule 25?"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": "Rule 25 specifies that...",
    "sources": [
      {"doc": "rb_cc08_2026_vande_bharat_sleeper_refund.pdf", "page": 5}
    ],
    "sql": null,
    "dont_know": false
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Railway Help Desk"
}
```

---

## Screenshots

### Main Interface
- Large question input
- Example questions
- Beautiful gradient design

### Answer Display
- Clear answer text
- Status badge (Answered / Don't know)
- Source citations
- SQL query (if applicable)

---

## Configuration

### Change Port
Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your port
```

### Production Mode
For production deployment:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

Or use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Change port in app.py
```

### Module Not Found
```bash
# Make sure you're in the project directory
cd rail_capstone_pack

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Slow Response Times
- First request may take 10-15 seconds (loading models)
- Subsequent requests should be faster (3-8 seconds)
- Check your internet connection (Gemini API)

---

## Integration with CLI

The web UI uses the same backend as the CLI:
- **CLI:** `python ask.py "question"`
- **Web:** http://localhost:5000

Both use `helpdesk.pipeline.ask()` function.

---

## Development

### File Structure
```
rail_capstone_pack/
├── app.py                  # Flask application
├── templates/
│   └── index.html         # Web UI template
├── helpdesk/              # Backend modules
│   └── pipeline.py        # ask() function
└── requirements.txt       # Dependencies (includes Flask)
```

### Extending the UI

**Add new features:**
1. Edit `templates/index.html` for frontend
2. Add routes in `app.py` for backend
3. Test with `python app.py`

**Example: Add history feature**
```python
@app.route('/history')
def history():
    # Return question history
    return jsonify({'history': []})
```

---

## Notes

- The web UI is optional - CLI still works independently
- Same accuracy and functionality as CLI
- Great for demos and presentations
- Can be deployed to cloud platforms (Heroku, AWS, etc.)

---

## Support

For issues:
1. Check terminal for error messages
2. Verify `.env` file has valid API key
3. Ensure all dependencies installed
4. Check index/ directory exists

---

**Enjoy using the Railway Help Desk Web UI!** 🚂✨
