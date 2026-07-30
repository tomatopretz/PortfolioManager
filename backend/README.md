# Portfolio Manager Backend

Flask-based REST API for portfolio management.

## Setup

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
brew install --cask google-cloud-sdk
brew install cloud-sql-proxy
gcloud auth login
gcloud auth application-default login
cp .env.example .env
```

Set `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@127.0.0.1:5433/portfoliomanager-bfaa2-database
```

Use the shared database username and password provided separately. Do not commit `.env`.

Start the Cloud SQL proxy in a separate terminal:

```bash
cloud-sql-proxy pretap-bfaa2:asia-southeast1:portfoliomanager-bfaa2-instance --port 5433
```

Run the backend:

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

- Set up Firebase SQL Connect/PostgreSQL integration (Step 2)
- Implement portfolio and item models (Step 3)
- Create database service layer (Step 4)
- Implement GET endpoints (Step 5)
