# Railway Help Desk - Web UI Guide

This document explains how to use and deploy the web interface for the Railway Help Desk system.

## Design Theme

The web interface features a **Royal Purple & Gold** color scheme:
- Deep purple gradient background (#1a0033 → #4a0080) for royal elegance
- Gold accents (#ffd700) for headings, borders, and highlights
- White content boxes with purple borders for clarity
- Georgia serif font for a classic, professional appearance
- Simple, clean layout focused on usability

---

## Features

- **Royal theme design** - Elegant purple and gold color scheme
- **Simple & clean layout** - Minimalist interface focused on usability
- **Responsive design** - Works seamlessly on desktop, tablet, and mobile
- **Example questions** - Click to auto-fill the input field
- **Real-time results** - Displays answer, sources, and SQL query
- **Loading indicator** - Visual feedback while processing
- **Error handling** - User-friendly error messages
- **Smooth animations** - Fade-in effects for result display
- **Accessibility** - High contrast, readable fonts

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure Flask is installed:
```bash
pip install Flask==3.0.0
```

### 2. Start the Server

```bash
python app.py
```

You'll see:
```
============================================================
Railway Help Desk - Web Interface
============================================================
Starting server...
Open your browser and go to: http://localhost:5000
Press CTRL+C to stop the server
============================================================
```

### 3. Access the Web UI

Open your browser and navigate to:
- **Local access:** http://localhost:5000
- **Alternative:** http://127.0.0.1:5000
- **Network access:** http://[your-ip]:5000 (accessible from other devices on your network)

---

## How to Use

### Asking Questions

1. **Type your question** in the input box
2. **Press Enter** or click the **"ASK QUESTION"** button
3. **Wait** for the loading indicator (spinner with "Processing your question...")
4. **View the results:**
   - Answer text
   - Status badge (✅ ANSWERED or ⚠️ I DON'T KNOW)
   - Sources (if available) - Document name and page number
   - SQL Query (if database was queried)

### Example Questions

Click any of these pre-filled examples to try the system:
- "What is Rule 25?"
- "AC First Class cancellation"
- "Delhi to Mumbai trains"
- "Train 12430 info"

---

## API Endpoints

### `GET /`
Returns the main HTML page (web interface).

### `POST /ask`
Submit a question and get an answer.

**Request:**
```json
{
  "question": "What is the cancellation charge for Tatkal tickets?"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": "According to the refund rules...",
    "sources": [
      {"doc": "irctc_refund_rules_jan2026.pdf", "page": 2}
    ],
    "sql": null,
    "dont_know": false
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No question provided"
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Railway Help Desk"
}
```

---

## UI Components

### Color Scheme

| Element | Color | Hex Code |
|---------|-------|----------|
| Background | Deep Purple Gradient | #1a0033 → #4a0080 |
| Heading | Gold | #ffd700 |
| Content Boxes | White | #ffffff (95% opacity) |
| Primary Border | Gold | #ffd700 |
| Purple Accent | Royal Purple | #6a1b9a |
| Button | Purple Gradient | #6a1b9a → #4a148c |
| Button Text | Gold | #ffd700 |
| SQL Code Background | Dark Purple | #2d1b4e |
| SQL Code Text | Gold | #ffd700 |

### Layout Structure

```
┌─────────────────────────────────────────┐
│           RAILWAY HELP DESK             │ ← Gold heading
│    Ask about Indian Railways rules...    │ ← Light purple subtitle
├─────────────────────────────────────────┤
│                                         │
│  [Type your question here...        ]  │ ← White input box
│                                         │
│  [      ASK QUESTION (button)      ]  │ ← Purple/gold button
│                                         │
│  Example Questions:                     │
│  [What is Rule 25?] [AC First Class...] │ ← Clickable examples
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  📝 Answer                              │
│  [Answer text appears here]            │
│  ✅ ANSWERED / ⚠️ I DON'T KNOW        │
│                                         │
│  📚 Sources                             │
│  📄 document.pdf (Page 2)              │
│                                         │
│  🔍 SQL Query                           │
│  SELECT * FROM trains...               │
│                                         │
└─────────────────────────────────────────┘
```

---

## Technology Stack

- **Backend:** Flask 3.0.0 (Python web framework)
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (no dependencies)
- **Styling:** Custom CSS with:
  - CSS Grid and Flexbox for layout
  - CSS animations for smooth transitions
  - Media queries for responsive design
- **Font:** Georgia (serif) for elegance
- **Icons:** Emoji icons (📝, 📚, 🔍, 🚂, etc.)

---

## Browser Compatibility

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## Troubleshooting

### Server Won't Start

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install Flask==3.0.0
```

### Can't Access from Another Device

**Issue:** Network URL (http://192.168.1.x:5000) not accessible

**Solution:**
1. Check firewall settings (allow port 5000)
2. Ensure both devices are on the same network
3. Verify the server is running with `0.0.0.0` (it is by default in app.py)

### Loading Takes Too Long

**Possible causes:**
1. API key issue (check `.env` file for `GEMINI_API_KEY`)
2. Network latency to Gemini API
3. Large document corpus

**Check logs in terminal for errors**

### Results Not Displaying

**Check browser console** (F12 → Console tab) for JavaScript errors.

**Common fix:** Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)

---

## Deployment

### Local Development
```bash
python app.py
```
Runs on http://localhost:5000 with debug mode enabled.

### Production Deployment

⚠️ **Do NOT use Flask's built-in server in production!**

Use a production WSGI server like **Gunicorn**:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or use **Waitress** (Windows-compatible):
```bash
pip install waitress
waitress-serve --port=5000 app:app
```

### Cloud Deployment Options

1. **Heroku**
   - Add `Procfile`: `web: gunicorn app:app`
   - Deploy via git push

2. **AWS (Elastic Beanstalk)**
   - Zip your project
   - Upload to Elastic Beanstalk
   - Set environment variables

3. **Azure Web Apps**
   - Use Azure CLI or portal
   - Set Python runtime
   - Configure environment variables

4. **Google Cloud Run**
   - Create Dockerfile
   - Deploy with `gcloud run deploy`

### Environment Variables

Required in production:
```
GEMINI_API_KEY=your_api_key_here
FLASK_ENV=production
```

---

## Customization

### Changing Colors

Edit `templates/index.html`, find the `<style>` section:

```css
/* Background gradient */
background: linear-gradient(135deg, #1a0033 0%, #2d004d 50%, #4a0080 100%);

/* Gold color */
color: #ffd700;

/* Purple accent */
background: #6a1b9a;
```

### Changing Fonts

Replace `Georgia` with your preferred font:
```css
font-family: 'Your Font', serif;
```

### Adding More Examples

Edit the examples section in `templates/index.html`:
```html
<button class="example-btn" onclick="setQuestion('Your question here')">
    Button text
</button>
```

---

## Performance Optimization

### Tips for Faster Response Times

1. **Cache LLM responses** (already implemented in `helpdesk/llm.py`)
2. **Use embeddings** for better search (build with `build_index.py --embeddings`)
3. **Compress responses** (enable gzip in Flask)
4. **Use CDN** for static assets in production
5. **Optimize database queries** (indexes already present)

### Current Performance

- Document queries: 3-5 seconds
- Database queries: 2-4 seconds
- Refusals: 1-2 seconds

Bottleneck: LLM API calls (2-4 seconds)

---

## Security Considerations

### Already Implemented ✅

- ✅ SQL injection protection (5-layer guard)
- ✅ Read-only database access
- ✅ Input validation
- ✅ No sensitive data in responses
- ✅ Error messages don't leak system info

### Additional Recommendations for Production

1. **HTTPS** - Use SSL/TLS certificates
2. **Rate limiting** - Prevent abuse (use Flask-Limiter)
3. **CORS** - Configure properly if needed
4. **Authentication** - Add user login if required
5. **Logging** - Monitor for suspicious activity

---

## Support

For issues or questions:
1. Check the main README.md
2. Review COMPLETE_SYSTEM_TEST_REPORT.md
3. Check terminal logs for errors
4. Verify .env file configuration

---

## Screenshots Reference

### Main Interface
- Royal purple gradient background
- White question box with gold border
- Purple "ASK QUESTION" button with gold text
- Clean, simple layout

### Results Display
- White result box with gold border
- Purple section titles (📝 Answer, 📚 Sources, 🔍 SQL Query)
- Green badge for answered (✅ ANSWERED)
- Orange badge for don't know (⚠️ I DON'T KNOW)
- Light purple source items with purple left border
- Dark purple SQL code box with gold text

---

**Last Updated:** November 4, 2026  
**Version:** 2.0 (Royal Theme Update)  
**Status:** ✅ Production Ready
