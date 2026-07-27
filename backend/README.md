# Portfolio Manager Backend

Flask-based REST API for portfolio management.

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Configure environment variables in `.env`:
   - `FLASK_ENV`: Set to `development` or `production`
   - `API_PORT`: Port to run the API on (default: 5000)
   - `CORS_ORIGIN`: Frontend URL for CORS (default: http://localhost:3000)
   - `FIREBASE_CREDENTIALS_JSON`: Path to Firebase credentials JSON

## Running the API

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Available Endpoints

- `GET /health` - Health check
- `GET /api/portfolio` - Retrieve portfolio (not implemented)
- `GET /api/portfolio/items` - List portfolio items (not implemented)

## Project Structure

```
backend/
├── app.py                  # Flask application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── models/               # Data models
├── routes/               # API route handlers
├── services/             # Business logic services
├── utils/                # Utility functions
└── tests/                # Test files
```

## Next Steps

- Set up Firestore integration (Step 2)
- Implement portfolio and item models (Step 3)
- Create Firestore service layer (Step 4)
- Implement GET endpoints (Step 5)
